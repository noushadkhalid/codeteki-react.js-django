from __future__ import annotations

from django.conf import settings


class AIContentEngine:
    """
    Lightweight wrapper around OpenAI chat completions.

    Centralised here so other services (SEO automation, blog generator, chatbot)
    can share API key/config handling.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an AI strategist working for Codeteki. You help summarise data, "
        "draft marketing insights, and respond with confident, actionable copy."
    )

    def __init__(self, model: str | None = None):
        self.model = model or getattr(settings, "OPENAI_SEO_MODEL", "gpt-4o-mini")
        self.api_key = getattr(settings, "OPENAI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
            except ImportError:
                self.client = None
            else:
                self.client = OpenAI(api_key=self.api_key)

    @property
    def enabled(self) -> bool:
        return bool(self.client)

    def generate(
        self,
        *,
        prompt: str,
        temperature: float = 0.2,
        system_prompt: str | None = None,
    ) -> dict:
        """
        Execute a chat completion and return a normalised payload describing the output.
        """
        if not self.enabled:
            return {
                "success": False,
                "output": "AI generation is disabled. Provide an OPENAI_API_KEY to enable this feature.",
                "model": self.model,
                "usage": {},
                "error": "missing_api_key",
            }

        system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as exc:  # pragma: no cover - external API call
            return {
                "success": False,
                "output": "",
                "model": self.model,
                "usage": {},
                "error": str(exc),
            }

        message = response.choices[0].message.content if response.choices else ""
        usage = getattr(response, "usage", None)
        return {
            "success": True,
            "output": (message or "").strip(),
            "model": self.model,
            "usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
            },
        }
