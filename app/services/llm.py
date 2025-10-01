from __future__ import annotations

import logging
from enum import Enum

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.llms.types import ChatResponse
from llama_index.llms.gemini import Gemini
from llama_index.llms.openai import OpenAI

from app.core.config import get_settings


logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_llm(self, provider: LLMProvider) -> OpenAI | Gemini:
        if provider is LLMProvider.OPENAI:
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured")
            return OpenAI(api_key=self.settings.openai_api_key)
        if provider is LLMProvider.GEMINI:
            if not self.settings.google_api_key:
                raise RuntimeError("GOOGLE_API_KEY is not configured")
            return Gemini(api_key=self.settings.google_api_key)
        raise ValueError(f"Unsupported provider: {provider}")

    def _resolve_provider(self, preferred: str | None) -> LLMProvider:
        if preferred:
            try:
                return LLMProvider(preferred.lower())
            except ValueError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Unknown LLM provider '{preferred}'") from exc
        return LLMProvider(self.settings.default_llm_provider.lower())

    def chat(
        self,
        *,
        history: list[ChatMessage],
        user_message: str,
        provider: str | None,
    ) -> ChatResponse:
        llm_provider = self._resolve_provider(provider)
        llm = self._get_llm(llm_provider)

        messages = history + [ChatMessage(role=MessageRole.USER, content=user_message)]
        logger.debug("Dispatching %d messages to %s", len(messages), llm_provider.value)
        return llm.chat(messages=messages)

    @staticmethod
    def to_chat_messages(records: list[dict[str, str]]) -> list[ChatMessage]:
        chat_messages: list[ChatMessage] = []
        for record in records:
            role = MessageRole(record["role"])
            chat_messages.append(ChatMessage(role=role, content=record["content"]))
        return chat_messages
