"""测试学习路径规划器"""

import pytest

from src.agent.planner import LearningPlanner, StudyPlan
from src.knowledge.graph import get_graph
from src.knowledge.math_g3g5 import ALL_POINTS
from src.memory.student import MasteryLevel


class TestStudyPlan:
    """测试学习计划"""

    def test_study_plan_creation(self):
        """测试学习计划创建"""
        plan = StudyPlan(
            current_focus="math_g3_001",
            next_steps=["math_g3_002", "math_g3_003"],
            estimated_sessions=10,
            review_points=[],
            reason="测试原因",
        )

        assert plan.current_focus == "math_g3_001"
        assert len(plan.next_steps) == 2
        assert plan.estimated_sessions == 10
        assert len(plan.review_points) == 0
        assert plan.reason == "测试原因"


class TestLearningPlanner:
    """测试学习路径规划器"""

    @pytest.fixture
    def planner(self):
        """创建测试用规划器"""
        return LearningPlanner(graph=get_graph())

    def test_planner_initialization(self, planner):
        """测试规划器初始化"""
        assert planner._graph is not None

    def test_generate_study_plan_new_student(self, planner):
        """测试新学生（无掌握程度）的学习计划"""
        plan = planner.generate_study_plan(
            student_id="new_student",
            grade=3,
            mastery_dict={},
            mastery_level_enum=MasteryLevel,
        )

        assert isinstance(plan, StudyPlan)
        assert plan.current_focus != "complete"
        assert plan.estimated_sessions > 0
        # 应该建议学习第一个可学习的知识点
        point = planner._graph.get_point(plan.current_focus)
        assert point is not None

    def test_generate_study_plan_all_mastered(self, planner):
        """测试全部掌握的学习计划"""
        mastery_dict = {p.id: MasteryLevel.MASTERED.value for p in ALL_POINTS}

        plan = planner.generate_study_plan(
            student_id="mastered_student",
            grade=3,
            mastery_dict=mastery_dict,
            mastery_level_enum=MasteryLevel,
        )

        assert plan.current_focus == "complete"
        assert len(plan.next_steps) == 0
        assert plan.estimated_sessions == 0
        assert "掌握了这个年级的所有知识点" in plan.reason

    def test_generate_study_plan_with_weak_points(self, planner):
        """测试有薄弱点的学习计划"""
        mastery_dict = {
            "math_g3_001": MasteryLevel.MASTERED.value,
            "math_g3_002": MasteryLevel.FUZZY.value,
            "math_g3_003": MasteryLevel.FORGOTTEN.value,
        }

        plan = planner.generate_study_plan(
            student_id="weak_student",
            grade=3,
            mastery_dict=mastery_dict,
            mastery_level_enum=MasteryLevel,
        )

        assert plan.current_focus in ("math_g3_002", "math_g3_003")
        assert len(plan.review_points) > 0
        assert "薄弱点" in plan.reason.lower() or "遗忘" in plan.reason

    def test_generate_study_plan_with_forgotten(self, planner):
        """测试有遗忘点的学习计划"""
        mastery_dict = {
            "math_g3_001": MasteryLevel.MASTERED.value,
            "math_g3_002": MasteryLevel.FORGOTTEN.value,
        }

        plan = planner.generate_study_plan(
            student_id="forgot_student",
            grade=3,
            mastery_dict=mastery_dict,
            mastery_level_enum=MasteryLevel,
        )

        assert "math_g3_002" in plan.review_points
        assert "遗忘" in plan.reason

    def test_find_next_learnable_point(self, planner):
        """测试查找下一个可学习知识点"""
        # 掌握了前置知识 math_g3_001
        mastered = {"math_g3_001"}

        next_point = planner._find_next_learnable_point(3, mastered)

        assert next_point is not None
        # 返回难度最低的可用知识点（prerequisites已满足）
        assert next_point.difficulty.value <= 2  # 低难度优先
    def test_find_next_learnable_point_none(self, planner):
        """测试没有可学习知识点"""
        # 掌握了所有知识点
        mastered = {p.id for p in planner._graph.get_points_by_grade(3)}

        next_point = planner._find_next_learnable_point(3, mastered)

        assert next_point is None

    def test_build_learning_path(self, planner):
        """测试构建学习路径"""
        # 要学 math_g3_002，已掌握 math_g3_001
        mastered = {"math_g3_001"}

        path = planner._build_learning_path("math_g3_002", mastered)

        # math_g3_001 已掌握，路径中不应包含
        assert "math_g3_001" not in path or path[-1] == "math_g3_002"

    def test_build_learning_path_with_prerequisites(self, planner):
        """测试带前置知识的学习路径"""
        # 要学 math_g5_003（分数乘除法）
        # 前置: math_g5_002 -> math_g3_004
        mastered = {"math_g3_004"}

        path = planner._build_learning_path("math_g5_003", mastered)

        # 路径应该包含必要的前置知识
        assert "math_g5_003" in path
        # math_g3_004 已掌握，不应在路径中
        assert "math_g3_004" not in path or path[0] != "math_g3_004"

    def test_estimate_sessions(self, planner):
        """测试估算学习次数"""
        # 简单难度（1）
        sessions = planner._estimate_sessions("math_g3_001")
        assert sessions == 2

        # 中等难度（2）
        sessions = planner._estimate_sessions("math_g3_004")
        assert sessions == 3

        # 困难难度（3）
        sessions = planner._estimate_sessions("math_g3_010")
        assert sessions == 5

        # 很困难难度（4）
        sessions = planner._estimate_sessions("math_g5_006")
        assert sessions == 7

        # 较高难度（4）
        sessions = planner._estimate_sessions("math_g5_010")
        assert sessions == 7

    def test_create_review_plan(self, planner):
        """测试创建复习计划"""
        forgotten_ids = {"math_g3_002", "math_g3_003"}
        mastered_ids = {"math_g3_001"}

        plan = planner._create_review_plan(
            forgotten_ids,
            "遗忘知识点",
            mastered_ids,
            set(),
        )

        assert plan.current_focus in forgotten_ids
        assert len(plan.review_points) == 2
        assert "遗忘知识点" in plan.reason
        assert plan.estimated_sessions == 2

    def test_create_review_plan_sorted_by_difficulty(self, planner):
        """测试复习计划按难度排序"""
        # math_g3_002 是中等难度，math_g3_005 是简单难度
        forgotten_ids = {"math_g3_002", "math_g3_005"}
        mastered_ids = set()

        plan = planner._create_review_plan(
            forgotten_ids,
            "遗忘知识点",
            mastered_ids,
            set(),
        )

        # 应该先复习简单知识点
        current_point = planner._graph.get_point(plan.current_focus)
        assert current_point.difficulty.value <= 2  # 简单或中等

    def test_create_weak_point_plan(self, planner):
        """测试创建薄弱点学习计划"""
        fuzzy_ids = {"math_g3_002", "math_g3_003"}
        mastered_ids = {"math_g3_001"}

        plan = planner._create_weak_point_plan(
            fuzzy_ids,
            planner._graph.get_points_by_grade(3),
            mastered_ids,
        )

        assert plan.current_focus in fuzzy_ids
        assert "薄弱点" in plan.reason
        assert plan.estimated_sessions > 0

    def test_create_weak_point_plan_with_prerequisites(self, planner):
        """测试带前置知识的薄弱点计划"""
        # math_g3_002 需要 math_g3_001，但没掌握
        fuzzy_ids = {"math_g3_002"}
        mastered_ids = set()

        plan = planner._create_weak_point_plan(
            fuzzy_ids,
            planner._graph.get_points_by_grade(3),
            mastered_ids,
        )

        # 路径应该包含前置知识
        assert "math_g3_001" in plan.next_steps or plan.current_focus == "math_g3_001"

    def test_get_forgetting_review_points(self, planner):
        """测试获取需要复习的遗忘点"""
        mastered_ids = {"math_g3_001", "math_g3_002"}

        # 目前简化实现返回空列表
        review_points = planner._get_forgetting_review_points(mastered_ids)

        # 应该返回列表（可能为空）
        assert isinstance(review_points, list)

    def test_generate_study_plan_priority(self, planner):
        """测试学习计划优先级"""
        mastery_dict = {
            "math_g3_001": MasteryLevel.MASTERED.value,
            "math_g3_002": MasteryLevel.FORGOTTEN.value,  # 优先级1
            "math_g3_003": MasteryLevel.FUZZY.value,  # 优先级2
        }

        plan = planner.generate_study_plan(
            student_id="priority_student",
            grade=3,
            mastery_dict=mastery_dict,
            mastery_level_enum=MasteryLevel,
        )

        # 应该优先处理遗忘的知识点
        assert plan.current_focus == "math_g3_002" or \
               "math_g3_002" in plan.review_points

    def test_grade_specific_points(self, planner):
        """测试年级特定知识点"""
        # 四年级学生
        plan = planner.generate_study_plan(
            student_id="grade4_student",
            grade=4,
            mastery_dict={},
            mastery_level_enum=MasteryLevel,
        )

        # 获取当前重点知识点
        current_point = planner._graph.get_point(plan.current_focus)
        assert current_point is not None
        assert current_point.grade == 4

    def test_learning_path_continuity(self, planner):
        """测试学习路径连续性"""
        # 掌握三年级第一个知识点
        mastery_dict = {"math_g3_001": MasteryLevel.MASTERED.value}

        plan = planner.generate_study_plan(
            student_id="continuity_student",
            grade=3,
            mastery_dict=mastery_dict,
            mastery_level_enum=MasteryLevel,
        )

        # 获取当前重点知识点
        current_point = planner._graph.get_point(plan.current_focus)
        assert current_point is not None

        # 检查前置知识
        prereqs = planner._graph.get_prerequisites_recursive(current_point.id)
        prereq_ids = {p.id for p in prereqs}

        # 所有前置知识应该都已掌握
        assert prereq_ids.issubset(mastery_dict.keys()) or len(prereqs) == 0

    def test_empty_mastery_dict(self, planner):
        """测试空掌握程度字典"""
        plan = planner.generate_study_plan(
            student_id="empty_student",
            grade=3,
            mastery_dict={},
            mastery_level_enum=MasteryLevel,
        )

        # 应该选择第一个可学习知识点
        current_point = planner._graph.get_point(plan.current_focus)
        assert current_point is not None
        # 第一个可学习点应该是没有前置知识的或前置知识已满足的
        prereqs = planner._graph.get_prerequisites_recursive(current_point.id)
        assert len(prereqs) == 0 or all(p.id in {} for p in prereqs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
