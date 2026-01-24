from __future__ import annotations

from typing import Dict

from ..models import ChatConversation, ChatLead, ChatMessage, ChatbotSettings
from .ai_client import AIContentEngine
from .knowledge_base import KnowledgeBaseService
from .chat_knowledge import ChatKnowledgeBuilder


class ChatbotService:
    """Handles AI chat flows, knowledge retrieval, and lead enrichment."""

    @classmethod
    def public_config(cls) -> Dict[str, object]:
        settings = ChatbotSettings.objects.order_by("-updated_at").first()
        if not settings:
            return {
                "name": "Codeteki AI",
                "personaTitle": "Automation Strategist",
                "intro": "Hi! I'm Codeteki's AI assistant. Ask me anything.",
                "accentColor": "#f9cb07",
                "quickReplies": [
                    "How does Codeteki work?",
                    "Do you offer website development?",
                    "Show me AI automation examples",
                ],
            }
        return {
            "name": settings.name,
            "personaTitle": settings.persona_title,
            "intro": settings.intro_message,
            "accentColor": settings.accent_color,
            "quickReplies": settings.quick_replies,
            "meetingLink": settings.meeting_link,
            "contactEmail": settings.contact_email,
        }

    def __init__(
        self,
        conversation: ChatConversation,
        *,
        ai_engine: AIContentEngine | None = None,
        knowledge_limit: int = 3,
    ):
        self.conversation = conversation
        self.settings = ChatbotSettings.objects.order_by("-updated_at").first()
        self.ai_engine = ai_engine or AIContentEngine()
        self.knowledge = KnowledgeBaseService(limit=knowledge_limit)
        self.knowledge_builder = ChatKnowledgeBuilder()
        self.dynamic_knowledge = self.knowledge_builder.build()
        self.dynamic_context_text = self.knowledge_builder.to_prompt_block(self.dynamic_knowledge)

    def _system_prompt(self) -> str:
        brand = self.settings.brand_voice if self.settings else "Confident & helpful"
        intro = (
            f"You are {self.settings.name} from Codeteki."
            if self.settings
            else "You are Codeteki's AI consultant."
        )
        return (
            f"{intro} Use a {brand.lower()} tone. "
            "Answer concisely, include CTAs when relevant, and gather lead details politely. "
            "If you don't know something, admit it and suggest speaking with a human."
        )

    def _create_chat_message(self, role: str, content: str, **metadata):
        return ChatMessage.objects.create(
            conversation=self.conversation,
            role=role,
            content=content,
            metadata=metadata,
        )

    def _record_lead(self, ai_response: str):
        try:
            self.conversation.lead
        except ChatLead.DoesNotExist:
            pass
        else:
            return
        if not self.settings or not self.settings.lead_capture_prompt:
            return
        if "email" in ai_response.lower() or "contact" in ai_response.lower():
            ChatLead.objects.create(conversation=self.conversation)

    def reply(self, user_message: str) -> Dict[str, object]:
        user_entry = self._create_chat_message(ChatMessage.ROLE_USER, user_message)
        self.conversation.last_user_message = user_message
        self.conversation.save(update_fields=["last_user_message", "updated_at"])

        articles = self.knowledge.search(user_message)
        context_block = self.knowledge.to_context_block(articles)
        prompt = self._build_prompt(
            user_message,
            knowledge_context=context_block,
            dynamic_context=self.dynamic_context_text,
        )

        ai_result = self.ai_engine.generate(
            prompt=prompt,
            temperature=0.3,
            system_prompt=self._system_prompt(),
        )
        if not ai_result.get("success"):
            fallback = (
                self.settings.fallback_message
                if self.settings
                else "Let me hand this to a teammate and we’ll reply ASAP."
            )
            response_text = fallback
        else:
            response_text = ai_result.get("output", "")

        assistant_entry = self._create_chat_message(
            ChatMessage.ROLE_ASSISTANT,
            response_text,
            context_articles=[article.slug for article in articles],
            model=ai_result.get("model"),
        )

        if ai_result.get("usage"):
            assistant_entry.token_count = (
                ai_result["usage"].get("prompt_tokens", 0)
                + ai_result["usage"].get("completion_tokens", 0)
            )
            assistant_entry.save(update_fields=["token_count", "metadata", "updated_at"])

        self._record_lead(response_text)
        self._sync_to_crm()

        payload = {
            "response": response_text,
            "conversationId": str(self.conversation.conversation_id),
            "articles": [
                {
                    "title": article.title,
                    "summary": article.summary,
                    "slug": article.slug,
                    "category": article.category.name,
                }
                for article in articles
            ],
            "usage": ai_result.get("usage", {}),
        }
        if not self.ai_engine.enabled:
            payload["notice"] = "AI disabled; served fallback copy."
        return payload

    def _build_prompt(self, user_message: str, *, knowledge_context: str, dynamic_context: str) -> str:
        intro = (
            "Use the following knowledge snippets to answer the user. "
            "If the context does not cover the question, answer generically "
            "and offer to connect them with Codeteki."
        )
        kb_context = knowledge_context or "No curated knowledge articles found."
        dynamic = dynamic_context or ""
        history_snippet = self._recent_history()
        return (
            f"{intro}\n"
            f"Knowledge Articles:\n{kb_context}\n\n"
            f"Company Data:\n{dynamic}\n\n"
            f"Conversation so far:\n{history_snippet}\n\n"
            f"Latest question: {user_message}"
        )

    def _recent_history(self, limit: int = 4) -> str:
        history = self.conversation.messages.order_by("-created_at")[:limit]
        rows = []
        for message in reversed(history):
            rows.append(f"{message.role.capitalize()}: {message.content}")
        return "\n".join(rows)

    def _sync_to_crm(self):
        """Auto-add chatbot lead to CRM pipeline if email is provided."""
        if not self.conversation.visitor_email:
            return
        # Only sync once (check metadata)
        if self.conversation.metadata.get('crm_synced'):
            return
        try:
            from crm.services.lead_integration import LeadIntegrationService
            contact, deal, created = LeadIntegrationService.create_lead_from_chat(
                self.conversation,
                auto_create_deal=True
            )
            if contact:
                self.conversation.metadata['crm_synced'] = True
                self.conversation.metadata['crm_contact_id'] = str(contact.id)
                if deal:
                    self.conversation.metadata['crm_deal_id'] = str(deal.id)
                self.conversation.save(update_fields=['metadata', 'updated_at'])
        except Exception:
            pass  # Don't break chat if CRM sync fails
