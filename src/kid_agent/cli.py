#!/usr/bin/env python
"""
Kid Agent CLI — Interactive command-line interface.
"""

from __future__ import annotations

import asyncio
import json
import logging

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from kid_agent.knowledge import get_kb_stats

logger = logging.getLogger(__name__)
console = Console()


async def interactive_session(agent) -> None:
    """Run an interactive CLI session with the agent."""
    console.print(Panel(
        "[bold blue]Kid Agent[/bold blue] — 基于DeepTutor的K-12数学教学助手\n"
        "[dim]输入知识点名称查询、或使用命令: /stats, /tools, /caps, /quit[/dim]",
        border_style="blue",
    ))

    # Show KB stats
    try:
        stats = get_kb_stats()
        console.print(f"\n📊 知识库: {stats['concepts']}个知识点, {stats['relations']}条依赖, {stats['mistakes']}个常见错误\n")
    except Exception:
        console.print("\n⚠️ 知识库未找到，部分功能不可用\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]你[/bold green]", console=console).strip()
            if not user_input:
                continue

            if user_input.lower() in ("/quit", "/exit", "quit", "exit", "退出", "拜拜"):
                console.print("👋 再见！明天见~")
                break

            if user_input == "/stats":
                _show_stats()
                continue

            if user_input == "/tools":
                _show_tools(agent)
                continue

            if user_input == "/caps":
                _show_capabilities(agent)
                continue

            # Default: query knowledge base
            result = await agent.tool_registry.execute(
                "kid_knowledge", action="query", name=user_input,
            )
            if hasattr(result, 'content'):
                console.print(result.content)
            else:
                console.print(str(result))
            console.print()

        except KeyboardInterrupt:
            console.print("\n👋 再见！明天见~")
            break
        except EOFError:
            console.print("\n👋 再见！明天见~")
            break
        except Exception as e:
            console.print(f"[red]出错了: {e}[/red]")
            logger.exception("CLI error")


def _show_stats() -> None:
    try:
        stats = get_kb_stats()
        table = Table(title="知识库统计")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="green")
        table.add_row("知识点", str(stats["concepts"]))
        table.add_row("依赖关系", str(stats["relations"]))
        table.add_row("常见错误", str(stats["mistakes"]))
        table.add_row("教材", str(stats["books"]))
        table.add_row("路径", stats["path"])
        console.print(table)
    except Exception as e:
        console.print(f"[red]获取统计失败: {e}[/red]")


def _show_tools(agent) -> None:
    tools = agent.tool_registry.list_tools()
    table = Table(title="已注册工具")
    table.add_column("名称", style="cyan")
    for t in tools:
        table.add_row(t)
    console.print(table)


def _show_capabilities(agent) -> None:
    caps = agent.capability_registry.list_capabilities()
    table = Table(title="已注册能力")
    table.add_column("名称", style="cyan")
    for c in caps:
        table.add_row(c)
    console.print(table)
