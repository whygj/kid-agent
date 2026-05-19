"""学习路径规划器 - 根据学生掌握程度生成个性化学习计划"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from src.knowledge.graph import KnowledgeGraph, get_graph


@dataclass
class StudyPlan:
    """学习计划"""
    current_focus: str  # 当前重点学习知识点ID
    next_steps: list[str]  # 下一步学习路径 [point_id...]
    estimated_sessions: int  # 预计需要的学习次数
    review_points: list[str]  # 需要复习的知识点ID列表
    reason: str  # 为什么这样安排


class LearningPlanner:
    """学习路径规划器"""

    def __init__(self, graph: KnowledgeGraph | None = None):
        """初始化学习路径规划器"""
        self._graph = graph or get_graph()

    def generate_study_plan(
        self,
        student_id: str,
        grade: int,
        mastery_dict: dict[str, int],
        mastery_level_enum: Any,
    ) -> StudyPlan:
        """生成学习计划

        Args:
            student_id: 学生ID
            grade: 年级
            mastery_dict: 掌握程度字典 {point_id: mastery_level}
            mastery_level_enum: 掌握程度枚举类

        Returns:
            StudyPlan: 学习计划
        """
        # 获取已掌握和需要加强的知识点
        mastered_ids = {
            pid for pid, level in mastery_dict.items()
            if level >= mastery_level_enum.MASTERED.value
        }
        fuzzy_ids = {
            pid for pid, level in mastery_dict.items()
            if level == mastery_level_enum.FUZZY.value
        }
        forgotten_ids = {
            pid for pid, level in mastery_dict.items()
            if level == mastery_level_enum.FORGOTTEN.value
        }

        # 获取年级所有知识点
        grade_points = self._graph.get_points_by_grade(grade)

        # 1. 优先处理遗忘的知识点
        if forgotten_ids:
            return self._create_review_plan(
                forgotten_ids, "遗忘知识点", mastered_ids, fuzzy_ids
            )

        # 2. 处理模糊的知识点（薄弱点）
        if fuzzy_ids:
            return self._create_weak_point_plan(
                fuzzy_ids, grade_points, mastered_ids
            )

        # 3. 检查需要复习的已掌握知识点（遗忘曲线）
        review_points = self._get_forgetting_review_points(
            mastered_ids, days_threshold=7
        )
        if review_points:
            return self._create_review_plan(
                review_points, "需要复习", mastered_ids, fuzzy_ids
            )

        # 4. 找出下一个可以学习的新知识点
        next_point = self._find_next_learnable_point(grade, mastered_ids)
        if next_point:
            next_steps = self._build_learning_path(next_point.id, mastered_ids)
            return StudyPlan(
                current_focus=next_point.id,
                next_steps=next_steps,
                estimated_sessions=self._estimate_sessions(next_point.id),
                review_points=[],
                reason=f"你已经准备好了，可以学习{next_point.name}！这是你下一个目标~",
            )

        # 5. 所有知识点都掌握了
        return StudyPlan(
            current_focus="complete",
            next_steps=[],
            estimated_sessions=0,
            review_points=[],
            reason="太棒了！你已经掌握了这个年级的所有知识点！继续加油！",
        )

    def _create_review_plan(
        self,
        point_ids: set[str],
        review_type: str,
        mastered_ids: set[str],
        fuzzy_ids: set[str],
    ) -> StudyPlan:
        """创建复习计划"""
        # 按难度排序，先复习简单知识点
        review_points = sorted(
            point_ids,
            key=lambda pid: self._graph.get_point(pid).difficulty.value
            if self._graph.get_point(pid) else 3,
        )

        current_focus = review_points[0]

        return StudyPlan(
            current_focus=current_focus,
            next_steps=review_points[1:],
            estimated_sessions=len(review_points),
            review_points=review_points,
            reason=f"发现有{len(review_points)}个{review_type}需要复习，先从最简单的开始吧！",
        )

    def _create_weak_point_plan(
        self,
        fuzzy_ids: set[str],
        grade_points: list,
        mastered_ids: set[str],
    ) -> StudyPlan:
        """创建薄弱点学习计划"""
        # 找出每个薄弱点的前置知识
        plan_points: list[str] = []
        visited: set[str] = set()

        for point_id in fuzzy_ids:
            if point_id in visited:
                continue

            # 检查前置知识是否已掌握
            prereqs = self._graph.get_prerequisites_recursive(point_id)
            unmastered_prereqs = [
                p for p in prereqs if p.id not in mastered_ids
            ]

            # 先学习未掌握的前置
            for prereq in unmastered_prereqs:
                if prereq.id not in visited:
                    visited.add(prereq.id)
                    plan_points.append(prereq.id)

            if point_id not in visited:
                visited.add(point_id)
                plan_points.append(point_id)

        current_focus = plan_points[0] if plan_points else "unknown"

        return StudyPlan(
            current_focus=current_focus,
            next_steps=plan_points[1:],
            estimated_sessions=len(plan_points) * 3,
            review_points=[],
            reason=f"找到{len(fuzzy_ids)}个薄弱点，需要加强练习！我们会先补上前置知识，然后再攻克这些难点~",
        )

    def _find_next_learnable_point(
        self,
        grade: int,
        mastered_ids: set[str],
    ) -> Any | None:
        """找出下一个可以学习的新知识点"""
        grade_points = self._graph.get_points_by_grade(grade)

        # 按难度和依赖关系排序
        candidates: list[Any] = []
        for point in grade_points:
            if point.id in mastered_ids:
                continue

            # 检查前置知识是否都已掌握
            prereqs = self._graph.get_prerequisites_recursive(point.id)
            prereq_ids = {p.id for p in prereqs}
            if prereq_ids.issubset(mastered_ids):
                candidates.append(point)

        # 优先选择难度较低的
        candidates.sort(key=lambda p: p.difficulty.value)
        return candidates[0] if candidates else None

    def _build_learning_path(
        self,
        target_id: str,
        mastered_ids: set[str],
    ) -> list[str]:
        """构建从当前状态到目标的学习路径"""
        path = self._graph.find_learning_path(target_id, mastered_ids)
        return [p.id for p in path if p.id != target_id] + [target_id]

    def _estimate_sessions(self, point_id: str) -> int:
        """估算掌握该知识点需要的学习次数"""
        point = self._graph.get_point(point_id)
        if not point:
            return 3

        # 根据难度估算
        difficulty_multiplier = {
            1: 2,  # 简单：2次
            2: 3,  # 中等：3次
            3: 5,  # 困难：5次
            4: 7,  # 很困难：7次
            5: 10,  # 专家级：10次
        }
        return difficulty_multiplier.get(point.difficulty.value, 3)

    def _get_forgetting_review_points(
        self,
        mastered_ids: set[str],
        days_threshold: int = 7,
    ) -> list[str]:
        """获取可能遗忘的知识点（需要根据实际数据实现）"""
        # 这里简化处理，返回需要复习的知识点
        # 实际实现应该结合ReviewScheduler的历史数据
        return []


# 默认学习路径规划器实例
_default_planner: LearningPlanner | None = None


def get_planner() -> LearningPlanner:
    """获取默认学习路径规划器实例（懒加载）"""
    global _default_planner
    if _default_planner is None:
        _default_planner = LearningPlanner()
    return _default_planner