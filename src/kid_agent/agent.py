#!/usr/bin/env python
"""
Kid Agent — Main Agent Entry Point
===================================

Initializes the DeepTutor runtime and registers kid-agent's
custom Tools and Capabilities.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from deeptutor.runtime.registry import (
    ToolRegistry,
    CapabilityRegistry,
    get_tool_registry,
    get_capability_registry,
)

from kid_agent.config import get_config, AgentConfig
from kid_agent.tools.knowledge_tool import KidKnowledgeTool
from kid_agent.capabilities.tutor import KidTutorCapability

logger = logging.getLogger(__name__)


class KidAgent:
    """
    K-12 Math Tutoring Agent powered by DeepTutor.

    Usage::

        agent = KidAgent()
        await agent.initialize()

        # Use via registries
        tool_reg = agent.tool_registry
        result = await tool_reg.execute(\"kid_knowledge\", action=\"query\", name=\"分数\")

        # Or run the tutor capability
        cap = agent.capability_registry.get(\"kid_tutor\")
    """

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or get_config()
        self._tool_registry: ToolRegistry | None = None
        self._capability_registry: CapabilityRegistry | None = None
        self._initialized = False

    @property
    def tool_registry(self) -> ToolRegistry:
        if self._tool_registry is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        return self._tool_registry

    @property
    def capability_registry(self) -> CapabilityRegistry:
        if self._capability_registry is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        return self._capability_registry

    async def initialize(self) -> None:
        """Initialize the agent: set up DeepTutor runtime and register custom components."""
        if self._initialized:
            logger.warning("KidAgent already initialized, skipping.")
            return

        # Set environment for DeepTutor
        for key, value in self.config.to_deeptutor_env().items():
            os.environ.setdefault(key, value)

        # 1. Initialize Tool Registry with DeepTutor builtins
        logger.info("Initializing Tool Registry...")
        self._tool_registry = ToolRegistry()
        self._tool_registry.load_builtins()
        logger.info("  Built-in tools: %s", self._tool_registry.list_tools())

        # 2. Register kid-agent's custom tool
        kid_knowledge_tool = KidKnowledgeTool()
        self._tool_registry.register(kid_knowledge_tool)
        logger.info("  Registered custom tool: %s", kid_knowledge_tool.name)

        # 3. Initialize Capability Registry with DeepTutor builtins
        logger.info("Initializing Capability Registry...")
        self._capability_registry = CapabilityRegistry()
        self._capability_registry.load_builtins()
        logger.info("  Built-in capabilities: %s", self._capability_registry.list_capabilities())

        # 4. Register kid-agent's custom capability
        kid_tutor_cap = KidTutorCapability()
        self._capability_registry.register(kid_tutor_cap)
        logger.info("  Registered custom capability: %s", kid_tutor_cap.manifest.name)

        self._initialized = True
        logger.info("KidAgent initialized successfully!")
        logger.info("  Tools: %s", self._tool_registry.list_tools())
        logger.info("  Capabilities: %s", self._capability_registry.list_capabilities())

    async def run_interactive(self) -> None:
        """Run an interactive CLI session."""
        if not self._initialized:
            await self.initialize()

        from kid_agent.cli import interactive_session
        await interactive_session(self)

    async def shutdown(self) -> None:
        """Clean up resources."""
        logger.info("KidAgent shutting down...")
        self._initialized = False


# Module-level convenience
_agent: KidAgent | None = None


async def get_agent() -> KidAgent:
    """Get or create the global KidAgent instance."""
    global _agent
    if _agent is None:
        _agent = KidAgent()
        await _agent.initialize()
    return _agent
