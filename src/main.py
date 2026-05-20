#!/usr/bin/env python
"""
Kid Agent - CLI Entry Point
============================

Usage:
    python -m src.main                 # Interactive CLI
    python -m src.main --mode web      # Web server
    python -m src.main query <name>    # Query a knowledge point
    python -m src.main stats           # Show knowledge base stats
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kid Agent - DeepTutor K-12 Math Tutor",
    )
    parser.add_argument("--mode", choices=["cli", "web", "api"], default="cli")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    subparsers = parser.add_subparsers(dest="command")
    query_parser = subparsers.add_parser("query", help="Query a knowledge point")
    query_parser.add_argument("name", help="Knowledge point name")
    subparsers.add_parser("stats", help="Show knowledge base statistics")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.command == "stats":
        asyncio.run(_run_stats())
    elif args.command == "query":
        asyncio.run(_run_query(args.name))
    elif args.mode == "cli":
        asyncio.run(_run_cli())
    elif args.mode in ("web", "api"):
        asyncio.run(_run_web(args.host, args.port))


async def _run_cli():
    from kid_agent.agent import get_agent
    agent = await get_agent()
    await agent.run_interactive()


async def _run_stats():
    from kid_agent.knowledge import get_kb_stats
    stats = get_kb_stats()
    print("Knowledge Base Stats:")
    print("  Concepts:", stats["concepts"])
    print("  Relations:", stats["relations"])
    print("  Mistakes:", stats["mistakes"])
    print("  Books:", stats["books"])
    print("  Path:", stats["path"])


async def _run_query(name: str):
    from kid_agent.agent import get_agent
    agent = await get_agent()
    result = await agent.tool_registry.execute(
        "kid_knowledge", action="query", name=name
    )
    print(result.content if hasattr(result, "content") else result)


async def _run_web(host: str, port: int):
    print(f"Starting web server on {host}:{port}")
    print("Web integration pending - use original src/web/app.py for now.")


if __name__ == "__main__":
    main()
