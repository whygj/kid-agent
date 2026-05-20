"""LLM provider adapter that reuses DeepTutor's LLM configuration.

When TutorBot runs in-process inside the DeepTutor server, this provider
reads api_key / model / base_url from DeepTutor's unified config and
delegates to the appropriate provider (OpenAICompat or Anthropic).
"""

from __future__ import annotations

from typing import cast

from kid_agent.services.llm.config import LLMConfig
from kid_agent.tutorbot.providers.base import LLMProvider


def create_kid_agent_provider(config: LLMConfig | None = None) -> LLMProvider:
    """Build a provider pre-configured from DeepTutor's LLMConfig."""
    from kid_agent.services.llm.provider_factory import get_runtime_provider

    return cast(LLMProvider, get_runtime_provider(config))
