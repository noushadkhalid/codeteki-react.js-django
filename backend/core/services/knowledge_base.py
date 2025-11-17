from __future__ import annotations

from django.db.models import Q

from ..models import KnowledgeArticle


class KnowledgeBaseService:
    """
    Lightweight retrieval layer for chatbot responses.

    Currently uses keyword-based filtering. The interface keeps room for future
    upgrades (vector search, embeddings, etc.) without rewriting the chatbot service.
    """

    def __init__(self, limit: int = 3):
        self.limit = limit

    def search(self, query: str | None) -> list[KnowledgeArticle]:
        queryset = (
            KnowledgeArticle.objects.filter(status=KnowledgeArticle.STATUS_PUBLISHED)
            .select_related("category")
            .order_by("-is_featured", "-published_at", "-updated_at")
        )
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(content__icontains=query)
                | Q(keywords__icontains=query)
                | Q(tags__icontains=query)
            )
        return list(queryset[: self.limit])

    def to_context_block(self, articles: list[KnowledgeArticle]) -> str:
        blocks = []
        for article in articles:
            tags = ", ".join(article.tag_list())
            blocks.append(
                f"Title: {article.title}\n"
                f"Summary: {article.summary}\n"
                f"Tags: {tags}\n"
                f"CTA: {article.call_to_action or 'Book Codeteki strategy call'}\n"
            )
        return "\n---\n".join(blocks)
