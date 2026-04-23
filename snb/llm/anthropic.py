"""Anthropic Claude client.

Thin wrapper over the official ``anthropic`` SDK that:
- lazy-imports the SDK (kept optional via extras [llm])
- centralises the default model + max_tokens
- applies prompt caching on the system prompt automatically
- exposes a tiny ``chat()`` surface so callers don't juggle SDK details

Why caching here: most SNB agents reuse the same multi-paragraph system
prompt across hundreds of calls (lead scoring, reply drafting, digest). With
``cache_control: ephemeral`` the 5-minute cache absorbs the cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from snb.config import get_logger, get_settings
from snb.core.exceptions import AuthError

_log = get_logger("llm.anthropic")


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str


class AnthropicClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        s = get_settings().llm
        key = api_key or (
            s.anthropic_api_key.get_secret_value() if s.anthropic_api_key else None
        )
        if not key:
            raise AuthError("Anthropic requires LLM_ANTHROPIC_API_KEY")

        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "anthropic not installed; run: pip install -e '.[llm]'"
            ) from e

        self._client = AsyncAnthropic(api_key=key)
        self.model = model or s.default_model
        self.max_tokens = max_tokens

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        cache_system: bool = True,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        """One-shot chat. Returns the assistant's text content."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if system:
            if cache_system:
                kwargs["system"] = [
                    {
                        "type": "text",
                        "text": system,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]
            else:
                kwargs["system"] = system

        resp = await self._client.messages.create(**kwargs)
        usage = getattr(resp, "usage", None)
        if usage is not None:
            _log.debug(
                "anthropic usage in={in_} out={out} cache_read={cr} cache_create={cc}",
                in_=getattr(usage, "input_tokens", None),
                out=getattr(usage, "output_tokens", None),
                cr=getattr(usage, "cache_read_input_tokens", None),
                cc=getattr(usage, "cache_creation_input_tokens", None),
            )
        blocks = [b for b in resp.content if getattr(b, "type", None) == "text"]
        return "".join(getattr(b, "text", "") for b in blocks).strip()
