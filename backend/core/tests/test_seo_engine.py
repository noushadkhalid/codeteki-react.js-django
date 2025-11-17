from __future__ import annotations

from django.core.files.base import ContentFile
from django.test import TestCase

from core.models import AISEORecommendation, BlogPost, SEODataUpload


class StubAIEngine:
    def __init__(self, response=None):
        self.model = "stub"
        self.enabled = True
        self._response = response

    def generate(self, *, prompt: str, temperature: float = 0.2, system_prompt: str | None = None):
        if callable(self._response):
            output = self._response(prompt)
        elif isinstance(self._response, str):
            output = self._response
        else:
            output = "stub-response"
        return {
            "success": True,
            "output": output,
            "model": self.model,
            "usage": {"prompt_tokens": 10, "completion_tokens": 50},
        }


class SEOAutomationEngineTests(TestCase):
    def _create_upload(self) -> SEODataUpload:
        csv_data = """Keyword,Search Volume,SEO Difficulty,Paid Difficulty,CPC
AI agency melbourne,320,28,35,4.5
voice ai agency,90,18,40,2.5
chatbot development cost,260,32,40,6.0
"""
        file = ContentFile(csv_data.encode("utf-8"), name="keywords.csv")
        return SEODataUpload.objects.create(name="Test Upload", csv_file=file)

    def test_ingest_from_file_populates_keywords(self):
        upload = self._create_upload()
        result = upload.ingest_from_file()

        self.assertEqual(upload.status, SEODataUpload.STATUS_PROCESSED)
        self.assertEqual(upload.keywords.count(), 3)
        self.assertGreater(upload.clusters.count(), 0)
        self.assertIn("total_keywords", upload.insights)
        self.assertEqual(result["rows"], 3)

    def test_ai_automation_creates_recommendations_with_stub_engine(self):
        upload = self._create_upload()
        upload.ingest_from_file()

        upload.run_ai_automation(cluster_limit=1, ai_engine=StubAIEngine(), refresh=True)

        self.assertTrue(AISEORecommendation.objects.filter(upload=upload).exists())

    def test_generate_blog_posts_creates_drafts(self):
        upload = self._create_upload()
        upload.ingest_from_file()

        blog_payload = """
[
  {
    "title": "AI Agency Melbourne Playbook",
    "excerpt": "Learn how Melbourne businesses deploy AI agencies.",
    "content": "# AI Agency Melbourne\\nContent body with strategies.",
    "keywords": ["ai agency melbourne", "voice ai agency"]
  }
]
"""
        upload.generate_blog_posts(
            cluster_limit=1,
            ai_engine=StubAIEngine(response=blog_payload),
        )

        post = BlogPost.objects.first()
        self.assertIsNotNone(post)
        self.assertFalse(post.is_published)
        self.assertIn("AI Agency", post.title)
