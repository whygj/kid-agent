"""测试知识图谱和知识点加载"""

import pytest

from src.knowledge.graph import KnowledgeGraph, get_graph
from src.knowledge.math_g3g5 import (
    ALL_POINTS,
    Difficulty,
    KnowledgePoint,
    get_point_by_id,
    get_points_by_grade,
    get_points_by_difficulty,
)


class TestKnowledgePoint:
    """测试知识点数据结构"""

    def test_knowledge_point_creation(self):
        """测试知识点创建"""
        point = KnowledgePoint(
            id="test_001",
            name="测试知识点",
            grade=3,
            difficulty=Difficulty.EASY,
            prerequisites=[],
            description="这是一个测试知识点",
        )

        assert point.id == "test_001"
        assert point.name == "测试知识点"
        assert point.grade == 3
        assert point.difficulty == Difficulty.EASY
        assert point.prerequisites == []

    def test_knowledge_point_default_values(self):
        """测试知识点默认值"""
        point = KnowledgePoint(
            id="test_002",
            name="默认测试",
            grade=4,
        )

        assert point.subject == "数学"
        assert point.difficulty == Difficulty.MEDIUM
        assert point.prerequisites == []
        assert point.examples == []
        assert point.common_mistakes == []


class TestAllPoints:
    """测试所有知识点加载"""

    def test_all_points_count(self):
        """测试知识点总数（30个）"""
        assert len(ALL_POINTS) == 30, f"期望30个知识点，实际{len(ALL_POINTS)}个"

    def test_grade_3_points_count(self):
        """测试三年级知识点数量（10个）"""
        grade_3 = [p for p in ALL_POINTS if p.grade == 3]
        assert len(grade_3) == 10, f"期望10个三年级知识点，实际{len(grade_3)}个"

    def test_grade_4_points_count(self):
        """测试四年级知识点数量（10个）"""
        grade_4 = [p for p in ALL_POINTS if p.grade == 4]
        assert len(grade_4) == 10, f"期望10个四年级知识点，实际{len(grade_4)}个"

    def test_grade_5_points_count(self):
        """测试五年级知识点数量（10个）"""
        grade_5 = [p for p in ALL_POINTS if p.grade == 5]
        assert len(grade_5) == 10, f"期望10个五年级知识点，实际{len(grade_5)}个"

    def test_point_ids_format(self):
        """测试知识点ID格式正确"""
        for point in ALL_POINTS:
            assert point.id.startswith(("math_g3_", "math_g4_", "math_g5_")), \
                f"知识点ID格式错误: {point.id}"

    def test_unique_point_ids(self):
        """测试知识点ID唯一性"""
        ids = [p.id for p in ALL_POINTS]
        assert len(ids) == len(set(ids)), "存在重复的知识点ID"


class TestGetPointById:
    """测试根据ID获取知识点"""

    def test_get_existing_point(self):
        """测试获取存在的知识点"""
        point = get_point_by_id("math_g3_001")
        assert point is not None
        assert point.id == "math_g3_001"
        assert point.name == "乘法口诀"
        assert point.grade == 3

    def test_get_nonexistent_point(self):
        """测试获取不存在的知识点"""
        point = get_point_by_id("nonexistent_id")
        assert point is None


class TestGetPointsByGrade:
    """测试按年级查询知识点"""

    def test_get_grade_3_points(self):
        """测试获取三年级知识点"""
        points = get_points_by_grade(3)
        assert len(points) == 10
        assert all(p.grade == 3 for p in points)

    def test_get_grade_4_points(self):
        """测试获取四年级知识点"""
        points = get_points_by_grade(4)
        assert len(points) == 10
        assert all(p.grade == 4 for p in points)

    def test_get_grade_5_points(self):
        """测试获取五年级知识点"""
        points = get_points_by_grade(5)
        assert len(points) == 10
        assert all(p.grade == 5 for p in points)

    def test_get_invalid_grade_points(self):
        """测试获取不存在年级的知识点"""
        points = get_points_by_grade(1)
        assert len(points) == 0
        points = get_points_by_grade(6)
        assert len(points) == 0


class TestGetPointsByDifficulty:
    """测试按难度查询知识点"""

    def test_get_easy_points(self):
        """测试获取简单知识点"""
        points = get_points_by_difficulty(Difficulty.EASY)
        assert all(p.difficulty == Difficulty.EASY for p in points)

    def test_get_medium_points(self):
        """测试获取中等难度知识点"""
        points = get_points_by_difficulty(Difficulty.MEDIUM)
        assert all(p.difficulty == Difficulty.MEDIUM for p in points)


class TestKnowledgeGraph:
    """测试知识图谱功能"""

    @pytest.fixture
    def graph(self):
        """创建测试用知识图谱"""
        return KnowledgeGraph(ALL_POINTS)

    def test_graph_initialization(self, graph):
        """测试知识图谱初始化"""
        assert len(graph.get_all_points()) == 30

    def test_get_point(self, graph):
        """测试获取知识点"""
        point = graph.get_point("math_g3_001")
        assert point is not None
        assert point.name == "乘法口诀"

    def test_get_prerequisites(self, graph):
        """测试获取前置知识点"""
        # math_g3_002 依赖 math_g3_001
        prereqs = graph.get_prerequisites("math_g3_002")
        prereq_ids = [p.id for p in prereqs]
        assert "math_g3_001" in prereq_ids

    def test_get_prerequisites_recursive(self, graph):
        """测试递归获取前置知识点"""
        # math_g5_003 依赖 math_g5_002, math_g5_002 依赖 math_g3_004
        prereqs = graph.get_prerequisites_recursive("math_g5_003")
        prereq_ids = [p.id for p in prereqs]
        assert "math_g5_002" in prereq_ids
        assert "math_g3_004" in prereq_ids

    def test_get_dependents(self, graph):
        """测试获取后续知识点"""
        # math_g3_001 被多个知识点依赖
        dependents = graph.get_dependents("math_g3_001")
        dependent_ids = [d.id for d in dependents]
        assert "math_g3_002" in dependent_ids
        assert "math_g3_003" in dependent_ids

    def test_get_weak_points(self, graph):
        """测试获取薄弱点"""
        # 掌握 math_g3_001，未掌握其依赖的知识点
        mastered = {"math_g3_001"}
        weak = graph.get_weak_points(mastered)
        weak_ids = [w.id for w in weak]
        # math_g3_002 和 math_g3_003 依赖 math_g3_001，且其前置已掌握
        assert "math_g3_002" in weak_ids
        assert "math_g3_003" in weak_ids

    def test_get_weak_points_empty(self, graph):
        """测试无薄弱点情况"""
        mastered = {p.id for p in ALL_POINTS}
        weak = graph.get_weak_points(mastered)
        assert len(weak) == 0

    def test_find_learning_path(self, graph):
        """测试查找学习路径"""
        # 要学 math_g5_003，但还没学数学基础
        mastered = set()
        path = graph.find_learning_path("math_g5_003", mastered)
        # 路径应包含必要的前置知识
        path_ids = [p.id for p in path]
        assert len(path) > 0
        assert "math_g5_003" in path_ids

    def test_get_points_by_grade_in_graph(self, graph):
        """测试在图中按年级获取知识点"""
        grade_3_points = graph.get_points_by_grade(3)
        assert len(grade_3_points) == 10
        assert all(p.grade == 3 for p in grade_3_points)

    def test_get_points_by_difficulty_in_graph(self, graph):
        """测试在图中按难度获取知识点"""
        easy_points = graph.get_points_by_difficulty(1)
        assert all(p.difficulty.value == 1 for p in easy_points)

    def test_to_dict(self, graph):
        """测试导出为字典"""
        data = graph.to_dict()
        assert "points" in data
        assert "graph" in data
        assert len(data["points"]) == 30


class TestGetGraph:
    """测试全局知识图谱单例"""

    def test_get_graph_singleton(self):
        """测试全局知识图谱单例"""
        graph1 = get_graph()
        graph2 = get_graph()
        assert graph1 is graph2

    def test_get_graph_content(self):
        """测试获取的内容正确"""
        # 全局 graph 从数据库加载，不是固定的 30 个点
        # 只验证它返回了数据
        graph = get_graph()
        points = graph.get_all_points()
        assert len(points) > 0


class TestKnowledgePointDependencies:
    """测试知识点依赖关系"""

    def test_prerequisite_chain(self):
        """测试前置知识链"""
        # math_g5_003 (分数乘除法) -> math_g5_002 (分数加减法) -> math_g3_004 (分数初步认识)
        point = get_point_by_id("math_g5_003")
        assert point is not None
        assert "math_g5_002" in point.prerequisites

        prereq = get_point_by_id("math_g5_002")
        assert prereq is not None
        assert "math_g3_004" in prereq.prerequisites

    def test_circular_dependencies(self):
        """测试无循环依赖"""
        graph = get_graph()
        for point in ALL_POINTS:
            # 获取递归前置知识
            prereqs = graph.get_prerequisites_recursive(point.id)
            prereq_ids = {p.id for p in prereqs}
            # 确保不自引用
            assert point.id not in prereq_ids, f"知识点 {point.id} 存在自引用"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
