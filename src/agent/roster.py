"""多学生管理 - 管理多个学生信息和学习报告"""

from dataclasses import dataclass
from typing import Any

from src.memory.student import MasteryLevel


@dataclass
class StudentSummary:
    """学生摘要信息"""
    student_id: str
    name: str
    grade: int
    level: int  # 等级
    total_xp: int  # 总经验值
    streak_days: int  # 连续学习天数
    mastered_count: int  # 已掌握知识点数
    fuzzy_count: int  # 模糊知识点数
    unknown_count: int  # 未接触知识点数
    total_quizzes: int  # 总答题数
    accuracy: float  # 正确率
    weak_points: list[str]  # 薄弱点列表
    learning_days: int  # 学习天数


@dataclass
class StudentReport:
    """学生学习报告"""
    student: StudentSummary
    mastery_distribution: dict[str, int]  # 掌握程度分布
    best_points: list[str]  # 表现最好的知识点
    worst_points: list[str]  # 表现最差的知识点
    recent_trend: list[bool]  # 最近10题趋势
    suggestions: list[str]  # 学习建议


class StudentRoster:
    """学生名册管理"""

    def __init__(self, store=None, graph=None):
        """初始化学生名册

        Args:
            store: 存储实例
            graph: 知识图谱
        """
        self._store = store
        self._graph = graph

    async def list_students(self) -> list[StudentSummary]:
        """获取所有学生列表

        Returns:
            list[StudentSummary]: 学生摘要列表
        """
        if not self._store:
            return []

        # 从数据库获取所有学生
        # 暂时返回空列表（需要添加 get_all_students 方法）
        return []

    async def get_all_students(self) -> list[Any]:
        """获取所有学生基本信息"""
        if not self._store:
            return []

        # TODO: 添加 get_all_students 到 store.py
        # 暂时返回空列表
        return []

    async def get_student_summary(self, student_id: str) -> StudentSummary | None:
        """获取学生摘要信息

        Args:
            student_id: 学生ID

        Returns:
            StudentSummary | None: 学生摘要信息
        """
        if not self._store:
            return None

        # 获取学生基本信息
        student = await self._store.get_student(student_id)
        if not student:
            return None

        # 获取掌握程度
        mastery_data = await self._store.get_mastery(student_id)

        # 统计各掌握程度数量
        mastered = sum(
            1 for level in mastery_data.values()
            if level >= MasteryLevel.MASTERED.value
        )
        fuzzy = sum(
            1 for level in mastery_data.values()
            if level == MasteryLevel.FUZZY.value
        )
        unknown = sum(
            1 for level in mastery_data.values()
            if level == MasteryLevel.UNKNOWN.value
        )

        # 获取薄弱点
        weak_points = self._get_weak_points(mastery_data)

        # 获取答题统计
        stats = await self._store.get_student_stats(student_id)

        # 计算等级
        level = 1 + student.total_xp // 100

        # 估算学习天数（根据答题记录分布）
        learning_days = self._estimate_learning_days(student_id)

        return StudentSummary(
            student_id=student_id,
            name=student.name,
            grade=student.grade,
            level=level,
            total_xp=student.total_xp,
            streak_days=student.streak_days,
            mastered_count=mastered,
            fuzzy_count=fuzzy,
            unknown_count=unknown,
            total_quizzes=stats.get("total_quizzes", 0),
            accuracy=stats.get("accuracy", 0),
            weak_points=weak_points,
            learning_days=learning_days,
        )

    async def get_student_report(self, student_id: str) -> StudentReport | None:
        """获取学生学习报告

        Args:
            student_id: 学生ID

        Returns:
            StudentReport | None: 学习报告
        """
        summary = await self.get_student_summary(student_id)
        if not summary:
            return None

        # 获取掌握程度分布
        mastery_data = await self._store.get_mastery(student_id)
        mastery_distribution = self._calculate_mastery_distribution(mastery_data)

        # 获取表现最好和最差的知识点
        point_stats = await self._store.get_student_stats(student_id)
        point_stats_data = point_stats.get("point_stats", {})

        best_points, worst_points = self._get_best_and_worst_points(
            point_stats_data, mastery_data
        )

        # 获取最近答题趋势
        recent_history = await self._store.get_student_history(student_id, limit=10)
        recent_trend = [r.is_correct for r in recent_history]

        # 生成学习建议
        suggestions = self._generate_suggestions(summary, mastery_data, point_stats)

        return StudentReport(
            student=summary,
            mastery_distribution=mastery_distribution,
            best_points=best_points,
            worst_points=worst_points,
            recent_trend=recent_trend,
            suggestions=suggestions,
        )

    def format_summary_text(self, summary: StudentSummary) -> str:
        """格式化学生摘要为文本

        Args:
            summary: 学生摘要

        Returns:
            str: 格式化文本
        """
        lines = [
            f"📊 学生学习报告",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"姓名: {summary.name}",
            f"年级: {summary.grade}年级",
            f"等级: {summary.level}级 ({summary.total_xp} XP)",
            f"连续学习: {summary.streak_days}天",
            f"学习天数: {summary.learning_days}天",
            f"",
            f"📚 知识掌握情况:",
            f"  已掌握: {summary.mastered_count}个",
            f"  需加强: {summary.fuzzy_count}个",
            f"  未接触: {summary.unknown_count}个",
            f"",
            f"📝 答题统计:",
            f"  总题数: {summary.total_quizzes}道",
            f"  正确率: {summary.accuracy:.1%}",
            f"",
        ]

        if summary.weak_points:
            lines.append("🔍 薄弱点:")
            for point in summary.weak_points[:5]:
                lines.append(f"  • {point}")

        return "\n".join(lines)

    def format_report_text(self, report: StudentReport) -> str:
        """格式化学习报告为文本

        Args:
            report: 学习报告

        Returns:
            str: 格式化文本
        """
        lines = [self.format_summary_text(report.student)]
        lines.append("")

        # 掌握程度分布
        lines.append("📈 掌握程度分布:")
        for level_name, count in report.mastery_distribution.items():
            if count > 0:
                lines.append(f"  {level_name}: {count}个")

        # 表现最好的知识点
        if report.best_points:
            lines.append("")
            lines.append("🌟 表现最好:")
            for point in report.best_points[:3]:
                lines.append(f"  • {point}")

        # 表现最差的知识点
        if report.worst_points:
            lines.append("")
            lines.append("⚠️ 需要加强:")
            for point in report.worst_points[:3]:
                lines.append(f"  • {point}")

        # 学习建议
        if report.suggestions:
            lines.append("")
            lines.append("💡 学习建议:")
            for i, suggestion in enumerate(report.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        return "\n".join(lines)

    def _get_weak_points(self, mastery_data: dict[str, int]) -> list[str]:
        """获取薄弱知识点"""
        weak = []
        for point_id, level in mastery_data.items():
            if level in (MasteryLevel.FUZZY.value, MasteryLevel.FORGOTTEN.value):
                weak.append(point_id)
        return weak

    def _calculate_mastery_distribution(
        self,
        mastery_data: dict[str, int],
    ) -> dict[str, int]:
        """计算掌握程度分布"""
        distribution = {
            "未接触": 0,
            "接触中": 0,
            "模糊": 0,
            "已掌握": 0,
            "已遗忘": 0,
        }

        for level in mastery_data.values():
            if level == MasteryLevel.UNKNOWN.value:
                distribution["未接触"] += 1
            elif level == MasteryLevel.EXPOSING.value:
                distribution["接触中"] += 1
            elif level == MasteryLevel.FUZZY.value:
                distribution["模糊"] += 1
            elif level == MasteryLevel.MASTERED.value:
                distribution["已掌握"] += 1
            elif level == MasteryLevel.FORGOTTEN.value:
                distribution["已遗忘"] += 1

        return distribution

    def _get_best_and_worst_points(
        self,
        point_stats: dict[str, dict],
        mastery_data: dict[str, int],
    ) -> tuple[list[str], list[str]]:
        """获取表现最好和最差的知识点"""
        best = []
        worst = []

        for point_id, stats in point_stats.items():
            if stats.get("total", 0) < 2:
                continue

            accuracy = stats.get("accuracy", 0)
            point = self._graph.get_point(point_id) if self._graph else None
            name = point.name if point else point_id

            if accuracy >= 0.9:
                best.append(name)
            elif accuracy < 0.6:
                worst.append(name)

        # 排序并限制数量
        best = sorted(best, key=lambda x: len(x))[:5]
        worst = sorted(worst, key=lambda x: len(x))[:5]

        return best, worst

    def _generate_suggestions(
        self,
        summary: StudentSummary,
        mastery_data: dict[str, int],
        point_stats: dict[str, dict],
    ) -> list[str]:
        """生成学习建议"""
        suggestions = []

        # 根据薄弱点给出建议
        if summary.weak_points:
            suggestions.append(
                f"重点练习薄弱知识点: {summary.weak_points[0]}"
            )

        # 根据正确率给出建议
        if summary.accuracy >= 0.8:
            suggestions.append("表现很棒！继续保持，可以尝试挑战更难的题目~")
        elif summary.accuracy >= 0.6:
            suggestions.append("还需要多加练习，注意答题速度和准确性")
        else:
            suggestions.append("建议从基础开始复习，不要急于做难题")

        # 根据连续学习天数给出建议
        if summary.streak_days >= 7:
            suggestions.append("你已经坚持学习一周了，太厉害了！继续保持~")
        elif summary.streak_days >= 3:
            suggestions.append("连续学习3天了，再坚持一下就能突破一周！")
        else:
            suggestions.append("建议每天坚持学习，养成好习惯很重要~")

        return suggestions

    def _estimate_learning_days(self, student_id: str) -> int:
        """估算学习天数"""
        # 根据答题记录的日期分布估算
        # 简化处理：返回固定值
        # 实际实现应该从数据库统计唯一日期数
        return 1


# 默认学生名册实例
_default_roster: StudentRoster | None = None


def get_student_roster() -> StudentRoster:
    """获取默认学生名册实例（懒加载）"""
    global _default_roster
    if _default_roster is None:
        _default_roster = StudentRoster()
    return _default_roster