from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import TextIOWrapper
from typing import Dict, Iterable, List

from django.db import transaction

from ..models import SEODataUpload, SEOKeyword, SEOKeywordCluster


@dataclass
class KeywordRow:
    keyword: str
    search_volume: int = 0
    seo_difficulty: int | None = None
    paid_difficulty: int | None = None
    cpc: Decimal | None = None
    ranking_url: str = ""
    trend: str = ""
    metadata: Dict[str, str] | None = None


class UbersuggestCSVParser:
    """Normalises common Ubersuggest CSV exports into KeywordRow objects."""

    HEADER_LOOKUP = {
        "keyword": "keyword",
        "keywords": "keyword",
        "search_volume": "search_volume",
        "search_volume_": "search_volume",
        "searches": "search_volume",
        "volume": "search_volume",
        "seo_difficulty": "seo_difficulty",
        "sd": "seo_difficulty",
        "paid_difficulty": "paid_difficulty",
        "pd": "paid_difficulty",
        "cpc": "cpc",
        "cost_per_click": "cpc",
        "url": "ranking_url",
        "landing_page": "ranking_url",
        "trend": "trend",
    }

    def __init__(self, upload: SEODataUpload, *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.encoding = encoding

    def parse(self) -> List[KeywordRow]:
        rows: List[KeywordRow] = []
        with self.upload.csv_file.open("rb") as handle:
            text_stream = TextIOWrapper(handle, encoding=self.encoding, newline="")
            reader = csv.DictReader(text_stream)
            if not reader.fieldnames:
                return rows
            header_map = self._build_header_map(reader.fieldnames)
            for raw_row in reader:
                normalized = self._normalize_row(raw_row, header_map)
                keyword = normalized.get("keyword")
                if not keyword:
                    continue
                row = KeywordRow(
                    keyword=keyword,
                    search_volume=self._to_int(normalized.get("search_volume")),
                    seo_difficulty=self._to_int(normalized.get("seo_difficulty")),
                    paid_difficulty=self._to_int(normalized.get("paid_difficulty")),
                    cpc=self._to_decimal(normalized.get("cpc")),
                    ranking_url=normalized.get("ranking_url", ""),
                    trend=normalized.get("trend", ""),
                    metadata={
                        key: value
                        for key, value in normalized.items()
                        if key not in {"keyword", "search_volume", "seo_difficulty", "paid_difficulty", "cpc", "ranking_url", "trend"}
                        and value
                    },
                )
                rows.append(row)
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for header in headers:
            normalized = self._normalize_key(header)
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized: Dict[str, str] = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if not canonical:
                continue
            normalized[canonical] = (value or "").strip()
        return normalized

    @staticmethod
    def _normalize_key(header: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")

    @staticmethod
    def _to_int(value: str | None) -> int:
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        if not digits:
            return 0
        return int(digits)

    @staticmethod
    def _to_decimal(value: str | None) -> Decimal | None:
        if not value:
            return None
        cleaned = re.sub(r"[^0-9.]", "", value)
        if not cleaned:
            return None
        try:
            amount = Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class KeywordIntentDetector:
    TRANSACTIONAL_TERMS = (
        "buy",
        "price",
        "quote",
        "service",
        "hire",
        "agency",
        "consultant",
        "cost",
        "near me",
        "book",
    )
    COMMERCIAL_TERMS = (
        "best",
        "review",
        "top",
        "compare",
        "vs",
        "tools",
        "software",
        "platform",
    )
    NAV_TERMS = (
        "login",
        "portal",
        "dashboard",
        "account",
        "app",
    )

    def detect(self, keyword: str, metadata: Dict[str, str] | None = None) -> str:
        text = keyword.lower()
        if any(term in text for term in self.TRANSACTIONAL_TERMS):
            return SEOKeyword.INTENT_TRANSACTIONAL
        if any(term in text for term in self.COMMERCIAL_TERMS):
            return SEOKeyword.INTENT_COMMERCIAL
        if any(term in text for term in self.NAV_TERMS):
            return SEOKeyword.INTENT_NAVIGATIONAL
        if metadata:
            meta_intent = metadata.get("intent", "").lower()
            if meta_intent in {
                "transactional",
                "commercial",
                "navigational",
                "informational",
            }:
                return meta_intent
        return SEOKeyword.INTENT_INFORMATIONAL


class KeywordOpportunityScorer:
    """Derives a normalised opportunity score for each keyword."""

    def __init__(self, rows: List[KeywordRow]):
        self.max_volume = max((row.search_volume for row in rows), default=0) or 1

    def score(self, row: KeywordRow, intent: str) -> Decimal:
        volume_score = Decimal(row.search_volume) / Decimal(self.max_volume)
        difficulty = Decimal(100 - (row.seo_difficulty or 0)) / Decimal(100)
        paid = Decimal(100 - (row.paid_difficulty or 0)) / Decimal(100)
        cpc_component = (row.cpc or Decimal("0.00")) / Decimal("10.0")
        intent_boost = Decimal("1.00")
        if intent in (SEOKeyword.INTENT_TRANSACTIONAL, SEOKeyword.INTENT_COMMERCIAL):
            intent_boost = Decimal("1.10")
        score = (
            volume_score * Decimal("0.5")
            + difficulty * Decimal("0.3")
            + paid * Decimal("0.1")
            + cpc_component * Decimal("0.1")
        ) * intent_boost
        return score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class KeywordClusterBuilder:
    def __init__(self, upload: SEODataUpload, keywords: List[SEOKeyword]):
        self.upload = upload
        self.keywords = keywords

    def build(self) -> Dict[str, object]:
        SEOKeywordCluster.objects.filter(upload=self.upload).delete()
        clusters: Dict[str, List[SEOKeyword]] = {}
        for keyword in self.keywords:
            label = self._cluster_label(keyword.keyword)
            clusters.setdefault(label, []).append(keyword)

        created_clusters: List[SEOKeywordCluster] = []
        for label, items in clusters.items():
            metrics = self._cluster_metrics(items)
            cluster = SEOKeywordCluster.objects.create(
                upload=self.upload,
                label=label,
                seed_keyword=items[0].keyword if items else label,
                intent=metrics["intent"],
                avg_volume=metrics["avg_volume"],
                avg_difficulty=metrics["avg_difficulty"],
                keyword_count=len(items),
                priority_score=metrics["priority_score"],
                summary=metrics["summary"],
            )
            created_clusters.append(cluster)
            for keyword in items:
                keyword.cluster = cluster
        if self.keywords:
            SEOKeyword.objects.bulk_update(self.keywords, ["cluster"])

        sorted_clusters = sorted(
            created_clusters,
            key=lambda cluster: (cluster.priority_score, cluster.avg_volume),
            reverse=True,
        )
        return {
            "cluster_count": len(created_clusters),
            "top_clusters": [
                {
                    "label": cluster.label,
                    "intent": cluster.intent,
                    "avg_volume": cluster.avg_volume,
                    "keyword_count": cluster.keyword_count,
                    "priority_score": float(cluster.priority_score),
                }
                for cluster in sorted_clusters[:5]
            ],
        }

    def _cluster_label(self, keyword: str) -> str:
        tokens = re.findall(r"[a-z0-9]+", keyword.lower())
        if not tokens:
            return keyword.lower()
        if "near" in tokens and "me" in tokens:
            return " ".join(tokens[: tokens.index("near")] + ["near me"])
        return " ".join(tokens[:3])

    def _cluster_metrics(self, keywords: List[SEOKeyword]) -> Dict[str, object]:
        count = len(keywords) or 1
        avg_volume = sum(keyword.search_volume for keyword in keywords) // count
        difficulties = [
            keyword.seo_difficulty for keyword in keywords if keyword.seo_difficulty
        ]
        avg_difficulty = int(sum(difficulties) / len(difficulties)) if difficulties else 0
        intents = [keyword.intent for keyword in keywords]
        dominant_intent = max(set(intents), key=intents.count)
        avg_priority = (
            sum(keyword.priority_score for keyword in keywords) / Decimal(count)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        summary = ", ".join(keyword.keyword for keyword in keywords[:3])
        return {
            "avg_volume": avg_volume,
            "avg_difficulty": avg_difficulty,
            "intent": dominant_intent,
            "priority_score": avg_priority,
            "summary": summary,
        }


class SEOInsightsBuilder:
    def __init__(self, upload: SEODataUpload, keywords: List[SEOKeyword], cluster_data: Dict[str, object] | None):
        self.upload = upload
        self.keywords = keywords
        self.cluster_data = cluster_data or {}

    def build(self) -> Dict[str, object]:
        total_keywords = len(self.keywords)
        if not total_keywords:
            return {"total_keywords": 0, "intent_breakdown": {}}
        avg_volume = sum(keyword.search_volume for keyword in self.keywords) // total_keywords
        avg_priority = (
            sum(keyword.priority_score for keyword in self.keywords) / Decimal(total_keywords)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        intent_breakdown: Dict[str, int] = {}
        for keyword in self.keywords:
            intent_breakdown[keyword.intent] = intent_breakdown.get(keyword.intent, 0) + 1

        top_keywords = sorted(
            self.keywords,
            key=lambda keyword: (keyword.priority_score, keyword.search_volume),
            reverse=True,
        )[:10]
        return {
            "total_keywords": total_keywords,
            "avg_volume": avg_volume,
            "avg_priority_score": float(avg_priority),
            "intent_breakdown": intent_breakdown,
            "top_keywords": [
                {
                    "keyword": keyword.keyword,
                    "intent": keyword.intent,
                    "search_volume": keyword.search_volume,
                    "priority_score": float(keyword.priority_score),
                }
                for keyword in top_keywords
            ],
            "cluster_overview": self.cluster_data,
        }


class SEOIngestService:
    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, object]:
        parser = UbersuggestCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No keyword rows were found in the CSV file.")

        intents = KeywordIntentDetector()
        scorer = KeywordOpportunityScorer(rows)
        keyword_objects: List[SEOKeyword] = []

        with transaction.atomic():
            self.upload.keywords.all().delete()
            self.upload.clusters.all().delete()

            for row in rows:
                intent = intents.detect(row.keyword, row.metadata)
                keyword_objects.append(
                    SEOKeyword(
                        upload=self.upload,
                        keyword=row.keyword,
                        search_volume=row.search_volume,
                        seo_difficulty=row.seo_difficulty or 0,
                        paid_difficulty=row.paid_difficulty or 0,
                        cpc=row.cpc,
                        keyword_type=self._keyword_type(row.keyword),
                        intent=intent,
                        ranking_url=row.ranking_url,
                        trend=row.trend,
                        priority_score=scorer.score(row, intent),
                        metadata=row.metadata or {},
                    )
                )

            SEOKeyword.objects.bulk_create(keyword_objects, batch_size=500)
            keywords = list(self.upload.keywords.all())
            cluster_data = KeywordClusterBuilder(self.upload, keywords).build()
            insights = SEOInsightsBuilder(self.upload, keywords, cluster_data).build()

        return {"rows": len(keyword_objects), "insights": insights}

    @staticmethod
    def _keyword_type(keyword: str) -> str:
        word_count = len(re.findall(r"[a-z0-9]+", keyword.lower()))
        if word_count <= 2:
            return "short_tail"
        if word_count <= 4:
            return "mid_tail"
        return "long_tail"
