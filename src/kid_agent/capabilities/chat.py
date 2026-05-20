"""Agentic chat capability."""

from __future__ import annotations

from kid_agent.agents.chat.agentic_pipeline import CHAT_OPTIONAL_TOOLS, AgenticChatPipeline
from kid_agent.capabilities.request_contracts import get_capability_request_schema
from kid_agent.core.capability_protocol import BaseCapability, CapabilityManifest
from kid_agent.core.context import UnifiedContext
from kid_agent.core.stream_bus import StreamBus


class ChatCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="chat",
        description="Agentic chat with autonomous tool selection across enabled tools.",
        stages=["thinking", "acting", "observing", "responding"],
        tools_used=CHAT_OPTIONAL_TOOLS,
        cli_aliases=["chat"],
        request_schema=get_capability_request_schema("chat"),
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        pipeline = AgenticChatPipeline(language=context.language)
        await pipeline.run(context, stream)
