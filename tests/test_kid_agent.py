#!/usr/bin/env python
"""
Tests for kid-agent tools and capabilities.
Run with: pytest tests/ -v
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is in the path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Set KID_KB_DIR to the test data directory
os.environ["KID_KB_DIR"] = str(PROJECT_ROOT / "data")


class TestKnowledgeModule:
    """Test the knowledge module."""

    def test_get_kb_stats(self):
        from kid_agent.knowledge import get_kb_stats
        stats = get_kb_stats()
        assert stats["concepts"] > 0, "Should have concepts in KB"
        assert stats["relations"] > 0, "Should have relations in KB"
        assert stats["mistakes"] > 0, "Should have mistakes in KB"
        print(f"KB Stats: {stats}")

    def test_get_kb_conn(self):
        from kid_agent.knowledge import get_kb_conn
        conn = get_kb_conn()
        row = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()
        conn.close()
        assert row[0] > 0


class TestKidKnowledgeTool:
    """Test the KidKnowledgeTool."""

    @pytest.fixture
    def tool(self):
        from kid_agent.tools.knowledge_tool import KidKnowledgeTool
        return KidKnowledgeTool()

    def test_get_definition(self, tool):
        defn = tool.get_definition()
        assert defn.name == "kid_knowledge"
        assert len(defn.parameters) > 0

    @pytest.mark.asyncio
    async def test_query_concept(self, tool):
        result = await tool.execute(action="query", name="分数")
        assert result.success, f"Query failed: {result.content}"
        assert "分数" in result.content

    @pytest.mark.asyncio
    async def test_search_concepts(self, tool):
        result = await tool.execute(action="search", query="加法")
        assert result.success, f"Search failed: {result.content}"

    @pytest.mark.asyncio
    async def test_by_grade(self, tool):
        result = await tool.execute(action="by_grade", grade=3)
        assert result.success, f"By grade failed: {result.content}"

    @pytest.mark.asyncio
    async def test_prereq_chain(self, tool):
        result = await tool.execute(action="prereq_chain", name="分数")

    @pytest.mark.asyncio
    async def test_mistakes(self, tool):
        result = await tool.execute(action="mistakes", name="分数")

    @pytest.mark.asyncio
    async def test_unknown_action(self, tool):
        result = await tool.execute(action="nonexistent")
        assert not result.success


class TestAgentInit:
    """Test agent initialization."""

    @pytest.mark.asyncio
    async def test_agent_initialize(self):
        from kid_agent.agent import KidAgent
        agent = KidAgent()
        await agent.initialize()
        assert "kid_knowledge" in agent.tool_registry.list_tools()
        assert "kid_tutor" in agent.capability_registry.list_capabilities()
        await agent.shutdown()

    @pytest.mark.asyncio
    async def test_agent_tool_query_via_tool(self):
        """Test tool execution via direct tool instance (not registry)."""
        from kid_agent.agent import KidAgent
        from kid_agent.tools.knowledge_tool import KidKnowledgeTool
        agent = KidAgent()
        await agent.initialize()
        # Use the tool directly to avoid ToolRegistry.execute name conflict
        tool = agent.tool_registry.get("kid_knowledge")
        assert tool is not None
        result = await tool.execute(action="query", name="加法")
        assert result.success
        await agent.shutdown()

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test that the tutor capability has correct manifest."""
        from kid_agent.capabilities.tutor import KidTutorCapability
        cap = KidTutorCapability()
        assert cap.manifest.name == "kid_tutor"
        assert "diagnose" in cap.manifest.stages
        assert "kid_knowledge" in cap.manifest.tools_used
