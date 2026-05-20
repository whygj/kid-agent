#!/usr/bin/env python
"""
Kid Tutor Capability — DeepTutor BaseCapability implementation.

Multi-stage tutoring pipeline: diagnose → plan → quiz → grade → explain → review.

Database schema (actual):
- concepts: id, section_id, name, definition, importance, formula, ...
- books: id, subject_id, grade, semester, publisher, version, title
- sections: id, book_id, name, ...
- relation_prerequisite: source_id (prereq) → target_id (concept)
- common_mistakes: id, concept_id, mistake, reason, correction, frequency
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

from kid_agent.core.capability_protocol import BaseCapability, CapabilityManifest
from kid_agent.core.context import UnifiedContext
from kid_agent.core.stream_bus import StreamBus

logger = logging.getLogger(__name__)

_KB_DIR = Path(os.environ.get(
    "KID_KB_DIR",
    str(Path(__file__).parent.parent / "data" / "kid_knowledge"),
))
_KB_PATH = _KB_DIR / "knowledge.db"

# Mastery levels
UNKNOWN = 0
EXPOSING = 1
FUZZY = 2
MASTERED = 3
FORGOTTEN = 4

MASTERY_LABELS = {
    UNKNOWN: "未学",
    EXPOSING: "接触中",
    FUZZY: "模糊理解",
    MASTERED: "已掌握",
    FORGOTTEN: "已遗忘",
}


def _get_conn() -> sqlite3.Connection:
    if not _KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge database not found: {_KB_PATH}")
    conn = sqlite3.connect(str(_KB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _get_prereq_ids(concept_id: str, conn: sqlite3.Connection) -> list[str]:
    """Get prerequisite concept IDs (source_id is the prereq of target_id)."""
    rows = conn.execute(
        "SELECT source_id FROM relation_prerequisite WHERE target_id = ?",
        (concept_id,),
    ).fetchall()
    return [r["source_id"] for r in rows]


def _concept_info(concept_id: str, conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT c.id, c.name, c.definition, c.importance, b.grade FROM concepts c "
        "JOIN sections s ON c.section_id = s.id "
        "JOIN books b ON s.book_id = b.id "
        "WHERE c.id = ?",
        (concept_id,),
    ).fetchone()
    return dict(row) if row else None


def _find_concept(name: str, conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT c.id, c.name, c.definition, c.importance, b.grade FROM concepts c "
        "JOIN sections s ON c.section_id = s.id "
        "JOIN books b ON s.book_id = b.id "
        "WHERE c.name LIKE ? LIMIT 1",
        (f"%{name}%",),
    ).fetchone()
    return dict(row) if row else None


def _get_mistakes(concept_id: str, conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT mistake, reason, correction FROM common_mistakes WHERE concept_id = ?",
        (concept_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _get_weakest_prerequisites(
    student_mastery: dict[str, int], concept_id: str, conn: sqlite3.Connection, depth: int = 3
) -> list[dict]:
    weak = []
    visited = set()

    def _walk(cid: str, d: int):
        if d > depth or cid in visited:
            return
        visited.add(cid)
        for pid in _get_prereq_ids(cid, conn):
            mastery = student_mastery.get(pid, UNKNOWN)
            if mastery < MASTERED:
                info = _concept_info(pid, conn)
                if info:
                    info["mastery"] = mastery
                    info["mastery_label"] = MASTERY_LABELS.get(mastery, "未知")
                    weak.append(info)
            _walk(pid, d + 1)

    _walk(concept_id, 0)
    weak.sort(key=lambda x: (x["mastery"], -x.get("grade", 0)))
    return weak


def _get_learnable_concepts(
    grade: int, student_mastery: dict[str, int], conn: sqlite3.Connection
) -> list[dict]:
    all_concepts = conn.execute(
        "SELECT c.id, c.name, c.definition, c.importance, b.grade FROM concepts c "
        "JOIN sections s ON c.section_id = s.id "
        "JOIN books b ON s.book_id = b.id "
        "WHERE b.grade = ? ORDER BY c.name",
        (grade,),
    ).fetchall()

    learnable = []
    for c in all_concepts:
        cd = dict(c)
        mastery = student_mastery.get(cd["id"], UNKNOWN)
        if mastery >= MASTERED:
            continue
        prereqs = _get_prereq_ids(cd["id"], conn)
        prereqs_met = all(student_mastery.get(pid, UNKNOWN) >= FUZZY for pid in prereqs)
        if prereqs_met:
            cd["mastery"] = mastery
            cd["mastery_label"] = MASTERY_LABELS.get(mastery, "未知")
            learnable.append(cd)
    return learnable


class KidTutorCapability(BaseCapability):
    """
    Multi-stage K-12 math tutoring capability for DeepTutor.

    Stages: diagnose → plan → quiz → grade → explain → review
    """

    manifest = CapabilityManifest(
        name="kid_tutor",
        description="K-12数学教学Agent：诊断薄弱点→学习路径规划→出题→批改→讲解→复习调度",
        stages=["diagnose", "plan", "quiz", "grade", "explain", "review"],
        tools_used=["kid_knowledge", "reason"],
        cli_aliases=["tutor", "数学教学", "出题"],
        config_defaults={
            "mastery_threshold": MASTERED,
            "quiz_difficulty_range": (1, 5),
            "review_intervals_days": [1, 3, 7, 14, 30],
        },
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        meta = context.metadata if hasattr(context, "metadata") else {}
        user_msg = context.user_message if hasattr(context, "user_message") else ""
        stage = meta.get("stage", "diagnose")
        grade = meta.get("grade", 3)
        kp_name = meta.get("knowledge_point", "")
        student_mastery: dict[str, int] = meta.get("student_mastery", {})

        conn = _get_conn()
        try:
            if stage == "diagnose":
                await self._diagnose(conn, student_mastery, grade, kp_name, stream)
            elif stage == "plan":
                await self._plan(conn, student_mastery, grade, stream)
            elif stage == "quiz":
                await self._quiz(conn, student_mastery, grade, kp_name, stream)
            elif stage == "grade":
                await self._grade(conn, student_mastery, user_msg, kp_name, stream)
            elif stage == "explain":
                await self._explain(conn, kp_name, stream)
            elif stage == "review":
                await self._review(conn, student_mastery, stream)
            else:
                async with stream.stage("error", source=self.manifest.name):
                    stream.emit(f"未知阶段: {stage}")
        finally:
            conn.close()

    async def _diagnose(self, conn, student_mastery: dict, grade: int, kp_name: str, stream: StreamBus) -> None:
        async with stream.stage("diagnose", source=self.manifest.name):
            stream.emit(f"🔍 开始诊断 {grade}年级学生的知识掌握情况...\n")

            if kp_name:
                concept = _find_concept(kp_name, conn)
                if concept:
                    weak = _get_weakest_prerequisites(student_mastery, concept["id"], conn)
                    if weak:
                        stream.emit(f"知识点 '{kp_name}' 的前置薄弱点:\n")
                        for w in weak[:5]:
                            stream.emit(f"  - [{w.get('grade', '?')}年级] {w['name']} ({w['mastery_label']})\n")
                    else:
                        stream.emit(f"✅ '{kp_name}' 的前置知识已全部掌握!\n")
                else:
                    stream.emit(f"⚠️ 未找到知识点: {kp_name}\n")
            else:
                learnable = _get_learnable_concepts(grade, student_mastery, conn)
                mastered_count = sum(1 for m in student_mastery.values() if m >= MASTERED)
                stream.emit(f"📊 {grade}年级诊断报告:\n")
                stream.emit(f"  已掌握: {mastered_count}个知识点\n")
                stream.emit(f"  可学习: {len(learnable)}个知识点\n")
                if learnable:
                    stream.emit("\n推荐学习顺序:\n")
                    for i, c in enumerate(learnable[:5], 1):
                        stream.emit(f"  {i}. {c['name']} ({c['mastery_label']})\n")

    async def _plan(self, conn, student_mastery: dict, grade: int, stream: StreamBus) -> None:
        async with stream.stage("plan", source=self.manifest.name):
            learnable = _get_learnable_concepts(grade, student_mastery, conn)
            stream.emit(f"📋 {grade}年级学习路径 ({len(learnable)}个可学习知识点):\n\n")
            for i, c in enumerate(learnable[:10], 1):
                mistakes = _get_mistakes(c["id"], conn)
                note = f" (⚠️{len(mistakes)}个常见错误)" if mistakes else ""
                stream.emit(f"  {i}. {c['name']}{note}\n")

    async def _quiz(self, conn, student_mastery: dict, grade: int, kp_name: str, stream: StreamBus) -> None:
        async with stream.stage("quiz", source=self.manifest.name):
            if kp_name:
                concept = _find_concept(kp_name, conn)
            else:
                learnable = _get_learnable_concepts(grade, student_mastery, conn)
                concept = learnable[0] if learnable else None

            if not concept:
                stream.emit("⚠️ 没有找到合适的知识点出题\n")
                return

            mistakes = _get_mistakes(concept["id"], conn)
            stream.emit(f"📝 出题: {concept['name']} ({concept.get('grade', grade)}年级)\n")
            if mistakes:
                stream.emit(f"  💡 利用{len(mistakes)}个常见错误生成干扰项\n")

            quiz_ctx = {
                "knowledge_point": concept["name"],
                "definition": concept.get("definition", ""),
                "importance": concept.get("importance", ""),
                "common_mistakes": [m["mistake"] for m in mistakes],
                "grade": concept.get("grade", grade),
            }
            stream.emit(f"\n题目上下文:\n{quiz_ctx}\n")

    async def _grade(self, conn, student_mastery: dict, user_answer: str, kp_name: str, stream: StreamBus) -> None:
        async with stream.stage("grade", source=self.manifest.name):
            stream.emit(f"✍️ 批改中...\n  学生回答: {user_answer[:100]}\n")

    async def _explain(self, conn, kp_name: str, stream: StreamBus) -> None:
        async with stream.stage("explain", source=self.manifest.name):
            if not kp_name:
                stream.emit("⚠️ 请指定要讲解的知识点\n")
                return
            concept = _find_concept(kp_name, conn)
            if not concept:
                stream.emit(f"⚠️ 未找到知识点: {kp_name}\n")
                return

            stream.emit(f"📖 讲解: {concept['name']} ({concept.get('grade', '?')}年级)\n\n")
            if concept.get("definition"):
                stream.emit(f"定义: {concept['definition']}\n\n")

            mistakes = _get_mistakes(concept["id"], conn)
            if mistakes:
                stream.emit("⚠️ 常见错误:\n")
                for m in mistakes[:5]:
                    line = f"  - {m['mistake']}"
                    if m.get("reason"):
                        line += f" → {m['reason']}"
                    stream.emit(f"{line}\n")

            prereqs = _get_prereq_ids(concept["id"], conn)
            if prereqs:
                stream.emit(f"\n📚 需要{len(prereqs)}个前置知识\n")

    async def _review(self, conn, student_mastery: dict, stream: StreamBus) -> None:
        async with stream.stage("review", source=self.manifest.name):
            stream.emit("🔄 复习调度（艾宾浩斯间隔: 1/3/7/14/30天）\n")
            fuzzy = sum(1 for m in student_mastery.values() if m == FUZZY)
            stream.emit(f"  模糊理解的知识点: {fuzzy}个（需优先复习）\n")
