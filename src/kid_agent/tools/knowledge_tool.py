#!/usr/bin/env python
"""
Kid Knowledge Tool — DeepTutor BaseTool implementation.

Provides knowledge-base query capabilities for K-12 math education.
Wraps the kid-agent knowledge service (SQLite + knowledge graph).

Database schema:
- concepts: id, section_id, name, definition, importance, formula, aliases, examples, ...
- books: id, subject_id, grade, semester, publisher, version, title
- sections: id, book_id, name, ...
- relation_prerequisite: source_id, target_id, source_type, target_type, strength, evidence
- common_mistakes: id, concept_id, mistake, reason, correction, frequency
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

from deeptutor.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)

_KB_DIR = Path(os.environ.get(
    "KID_KB_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data"),
))
_KB_PATH = _KB_DIR / "knowledge.db"


def _get_conn() -> sqlite3.Connection:
    if not _KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge database not found: {_KB_PATH}")
    conn = sqlite3.connect(str(_KB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _query_concept(name: str) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT c.*, b.grade FROM concepts c "
            "JOIN sections s ON c.section_id = s.id "
            "JOIN books b ON s.book_id = b.id "
            "WHERE c.name LIKE ? LIMIT 1",
            (f"%{name}%",),
        ).fetchone()
        if not row:
            return None
        concept = dict(row)

        # Prerequisites (source_id → target_id means source is prereq of target)
        prereqs = conn.execute(
            "SELECT c2.name, b2.grade FROM relation_prerequisite rp "
            "JOIN concepts c2 ON rp.source_id = c2.id "
            "LEFT JOIN sections s2 ON c2.section_id = s2.id "
            "LEFT JOIN books b2 ON s2.book_id = b2.id "
            "WHERE rp.target_id = ?",
            (concept["id"],),
        ).fetchall()
        concept["prerequisites"] = [dict(r) for r in prereqs]

        # Common mistakes
        mistakes = conn.execute(
            "SELECT mistake, reason, correction FROM common_mistakes WHERE concept_id = ?",
            (concept["id"],),
        ).fetchall()
        concept["common_mistakes"] = [dict(r) for r in mistakes]

        return concept
    finally:
        conn.close()


def _search_concepts(query: str, limit: int = 10) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        # Try FTS first
        try:
            rows = conn.execute(
                "SELECT c.id, c.name, c.importance, b.grade FROM concepts c "
                "JOIN concepts_fts fts ON c.id = fts.rowid "
                "JOIN sections s ON c.section_id = s.id "
                "JOIN books b ON s.book_id = b.id "
                "WHERE concepts_fts MATCH ? "
                "ORDER BY rank LIMIT ?",
                (query, limit),
            ).fetchall()
            if rows:
                return [dict(r) for r in rows]
        except sqlite3.OperationalError:
            pass

        # Fallback to LIKE
        rows = conn.execute(
            "SELECT c.id, c.name, c.importance, b.grade FROM concepts c "
            "JOIN sections s ON c.section_id = s.id "
            "JOIN books b ON s.book_id = b.id "
            "WHERE c.name LIKE ? OR c.definition LIKE ? "
            "LIMIT ?",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _get_prerequisite_chain(name: str, depth: int = 3) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        chain = []
        visited = set()

        def _walk(target_id: str, current_depth: int):
            if current_depth > depth:
                return
            prereqs = conn.execute(
                "SELECT source_id FROM relation_prerequisite WHERE target_id = ?",
                (target_id,),
            ).fetchall()
            for r in prereqs:
                sid = r["source_id"]
                if sid in visited:
                    continue
                visited.add(sid)
                kp = conn.execute(
                    "SELECT c.id, c.name, c.importance, b.grade FROM concepts c "
                    "JOIN sections s ON c.section_id = s.id "
                    "JOIN books b ON s.book_id = b.id "
                    "WHERE c.id = ?",
                    (sid,),
                ).fetchone()
                if kp:
                    chain.append(dict(kp))
                    _walk(sid, current_depth + 1)

        start = conn.execute(
            "SELECT id FROM concepts WHERE name LIKE ? LIMIT 1",
            (f"%{name}%",),
        ).fetchone()
        if start:
            _walk(start["id"], 0)
        chain.sort(key=lambda x: (x.get("grade", 0)))
        return chain
    finally:
        conn.close()


def _get_concepts_by_grade(grade: int) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT c.id, c.name, c.importance, c.definition, b.grade FROM concepts c "
            "JOIN sections s ON c.section_id = s.id "
            "JOIN books b ON s.book_id = b.id "
            "WHERE b.grade = ? ORDER BY c.name",
            (grade,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


class KidKnowledgeTool(BaseTool):
    """DeepTutor tool for querying K-12 math knowledge base."""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="kid_knowledge",
            description=(
                "查询K-12数学知识库。支持：按名称查询知识点、搜索知识点、"
                "获取前置依赖链、按年级列出知识点、获取常见错误。"
                "数据来源：K12-KGraph（人教版1-9年级，304个知识点，322条依赖，840条常见错误）。"
            ),
            parameters=[
                ToolParameter(
                    name="action",
                    type="string",
                    description="操作类型：query(查详情)/search(搜索)/prereq_chain(依赖链)/by_grade(按年级)/mistakes(常见错误)",
                    required=True,
                    enum=["query", "search", "prereq_chain", "by_grade", "mistakes"],
                ),
                ToolParameter(
                    name="name",
                    type="string",
                    description="知识点名称（支持模糊匹配），用于query/prereq_chain/mistakes",
                    required=False,
                ),
                ToolParameter(
                    name="query",
                    type="string",
                    description="搜索关键词，用于search",
                    required=False,
                ),
                ToolParameter(
                    name="grade",
                    type="integer",
                    description="年级（1-9），用于by_grade",
                    required=False,
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="返回结果数量上限",
                    required=False,
                    default=10,
                ),
            ],
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action", "")
        name = kwargs.get("name", "")
        query = kwargs.get("query", "")
        grade = kwargs.get("grade")
        limit = int(kwargs.get("limit", 10))

        try:
            if action == "query":
                if not name:
                    return ToolResult(content="请提供知识点名称", success=False)
                result = _query_concept(name)
                if not result:
                    return ToolResult(content=f"未找到知识点: {name}", success=False)
                # Pretty print
                parts = [f"📚 {result['name']} ({result.get('grade', '?')}年级)"]
                if result.get("definition"):
                    parts.append(f"   定义: {result['definition']}")
                if result.get("importance"):
                    parts.append(f"   重要性: {result['importance']}")
                if result.get("prerequisites"):
                    parts.append(f"   前置知识: {', '.join(p['name'] for p in result['prerequisites'])}")
                if result.get("common_mistakes"):
                    parts.append(f"   常见错误: {len(result['common_mistakes'])}个")
                return ToolResult(
                    content="\n".join(parts),
                    metadata={"action": "query", "data": result},
                )

            elif action == "search":
                if not query:
                    return ToolResult(content="请提供搜索关键词", success=False)
                results = _search_concepts(query, limit)
                if not results:
                    return ToolResult(content=f"搜索'{query}'无结果", success=False)
                lines = [f"找到{len(results)}个知识点:"]
                for r in results:
                    lines.append(f"  - [{r.get('grade', '?')}年级] {r['name']} ({r.get('importance', '')})")
                return ToolResult(
                    content="\n".join(lines),
                    metadata={"action": "search", "count": len(results), "results": results},
                )

            elif action == "prereq_chain":
                if not name:
                    return ToolResult(content="请提供知识点名称", success=False)
                chain = _get_prerequisite_chain(name, depth=3)
                if not chain:
                    return ToolResult(content=f"'{name}'无前置依赖或未找到", success=False)
                arrow_chain = " → ".join(f"[{r.get('grade', '?')}年级]{r['name']}" for r in chain)
                return ToolResult(
                    content=f"前置依赖链 ({len(chain)}层):\n{arrow_chain}",
                    metadata={"action": "prereq_chain", "chain": chain},
                )

            elif action == "by_grade":
                if not grade:
                    return ToolResult(content="请提供年级(1-9)", success=False)
                results = _get_concepts_by_grade(int(grade))
                if not results:
                    return ToolResult(content=f"{grade}年级暂无知识点", success=False)
                lines = [f"{grade}年级共{len(results)}个知识点:"]
                for r in results:
                    lines.append(f"  - {r['name']} ({r.get('importance', '')})")
                return ToolResult(
                    content="\n".join(lines),
                    metadata={"action": "by_grade", "grade": grade, "count": len(results)},
                )

            elif action == "mistakes":
                if not name:
                    return ToolResult(content="请提供知识点名称", success=False)
                concept = _query_concept(name)
                if not concept:
                    return ToolResult(content=f"未找到知识点: {name}", success=False)
                mistakes = concept.get("common_mistakes", [])
                if not mistakes:
                    return ToolResult(content=f"'{concept['name']}'暂无常见错误数据")
                lines = [f"'{concept['name']}'的{len(mistakes)}个常见错误:"]
                for m in mistakes:
                    line = f"  - {m['mistake']}"
                    if m.get("reason"):
                        line += f" → 原因: {m['reason']}"
                    if m.get("correction"):
                        line += f" → 纠正: {m['correction']}"
                    lines.append(line)
                return ToolResult(
                    content="\n".join(lines),
                    metadata={"action": "mistakes", "mistakes": mistakes},
                )

            else:
                return ToolResult(
                    content=f"未知操作: {action}。支持: query/search/prereq_chain/by_grade/mistakes",
                    success=False,
                )

        except FileNotFoundError as e:
            return ToolResult(content=f"知识库未找到: {e}", success=False)
        except Exception as e:
            logger.exception("KidKnowledgeTool error")
            return ToolResult(content=f"查询出错: {e}", success=False)
