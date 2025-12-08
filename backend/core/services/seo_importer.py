from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import TextIOWrapper
from typing import Dict, Iterable, List, Any
from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

from ..models import (
    SEODataUpload,
    SEOKeyword,
    SEOKeywordCluster,
    SEOProject,
    SEOCompetitor,
    SEOCompetitorKeyword,
    SEOBacklinkOpportunity,
    SEOKeywordRank,
    SEOContentGap,
)


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


# =============================================================================
# UBERSUGGEST COMPETITOR IMPORTER
# =============================================================================

class CompetitorCSVParser:
    """Parses Ubersuggest competitor list exports."""

    HEADER_LOOKUP = {
        "domain": "domain",
        "competitor": "domain",
        "website": "domain",
        "url": "domain",
        "domain_score": "domain_score",
        "authority": "domain_score",
        "da": "domain_score",
        "organic_keywords": "organic_keywords",
        "keywords": "organic_keywords",
        "monthly_traffic": "monthly_traffic",
        "traffic": "monthly_traffic",
        "organic_traffic": "monthly_traffic",
        "backlinks": "backlinks",
        "referring_domains": "referring_domains",
        "ref_domains": "referring_domains",
    }

    def __init__(self, upload: SEODataUpload, *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        rows = []
        with self.upload.csv_file.open("rb") as handle:
            text_stream = TextIOWrapper(handle, encoding=self.encoding, newline="")
            reader = csv.DictReader(text_stream)
            if not reader.fieldnames:
                return rows
            header_map = self._build_header_map(reader.fieldnames)
            for raw_row in reader:
                normalized = self._normalize_row(raw_row, header_map)
                domain = normalized.get("domain")
                if not domain:
                    continue
                # Clean domain
                domain = self._clean_domain(domain)
                rows.append({
                    "domain": domain,
                    "domain_score": self._to_int(normalized.get("domain_score")),
                    "organic_keywords": self._to_int(normalized.get("organic_keywords")),
                    "monthly_traffic": self._to_int(normalized.get("monthly_traffic")),
                    "backlinks": self._to_int(normalized.get("backlinks")),
                    "referring_domains": self._to_int(normalized.get("referring_domains")),
                })
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = self._normalize_key(header)
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if canonical:
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
        return int(digits) if digits else 0

    @staticmethod
    def _clean_domain(domain: str) -> str:
        domain = domain.strip().lower()
        if domain.startswith(("http://", "https://")):
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
        domain = domain.replace("www.", "")
        return domain.rstrip("/")


class CompetitorIngestService:
    """Imports competitor data from Ubersuggest exports."""

    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, Any]:
        if not self.upload.project:
            raise ValueError("Upload must be linked to a project to import competitors.")

        parser = CompetitorCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No competitor data found in the CSV file.")

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for row in rows:
                competitor, created = SEOCompetitor.objects.update_or_create(
                    project=self.upload.project,
                    domain=row["domain"],
                    defaults={
                        "domain_score": row["domain_score"] or None,
                        "organic_keywords": row["organic_keywords"] or None,
                        "monthly_traffic": row["monthly_traffic"] or None,
                        "backlinks_count": row["backlinks"] or None,
                        "metrics_updated_at": timezone.now(),
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        return {
            "rows": len(rows),
            "created": created_count,
            "updated": updated_count,
            "insights": {
                "total_competitors": len(rows),
                "avg_domain_score": sum(r["domain_score"] for r in rows) // len(rows) if rows else 0,
            }
        }


# =============================================================================
# UBERSUGGEST COMPETITOR KEYWORDS IMPORTER
# =============================================================================

class CompetitorKeywordCSVParser:
    """Parses Ubersuggest competitor keywords exports."""

    HEADER_LOOKUP = {
        "keyword": "keyword",
        "keywords": "keyword",
        "position": "position",
        "rank": "position",
        "ranking": "position",
        "search_volume": "search_volume",
        "volume": "search_volume",
        "url": "url",
        "landing_page": "url",
        "traffic": "traffic",
        "estimated_traffic": "traffic",
        "cpc": "cpc",
        "difficulty": "difficulty",
        "sd": "difficulty",
    }

    def __init__(self, upload: SEODataUpload, competitor_domain: str = "", *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.competitor_domain = competitor_domain
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        rows = []
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
                rows.append({
                    "keyword": keyword,
                    "position": self._to_int(normalized.get("position")),
                    "search_volume": self._to_int(normalized.get("search_volume")),
                    "url": normalized.get("url", ""),
                    "traffic": self._to_int(normalized.get("traffic")),
                    "cpc": self._to_decimal(normalized.get("cpc")),
                    "difficulty": self._to_int(normalized.get("difficulty")),
                })
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if canonical:
                normalized[canonical] = (value or "").strip()
        return normalized

    @staticmethod
    def _to_int(value: str | None) -> int:
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else 0

    @staticmethod
    def _to_decimal(value: str | None) -> Decimal | None:
        if not value:
            return None
        cleaned = re.sub(r"[^0-9.]", "", value)
        if not cleaned:
            return None
        try:
            return Decimal(cleaned).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return None


class CompetitorKeywordIngestService:
    """Imports competitor keyword data and identifies content gaps."""

    def __init__(self, upload: SEODataUpload, competitor: SEOCompetitor | None = None):
        self.upload = upload
        self.competitor = competitor

    def run(self) -> Dict[str, Any]:
        if not self.upload.project:
            raise ValueError("Upload must be linked to a project.")

        parser = CompetitorKeywordCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No keyword data found in the CSV file.")

        # Get or create competitor if not provided
        competitor = self.competitor
        if not competitor:
            # Try to find from notes or create generic one
            competitor, _ = SEOCompetitor.objects.get_or_create(
                project=self.upload.project,
                domain="unknown_competitor",
                defaults={"notes": f"Auto-created from upload: {self.upload.name}"}
            )

        created_count = 0
        content_gaps = 0

        with transaction.atomic():
            # Clear existing keywords for this competitor
            competitor.keywords.all().delete()

            keyword_objects = []
            for row in rows:
                # Calculate opportunity score
                volume = row["search_volume"] or 0
                position = row["position"] or 100
                difficulty = row["difficulty"] or 50

                # Higher score = better opportunity (high volume, low difficulty, weak competitor position)
                opportunity = Decimal(0)
                if volume > 0:
                    volume_factor = min(volume / 10000, 1.0)
                    difficulty_factor = (100 - difficulty) / 100
                    position_factor = min(position / 50, 1.0)  # Higher position = weaker, better for us
                    opportunity = Decimal(str(
                        volume_factor * 0.4 + difficulty_factor * 0.3 + position_factor * 0.3
                    )).quantize(Decimal("0.01"))

                # Check if this is a content gap (competitor ranks, we don't)
                is_gap = position <= 20 and volume >= 100

                keyword_objects.append(SEOCompetitorKeyword(
                    competitor=competitor,
                    keyword=row["keyword"],
                    position=row["position"] or None,
                    search_volume=volume,
                    traffic=row["traffic"] or None,
                    seo_difficulty=row["difficulty"] or None,
                    cpc=row.get("cpc"),
                    is_content_gap=is_gap,
                    opportunity_score=opportunity,
                ))

                if is_gap:
                    content_gaps += 1

            SEOCompetitorKeyword.objects.bulk_create(keyword_objects, batch_size=500)
            created_count = len(keyword_objects)

        return {
            "rows": created_count,
            "content_gaps": content_gaps,
            "insights": {
                "total_keywords": created_count,
                "content_gap_opportunities": content_gaps,
                "avg_position": sum(r["position"] for r in rows if r["position"]) // len([r for r in rows if r["position"]]) if any(r["position"] for r in rows) else 0,
            }
        }


# =============================================================================
# UBERSUGGEST BACKLINKS IMPORTER
# =============================================================================

class BacklinkCSVParser:
    """Parses Ubersuggest backlink exports."""

    HEADER_LOOKUP = {
        "source_url": "source_url",
        "source": "source_url",
        "from_url": "source_url",
        "referring_url": "source_url",
        "target_url": "target_url",
        "target": "target_url",
        "to_url": "target_url",
        "anchor_text": "anchor_text",
        "anchor": "anchor_text",
        "domain_score": "domain_score",
        "authority": "domain_score",
        "da": "domain_score",
        "page_score": "page_score",
        "pa": "page_score",
        "link_type": "link_type",
        "type": "link_type",
        "first_seen": "first_seen",
        "last_seen": "last_seen",
    }

    def __init__(self, upload: SEODataUpload, *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        rows = []
        with self.upload.csv_file.open("rb") as handle:
            text_stream = TextIOWrapper(handle, encoding=self.encoding, newline="")
            reader = csv.DictReader(text_stream)
            if not reader.fieldnames:
                return rows
            header_map = self._build_header_map(reader.fieldnames)
            for raw_row in reader:
                normalized = self._normalize_row(raw_row, header_map)
                source_url = normalized.get("source_url")
                if not source_url:
                    continue
                rows.append({
                    "source_url": source_url,
                    "source_domain": self._extract_domain(source_url),
                    "target_url": normalized.get("target_url", ""),
                    "anchor_text": normalized.get("anchor_text", ""),
                    "domain_score": self._to_int(normalized.get("domain_score")),
                    "page_score": self._to_int(normalized.get("page_score")),
                    "link_type": normalized.get("link_type", "dofollow").lower(),
                })
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if canonical:
                normalized[canonical] = (value or "").strip()
        return normalized

    @staticmethod
    def _to_int(value: str | None) -> int:
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else 0

    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            parsed = urlparse(url if url.startswith("http") else f"https://{url}")
            domain = parsed.netloc or parsed.path.split("/")[0]
            return domain.replace("www.", "").lower()
        except Exception:
            return url.lower()


class BacklinkIngestService:
    """Imports backlink data as opportunities."""

    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, Any]:
        if not self.upload.project:
            raise ValueError("Upload must be linked to a project.")

        parser = BacklinkCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No backlink data found in the CSV file.")

        created_count = 0
        high_quality_count = 0

        with transaction.atomic():
            for row in rows:
                da = row["domain_score"] or 0
                if da >= 50:
                    high_quality_count += 1

                # Calculate priority score based on DA
                priority = Decimal(str(min(da, 100) / 100)).quantize(Decimal("0.01"))

                opportunity, created = SEOBacklinkOpportunity.objects.update_or_create(
                    project=self.upload.project,
                    source_domain=row["source_domain"],
                    defaults={
                        "source_url": row["source_url"][:500] if row["source_url"] else "",
                        "source_title": row.get("anchor_text", "")[:300] if row.get("anchor_text") else "",
                        "domain_authority": da or None,
                        "page_authority": row.get("page_score") or None,
                        "opportunity_type": SEOBacklinkOpportunity.TYPE_COMPETITOR,
                        "priority_score": priority,
                    }
                )
                if created:
                    created_count += 1

        return {
            "rows": len(rows),
            "created": created_count,
            "high_quality": high_quality_count,
            "insights": {
                "total_backlinks": len(rows),
                "high_quality_links": high_quality_count,
                "avg_domain_authority": sum(r["domain_score"] for r in rows) // len(rows) if rows else 0,
            }
        }


# =============================================================================
# UBERSUGGEST RANKINGS IMPORTER
# =============================================================================

class RankingsCSVParser:
    """Parses Ubersuggest rank tracking exports."""

    HEADER_LOOKUP = {
        "keyword": "keyword",
        "keywords": "keyword",
        "position": "position",
        "rank": "position",
        "ranking": "position",
        "previous_position": "previous_position",
        "prev_position": "previous_position",
        "change": "change",
        "search_volume": "search_volume",
        "volume": "search_volume",
        "url": "url",
        "landing_page": "url",
        "date": "date",
        "tracked_date": "date",
    }

    def __init__(self, upload: SEODataUpload, *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        rows = []
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
                position = self._to_int(normalized.get("position"))
                prev_position = self._to_int(normalized.get("previous_position"))
                change = position - prev_position if prev_position else 0
                rows.append({
                    "keyword": keyword,
                    "position": position,
                    "previous_position": prev_position or None,
                    "change": change,
                    "search_volume": self._to_int(normalized.get("search_volume")),
                    "url": normalized.get("url", ""),
                })
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if canonical:
                normalized[canonical] = (value or "").strip()
        return normalized

    @staticmethod
    def _to_int(value: str | None) -> int:
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else 0


class RankingsIngestService:
    """Imports rank tracking data."""

    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, Any]:
        if not self.upload.project:
            raise ValueError("Upload must be linked to a project.")

        parser = RankingsCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No ranking data found in the CSV file.")

        created_count = 0
        improved_count = 0
        declined_count = 0

        with transaction.atomic():
            for row in rows:
                # Calculate position change (positive = improvement, negative = decline)
                change = row["change"]
                # If change is negative in CSV (they moved up), we want positive
                # If change is positive in CSV (they moved down), we want negative
                position_change = -change if change != 0 else 0

                rank = SEOKeywordRank.objects.create(
                    project=self.upload.project,
                    keyword=row["keyword"],
                    date=timezone.now().date(),
                    position=row["position"] or None,
                    previous_position=row["previous_position"],
                    ranking_url=row["url"][:500] if row["url"] else "",
                    search_volume=row["search_volume"],
                    position_change=position_change,
                )
                created_count += 1
                if position_change > 0:  # Positive = improved (moved up)
                    improved_count += 1
                elif position_change < 0:
                    declined_count += 1

        return {
            "rows": created_count,
            "improved": improved_count,
            "declined": declined_count,
            "insights": {
                "total_keywords": created_count,
                "improved_rankings": improved_count,
                "declined_rankings": declined_count,
                "avg_position": sum(r["position"] for r in rows if r["position"]) // len([r for r in rows if r["position"]]) if any(r["position"] for r in rows) else 0,
            }
        }


# =============================================================================
# CONTENT GAP IMPORTER
# =============================================================================

class ContentGapCSVParser:
    """Parses Ubersuggest keyword gap analysis exports."""

    HEADER_LOOKUP = {
        "keyword": "keyword",
        "keywords": "keyword",
        "your_position": "your_position",
        "our_position": "your_position",
        "competitor_position": "competitor_position",
        "comp_position": "competitor_position",
        "search_volume": "search_volume",
        "volume": "search_volume",
        "difficulty": "difficulty",
        "sd": "difficulty",
        "cpc": "cpc",
        "competitor": "competitor_domain",
        "competitor_domain": "competitor_domain",
    }

    def __init__(self, upload: SEODataUpload, *, encoding: str = "utf-8-sig"):
        self.upload = upload
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        rows = []
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
                your_pos = self._to_int(normalized.get("your_position"))
                comp_pos = self._to_int(normalized.get("competitor_position"))
                rows.append({
                    "keyword": keyword,
                    "your_position": your_pos or None,
                    "competitor_position": comp_pos or None,
                    "search_volume": self._to_int(normalized.get("search_volume")),
                    "difficulty": self._to_int(normalized.get("difficulty")),
                    "cpc": self._to_decimal(normalized.get("cpc")),
                    "competitor_domain": normalized.get("competitor_domain", ""),
                })
        return rows

    def _build_header_map(self, headers: Iterable[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")
            mapping[header] = self.HEADER_LOOKUP.get(normalized, normalized)
        return mapping

    def _normalize_row(self, row: Dict[str, str], header_map: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for original_key, value in row.items():
            canonical = header_map.get(original_key)
            if canonical:
                normalized[canonical] = (value or "").strip()
        return normalized

    @staticmethod
    def _to_int(value: str | None) -> int:
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else 0

    @staticmethod
    def _to_decimal(value: str | None) -> Decimal | None:
        if not value:
            return None
        cleaned = re.sub(r"[^0-9.]", "", value)
        if not cleaned:
            return None
        try:
            return Decimal(cleaned).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            return None


class ContentGapIngestService:
    """Imports content gap analysis data."""

    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, Any]:
        if not self.upload.project:
            raise ValueError("Upload must be linked to a project.")

        parser = ContentGapCSVParser(self.upload)
        rows = parser.parse()
        if not rows:
            raise ValueError("No content gap data found in the CSV file.")

        created_count = 0
        high_priority_count = 0

        with transaction.atomic():
            # Clear existing gaps for this project
            SEOContentGap.objects.filter(project=self.upload.project).delete()

            for row in rows:
                volume = row["search_volume"] or 0
                difficulty = row["difficulty"] or 50
                comp_pos = row["competitor_position"] or 100
                comp_domain = row["competitor_domain"] or ""

                # Calculate opportunity score
                # Higher score for: high volume, low difficulty, competitor ranks well
                volume_factor = min(volume / 10000, 1.0)
                difficulty_factor = (100 - difficulty) / 100
                comp_factor = (50 - min(comp_pos, 50)) / 50  # Better if competitor in top 50

                opportunity = Decimal(str(
                    volume_factor * 0.4 + difficulty_factor * 0.3 + comp_factor * 0.3
                )).quantize(Decimal("0.01"))

                # Determine priority
                priority = "low"
                if opportunity >= Decimal("0.6"):
                    priority = "high"
                    high_priority_count += 1
                elif opportunity >= Decimal("0.4"):
                    priority = "medium"

                # Build competitors ranking list
                competitors_list = []
                if comp_domain and comp_pos:
                    competitors_list.append({"competitor": comp_domain, "position": comp_pos})

                SEOContentGap.objects.create(
                    project=self.upload.project,
                    keyword=row["keyword"],
                    search_volume=volume,
                    seo_difficulty=difficulty or None,
                    cpc=row.get("cpc"),
                    competitors_ranking=competitors_list,
                    best_competitor_position=comp_pos if comp_pos else None,
                    opportunity_score=opportunity,
                    priority=priority,
                )
                created_count += 1

        return {
            "rows": created_count,
            "high_priority": high_priority_count,
            "insights": {
                "total_gaps": created_count,
                "high_priority_opportunities": high_priority_count,
                "avg_search_volume": sum(r["search_volume"] for r in rows) // len(rows) if rows else 0,
            }
        }


# =============================================================================
# MASTER IMPORT ROUTER
# =============================================================================

class UbersuggestImportRouter:
    """Routes import to the appropriate service based on upload source type."""

    def __init__(self, upload: SEODataUpload):
        self.upload = upload

    def run(self) -> Dict[str, Any]:
        source = self.upload.source

        # Mark as processing
        self.upload.status = SEODataUpload.STATUS_PROCESSING
        self.upload.save(update_fields=["status", "updated_at"])

        try:
            if source == SEODataUpload.SOURCE_UBERSUGGEST_KEYWORDS:
                result = SEOIngestService(self.upload).run()
            elif source == SEODataUpload.SOURCE_UBERSUGGEST_COMPETITORS:
                result = CompetitorIngestService(self.upload).run()
            elif source == SEODataUpload.SOURCE_UBERSUGGEST_COMPETITOR_KEYWORDS:
                result = CompetitorKeywordIngestService(self.upload).run()
            elif source == SEODataUpload.SOURCE_UBERSUGGEST_BACKLINKS:
                result = BacklinkIngestService(self.upload).run()
            elif source == SEODataUpload.SOURCE_UBERSUGGEST_RANKINGS:
                result = RankingsIngestService(self.upload).run()
            elif source == SEODataUpload.SOURCE_UBERSUGGEST_KEYWORD_GAPS:
                result = ContentGapIngestService(self.upload).run()
            elif source in (
                SEODataUpload.SOURCE_UBERSUGGEST_TOP_PAGES,
                SEODataUpload.SOURCE_UBERSUGGEST_CONTENT_IDEAS,
                SEODataUpload.SOURCE_UBERSUGGEST_SITE_AUDIT,
            ):
                # These can use the keyword parser with custom handling
                result = SEOIngestService(self.upload).run()
            else:
                raise ValueError(f"Unknown source type: {source}")

            # Update upload record
            self.upload.status = SEODataUpload.STATUS_PROCESSED
            self.upload.processed_at = timezone.now()
            self.upload.row_count = result.get("rows", 0)
            self.upload.insights = result.get("insights", {})
            self.upload.save(update_fields=[
                "status", "processed_at", "row_count", "insights", "updated_at"
            ])

            return result

        except Exception as e:
            self.upload.status = SEODataUpload.STATUS_FAILED
            self.upload.insights = {"error": str(e)}
            self.upload.save(update_fields=["status", "insights", "updated_at"])
            raise
