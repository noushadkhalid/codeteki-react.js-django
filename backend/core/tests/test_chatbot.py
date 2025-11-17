from __future__ import annotations

from django.test import TestCase

from core.models import (
    ChatConversation,
    ChatbotSettings,
    KnowledgeArticle,
    KnowledgeCategory,
)
from core.services.chatbot import ChatbotService


class StubAIEngine:
    def __init__(self, response: str = "stub-response"):
        self.response = response
        self.model = "stub"
        self.enabled = True

    def generate(self, *, prompt: str, temperature: float = 0.2, system_prompt: str | None = None):
        return {
            "success": True,
            "output": self.response,
            "model": self.model,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }


class ChatbotServiceTests(TestCase):
    def setUp(self):
        category = KnowledgeCategory.objects.create(name="General", slug="general")
        KnowledgeArticle.objects.create(
            category=category,
            title="AI Workforce Overview",
            slug="ai-workforce-overview",
            summary="How Codeteki deploys AI copilots.",
            content="<p>Detailed automation playbook.</p>",
            status=KnowledgeArticle.STATUS_PUBLISHED,
            tags="ai,automation",
            is_featured=True,
        )
        ChatbotSettings.objects.create(name="Codeteki AI", intro_message="Hi there!")

    def test_public_config_returns_defaults(self):
        payload = ChatbotService.public_config()
        self.assertIn("intro", payload)
        self.assertEqual(payload["name"], "Codeteki AI")

    def test_reply_uses_stub_engine(self):
        conversation = ChatConversation.objects.create(visitor_name="Test User")
        service = ChatbotService(conversation, ai_engine=StubAIEngine("Hello from stub"))

        payload = service.reply("Tell me about AI copilots")

        self.assertIn("response", payload)
        self.assertEqual(payload["response"], "Hello from stub")
        self.assertTrue(conversation.messages.filter(role="assistant").exists())
