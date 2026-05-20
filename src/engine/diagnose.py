"""诊断引擎 - 分析学生薄弱点并生成学习建议"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from src.config.settings import get_config
from src.knowledge.graph import KnowledgeGraph
from src.knowledge.loader import get_point
from src.knowledge.service import get_knowledge_service


@dataclass
class WeakPoint:
    """薄弱知识点"""
    point_id: str
    point_name: str
    error_count: int
    total_count: int
    accuracy: float


@dataclass
class LearningRecommendation:
    """学习建议"""
    priority: int  # 优先级
    point_id: str
    point_name: str
    reason: str
    suggested_action: str


@dataclass
class DiagnosisReport:
    """诊断报告"""
    student_id: str
    weak_points: list[WeakPoint]
    recommendations: list[LearningRecommendation]
    overall_summary: str
    suggested_path: list[str]  # 推荐的学习路径（知识点ID）


class DiagnoseEngine:
    """诊断引擎"""

    def __init__(self):
        """初始化诊断引擎"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None
        self._graph = KnowledgeGraph()
        self._knowledge_service = get_knowledge_service()
        self._prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """加载诊断prompt模板"""
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "diagnose.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """你是专业的数学老师，请根据学生的做题情况分析薄弱点并给出学习建议。

学生年级：{grade}
总答题数：{total_count}
整体正确率：{accuracy:.1%}

薄弱知识点：
{weak_points_info}

请分析：
1. 学生的主要薄弱点是什么
2. 需要优先复习哪些知识点
3. 给出具体的学习建议

请用JSON格式返回：
{{
    "summary": "整体分析",
    "recommendations": [
        {{
            "priority": 1,
            "point_id": "知识点ID",
            "point_name": "知识点名称",
            "reason": "原因",
            "suggested_action": "建议"
        }}
    ]
}}
"""

    async def diagnose(
        self,
        student_id: str,
        grade: int,
        history_stats: dict[str, Any],
        mastered_points: set[str],
    ) -> DiagnosisReport:
        """诊断学生薄弱点"""
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        # 分析薄弱点
        weak_points = self._analyze_weak_points(history_stats)

        # 找出学习路径
        suggested_path = self._build_learning_path(weak_points, mastered_points)

        # 调用LLM生成建议
        recommendations = await self._generate_recommendations(
            grade,
            history_stats,
            weak_points,
        )

        # 生成整体总结
        overall_summary = self._generate_summary(
            history_stats,
            weak_points,
            recommendations,
        )

        return DiagnosisReport(
            student_id=student_id,
            weak_points=weak_points,
            recommendations=recommendations,
            overall_summary=overall_summary,
            suggested_path=suggested_path,
        )

    def _analyze_weak_points(
        self,
        history_stats: dict[str, Any],
        min_attempts: int = 2,
    ) -> list[WeakPoint]:
        """分析薄弱知识点"""
        weak_points: list[WeakPoint] = []
        point_stats = history_stats.get("point_stats", {})

        for point_id, stats in point_stats.items():
            total = stats.get("total", 0)
            if total < min_attempts:
                continue

            accuracy = stats.get("accuracy", 0)

            # 正确率低于60%视为薄弱
            if accuracy < 0.6:
                point = self._graph.get_point(point_id)
                if point:
                    weak_points.append(
                        WeakPoint(
                            point_id=point_id,
                            point_name=point.name,
                            error_count=total - int(total * accuracy),
                            total_count=total,
                            accuracy=accuracy,
                        )
                    )

        # 按正确率排序
        weak_points.sort(key=lambda x: x.accuracy)
        return weak_points

    def _build_learning_path(
        self,
        weak_points: list[WeakPoint],
        mastered_points: set[str],
    ) -> list[str]:
        """构建学习路径"""
        if not weak_points:
            return []

        # 找出需要补的前置知识
        path: list[str] = []
        visited: set[str] = set()

        for weak in weak_points:
            prerequisites = self._graph.get_prerequisites_recursive(weak.point_id)
            for prereq in prerequisites:
                if prereq.id not in mastered_points:
                    visited.add(prereq.id)
                    path.insert(0, prereq.id)

            if weak.point_id not in visited:
                visited.add(weak.point_id)
                path.append(weak.point_id)

        return path

    async def _generate_recommendations(
        self,
        grade: int,
        history_stats: dict[str, Any],
        weak_points: list[WeakPoint],
    ) -> list[LearningRecommendation]:
        """生成学习建议"""
        if not weak_points:
            return [
                LearningRecommendation(
                    priority=1,
                    point_id="review",
                    point_name="巩固复习",
                    reason="表现很好！",
                    suggested_action="继续做题巩固已掌握的知识点",
                )
            ]

        # 构建prompt
        weak_points_info = "\n".join(
            f"- {wp.point_name} (正确率: {wp.accuracy:.1%}, 错{wp.error_count}道题)"
            for wp in weak_points[:5]
        )

        prompt = self._prompt_template.format(
            grade=grade,
            total_count=history_stats.get("total_quizzes", 0),
            accuracy=history_stats.get("accuracy", 0),
            weak_points_info=weak_points_info,
        )

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是专业的数学老师，请用JSON格式返回学习建议。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=800,
        )

        return self._parse_recommendations(
            response.choices[0].message.content,
            weak_points,
        )

    def _parse_recommendations(
        self,
        content: str,
        weak_points: list[WeakPoint],
    ) -> list[LearningRecommendation]:
        """解析LLM返回的建议"""
        import json
        import re

        json_match = re.search(r'\{[^{}]*"recommendations".*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                recs = data.get("recommendations", [])
                return [
                    LearningRecommendation(
                        priority=r.get("priority", i + 1),
                        point_id=r.get("point_id", weak_points[i].point_id if i < len(weak_points) else "unknown"),
                        point_name=r.get("point_name", weak_points[i].point_name if i < len(weak_points) else "未知"),
                        reason=r.get("reason", ""),
                        suggested_action=r.get("suggested_action", ""),
                    )
                    for i, r in enumerate(recs)
                ]
            except json.JSONDecodeError:
                pass

        # 降级处理
        return [
            LearningRecommendation(
                priority=1,
                point_id=wp.point_id,
                point_name=wp.point_name,
                reason=f"正确率只有{wp.accuracy:.1%}",
                suggested_action="多加练习，复习相关知识点",
            )
            for wp in weak_points[:3]
        ]

    def _generate_summary(
        self,
        history_stats: dict[str, Any],
        weak_points: list[WeakPoint],
        recommendations: list[LearningRecommendation],
    ) -> str:
        """生成整体总结"""
        total = history_stats.get("total_quizzes", 0)
        accuracy = history_stats.get("accuracy", 0)

        if not weak_points:
            return f"太棒了！你总共完成了{total}道题，正确率{accuracy:.1%}，表现非常优秀！继续保持！"

        weak_names = [wp.point_name for wp in weak_points[:3]]
        weak_summary = f"、{'、'.join(weak_names)}还有进步空间。"

        return f"你完成了{total}道题，整体正确率{accuracy:.1%}。在{weak_summary}建议重点复习这几个知识点，加油！"


# 默认诊断引擎实例
_default_engine: DiagnoseEngine | None = None


async def get_diagnose_engine() -> DiagnoseEngine:
    """获取默认诊断引擎实例（懒加载）"""
    global _default_engine
    if _default_engine is None:
        _default_engine = DiagnoseEngine()
    return _default_engine