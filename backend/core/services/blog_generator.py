from __future__ import annotations

import json
from typing import Dict, List

from django.utils.text import Truncator, slugify

from ..models import BlogPost, SEODataUpload
from .ai_client import AIContentEngine


class BlogContentGenerator:
    """Turns keyword clusters into BlogPost drafts using the AIContentEngine."""

    def __init__(self, upload: SEODataUpload, ai_engine: AIContentEngine | None = None):
        self.upload = upload
        self.ai_engine = ai_engine or AIContentEngine()

    def generate(self, *, cluster_limit: int = 3, category: str = "Insights") -> Dict[str, object]:
        clusters = list(
            self.upload.clusters.order_by("-priority_score", "-avg_volume")[:cluster_limit]
        )
        if not clusters:
            raise ValueError("Upload must have processed keyword clusters before generating blogs.")

        cluster_payload = [
            {
                "label": cluster.label,
                "intent": cluster.intent,
                "avg_volume": cluster.avg_volume,
                "priority_score": float(cluster.priority_score),
                "top_keywords": [
                    keyword.keyword
                    for keyword in cluster.keywords.order_by("-priority_score")[:5]
                ],
            }
            for cluster in clusters
        ]

        prompt = (
            "You are a senior content strategist at Codeteki. Based on the keyword clusters below, "
            "propose detailed blog drafts that will perform well organically.\n"
            f"Keyword data: {json.dumps(cluster_payload, ensure_ascii=False)}\n"
            "Return ONLY a JSON array. Each item requires:\n"
            "  - title: Compelling H1\n"
            "  - excerpt: 2 sentence summary under 300 characters\n"
            "  - outline: bullet list of H2/H3 structure\n"
            "  - content: markdown blog draft 600-800 words referencing the provided keywords\n"
            "  - keywords: array of keywords you used in the article\n"
            "No markdown fences, no commentary, just raw JSON."
        )

        result = self.ai_engine.generate(prompt=prompt, temperature=0.4)
        if not result.get("success"):
            error = result.get("error") or "AI blog generation failed."
            raise ValueError(error)

        posts_payload = self._parse_response(result.get("output", ""))
        created_posts = self._persist_posts(posts_payload, category)

        return {
            "created": len(created_posts),
            "post_ids": [post.id for post in created_posts],
            "ai_enabled": self.ai_engine.enabled,
            "model": self.ai_engine.model,
        }

    def _parse_response(self, raw_output: str) -> List[Dict[str, object]]:
        json_blob = self._extract_json(raw_output)
        try:
            data = json.loads(json_blob)
        except json.JSONDecodeError as exc:
            raise ValueError(f"AI response could not be parsed: {exc}") from exc

        if isinstance(data, dict):
            possible = data.get("posts") or data.get("blog_posts")
            if possible:
                data = possible
            else:
                data = [data]
        if not isinstance(data, list):
            raise ValueError("AI response was not a list of blog drafts.")
        return data

    @staticmethod
    def _extract_json(raw_output: str) -> str:
        text = raw_output.strip()
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 3:
                text = parts[1 if parts[1].strip() else 2]
        text = text.strip()
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            return text[start : end + 1]
        return text

    def _persist_posts(self, posts_payload: List[Dict[str, object]], category: str) -> List[BlogPost]:
        created: List[BlogPost] = []
        for entry in posts_payload:
            title = (entry.get("title") or "").strip()
            content = (entry.get("content") or "").strip()
            if not title or not content:
                continue

            excerpt = (entry.get("excerpt") or "").strip()
            if not excerpt:
                excerpt = Truncator(content).chars(300)
            keywords = entry.get("keywords") or []
            tags = ", ".join(keywords)[:255]

            slug = self._unique_slug(title)
            post = BlogPost.objects.create(
                title=title,
                slug=slug,
                excerpt=Truncator(excerpt).chars(320),
                content=content,
                author="Codeteki Automation",
                category=category,
                tags=tags,
                is_featured=False,
                is_published=False,
            )
            created.append(post)
        return created

    def _unique_slug(self, title: str) -> str:
        base = slugify(title) or slugify(f"{self.upload.name}-{len(title)}") or "blog-post"
        slug = base
        counter = 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug
