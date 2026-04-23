"""LLM clients. Anthropic-first, with OpenAI as optional fallback.

Prompt caching is on by default — every long system prompt is wrapped with
``cache_control: ephemeral``. Cache hits cost ~10% of a normal input token,
so even modestly-reused system prompts pay back fast.
"""

from snb.llm.anthropic import AnthropicClient, ChatMessage

__all__ = ["AnthropicClient", "ChatMessage"]
