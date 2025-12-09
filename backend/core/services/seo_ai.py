from __future__ import annotations

import json
from typing import Dict, List

from ..models import AISEORecommendation, SEODataUpload, SEOKeyword, SEOKeywordCluster
from .ai_client import AIContentEngine

class SEOAutomationEngine:
    SYSTEM_PROMPT = (
        "You are an SEO and content strategy expert working for Codeteki. "
        "You analyse keyword data, identify themes, and recommend specific content actions."
    )

    def __init__(self, upload: SEODataUpload, ai_engine: AIContentEngine | None = None):
        self.upload = upload
        self.ai_engine = ai_engine or AIContentEngine()

    def generate(self, *, cluster_limit: int = 5) -> Dict[str, object]:
        if not self.upload.keywords.exists():
            raise ValueError("Upload must be processed before triggering AI automation.")

        created: List[AISEORecommendation] = []
        created.append(self._create_opportunity_overview())

        clusters = list(
            self.upload.clusters.order_by("-priority_score", "-avg_volume")[:cluster_limit]
        )
        for cluster in clusters:
            created.extend(self._create_cluster_recommendations(cluster))

        return {
            "recommendations": len([item for item in created if item]),
            "model": self.ai_engine.model,
            "ai_enabled": self.ai_engine.enabled,
        }

    def _create_opportunity_overview(self) -> AISEORecommendation | None:
        keywords = list(self.upload.keywords.order_by("-priority_score")[:10])
        if not keywords:
            return None
        keyword_payload = self._keyword_payload(keywords)
        cluster_snapshot = self.upload.insights.get("cluster_overview", {})
        prompt = (
            f"Project name: {self.upload.name}\n"
            f"Total keywords: {self.upload.insights.get('total_keywords')}\n"
            f"Average priority score: {self.upload.insights.get('avg_priority_score')}\n"
            f"Intent breakdown: {json.dumps(self.upload.insights.get('intent_breakdown', {}), ensure_ascii=False)}\n"
            f"Top keyword opportunities: {json.dumps(keyword_payload, ensure_ascii=False)}\n"
            f"Cluster snapshot: {json.dumps(cluster_snapshot, ensure_ascii=False)}\n"
            "Provide a concise summary covering:\n"
            "1. Immediate quick-win topics we should publish this week.\n"
            "2. Long-term pillar content themes that align with the data.\n"
            "3. Recommended conversion actions or lead magnets to pair with the content.\n"
            "Respond using markdown with section headings and bullet points."
        )
        return self._persist_recommendation(
            category=AISEORecommendation.CATEGORY_OPPORTUNITY,
            title="SEO Opportunity Summary",
            prompt=prompt,
            metadata={"top_keywords": keyword_payload, "clusters": cluster_snapshot},
        )

    def _create_cluster_recommendations(self, cluster: SEOKeywordCluster) -> List[AISEORecommendation]:
        keywords = list(cluster.keywords.order_by("-priority_score")[:5])
        if not keywords:
            return []
        keyword_payload = self._keyword_payload(keywords)
        base_prompt = (
            f"Cluster: {cluster.label}\n"
            f"Intent: {cluster.get_intent_display()}\n"
            f"Average volume: {cluster.avg_volume}\n"
            f"Avg difficulty: {cluster.avg_difficulty}\n"
            f"Keywords: {json.dumps(keyword_payload, ensure_ascii=False)}\n"
        )

        content_prompt = (
            base_prompt
            + "Draft a detailed content brief (title, hook, intro angle, H2/H3 outline, CTA ideas) "
            "for an article or landing page that would best capture this cluster. Keep the tone confident and helpful."
        )
        metadata_prompt = (
            base_prompt
            + """Generate a complete SEO metadata kit with the following format (use exactly these labels):

**Page Title:** [50-60 chars, include primary keyword, brand at end]
**Meta Description:** [150-155 chars, compelling with CTA]
**Meta Keywords:** [5-8 comma-separated keywords from the cluster data above]
**OG Title:** [Same as page title or slightly shorter for social]
**OG Description:** [Same as meta description or more engaging for social]
**URL Slug:** [lowercase-with-dashes]

**FAQ Schema Questions:**
1. [Question about this topic]
2. [Question about this topic]
3. [Question about this topic]

Use the actual keywords from the data provided - don't make up new ones."""
        )

        recommendations = [
            self._persist_recommendation(
                category=AISEORecommendation.CATEGORY_CLUSTER_BRIEF,
                title=f"Content Brief: {cluster.label}",
                prompt=content_prompt,
                metadata={"cluster_id": cluster.id, "keywords": keyword_payload},
                cluster=cluster,
                keyword=keywords[0],
            ),
            self._persist_recommendation(
                category=AISEORecommendation.CATEGORY_METADATA,
                title=f"Meta Kit: {cluster.label}",
                prompt=metadata_prompt,
                metadata={"cluster_id": cluster.id, "keywords": keyword_payload},
                cluster=cluster,
                keyword=keywords[0],
            ),
        ]

        faq_prompt = (
            base_prompt
            + "Provide five FAQ ideas (question + short answer) that align with this keyword intent."
        )
        recommendations.append(
            self._persist_recommendation(
                category=AISEORecommendation.CATEGORY_FAQ,
                title=f"FAQ Ideas: {cluster.label}",
                prompt=faq_prompt,
                metadata={"cluster_id": cluster.id, "keywords": keyword_payload},
                cluster=cluster,
            )
        )

        return [rec for rec in recommendations if rec]

    def _keyword_payload(self, keywords: List[SEOKeyword]) -> List[Dict[str, object]]:
        return [
            {
                "keyword": keyword.keyword,
                "volume": keyword.search_volume,
                "intent": keyword.intent,
                "priority_score": float(keyword.priority_score),
            }
            for keyword in keywords
        ]

    def _persist_recommendation(
        self,
        *,
        category: str,
        title: str,
        prompt: str,
        metadata: Dict[str, object] | None = None,
        cluster: SEOKeywordCluster | None = None,
        keyword: SEOKeyword | None = None,
    ) -> AISEORecommendation:
        result = self.ai_engine.generate(prompt=prompt, system_prompt=self.SYSTEM_PROMPT)
        usage = result.get("usage", {})
        status = (
            AISEORecommendation.STATUS_GENERATED if result.get("success") else AISEORecommendation.STATUS_ERROR
        )
        return AISEORecommendation.objects.create(
            upload=self.upload,
            cluster=cluster,
            keyword=keyword,
            category=category,
            title=title,
            prompt=prompt,
            response=result.get("output", ""),
            ai_model=result.get("model", self.ai_engine.model),
            prompt_tokens=usage.get("prompt_tokens", 0) or 0,
            completion_tokens=usage.get("completion_tokens", 0) or 0,
            metadata=metadata or {},
            status=status,
            error_message=result.get("error", ""),
        )
