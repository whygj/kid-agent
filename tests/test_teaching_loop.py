"""端到端教学闭环集成测试

模拟完整教学流程，验证知识库数据在主流程中流通。
不调用真实 LLM API，使用 mock。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.knowledge.service import get_knowledge_service
from src.knowledge.graph import KnowledgeGraph
from src.knowledge.loader import get_point


class TestTeachingLoop:
    """教学闭环测试"""

    @pytest.fixture
    def knowledge_service(self):
        """获取知识库服务"""
        return get_knowledge_service()

    def test_knowledge_base_integration(self, knowledge_service):
        """测试1: 知识库基本功能"""
        print("\n=== 测试1: 知识库基本功能 ===")

        # 验证知识点总数
        stats = knowledge_service.get_statistics()
        print(f"总知识点: {stats['total_concepts']}")
        print(f"前置依赖: {stats['total_relations']}")
        print(f"常见错误: {stats['total_mistakes']}")

        assert stats['total_concepts'] >= 300, "至少应该有300个知识点"

        # 验证3年级有知识点
        grade3_points = knowledge_service.get_points_by_grade(3)
        print(f"3年级知识点: {len(grade3_points)}个")
        assert len(grade3_points) > 0, "3年级应该有知识点"

        # 选择第一个知识点
        point = grade3_points[0]
        print(f"选中知识点: {point.name}")
        print(f"  ID: {point.id}")
        print(f"  难度: {point.difficulty}")
        print(f"  重要性: {point.importance}")

        # 验证知识点有定义和常见错误
        assert point.definition or point.description, "知识点应该有定义"
        assert len(point.examples) > 0, "知识点应该有示例"
        print(f"  定义长度: {len(point.definition) if point.definition else 0}")
        print(f"  示例数: {len(point.examples)}")

        print("[OK] 知识库基本功能测试通过")

    def test_common_mistakes_from_database(self, knowledge_service):
        """测试2: 常见错误从数据库获取"""
        print("\n=== 测试2: 常见错误从数据库获取 ===")

        # 找一个有常见错误的知识点
        grade_points = knowledge_service.get_points_by_grade(3)
        point_with_mistakes = None
        for point in grade_points:
            mistakes = knowledge_service.get_common_mistakes(point.id)
            if len(mistakes) > 0:
                point_with_mistakes = point
                break

        if not point_with_mistakes:
            pytest.skip("没有找到有常见错误的知识点")

        print(f"知识点: {point_with_mistakes.name}")

        # 直接获取常见错误
        mistakes = knowledge_service.get_common_mistakes(point_with_mistakes.id)
        print(f"常见错误数: {len(mistakes)}")
        print(f"示例错误: {mistakes[0][:50]}..." if mistakes else "无")

        assert len(mistakes) > 0, "应该能从数据库获取常见错误"

        print("[OK] 常见错误从数据库获取测试通过")

    def test_prerequisite_graph_analysis(self, knowledge_service):
        """测试3: 前置依赖图分析"""
        print("\n=== 测试3: 前置依赖图分析 ===")

        # 找一个有前置依赖的知识点
        grade_points = knowledge_service.get_points_by_grade(4)
        point_with_prereqs = None
        for point in grade_points:
            prereqs = knowledge_service.get_prerequisite_ids(point.id)
            if len(prereqs) > 0:
                point_with_prereqs = point
                break

        if not point_with_prereqs:
            pytest.skip("没有找到有前置依赖的知识点")

        print(f"知识点: {point_with_prereqs.name}")
        print(f"直接前置: {knowledge_service.get_prerequisite_ids(point_with_prereqs.id)}")

        # 获取递归前置依赖
        prereq_ids = knowledge_service.get_prerequisites_recursive(point_with_prereqs.id)
        print(f"递归前置数: {len(prereq_ids)}")

        assert len(prereq_ids) > 0, "应该能递归获取前置依赖"

        # 获取前置知识点详情
        prereq_details = []
        for pid in prereq_ids:
            detail = knowledge_service.get_knowledge_detail(pid)
            if detail:
                prereq_details.append(detail.name)

        print(f"前置知识点: {prereq_details[:3]}")

        print("[OK] 前置依赖图分析测试通过")

    def test_knowledge_graph_integration(self):
        """测试4: 知识图谱集成"""
        print("\n=== 测试4: 知识图谱集成 ===")

        graph = KnowledgeGraph()
        points = graph.get_all_points()

        print(f"图谱中知识点数: {len(points)}")
        assert len(points) >= 300, "图谱中应该有至少300个知识点"

        # 获取3年级点
        grade3_points = graph.get_points_by_grade(3)
        print(f"3年级知识点: {len(grade3_points)}个")
        assert len(grade3_points) > 0, "图谱应该有3年级知识点"

        # 测试前置依赖获取
        if grade3_points:
            point_id = grade3_points[0].id
            prereqs = graph.get_prerequisites_recursive(point_id)
            print(f"递归前置依赖: {len(prereqs)}个")
            # 可能为空，这是正常的

        print("[OK] 知识图谱集成测试通过")

    def test_next_learnable_points(self, knowledge_service):
        """测试5: 下一个可学习知识点"""
        print("\n=== 测试5: 下一个可学习知识点 ===")

        # 假设学生没有掌握任何知识点
        mastered_ids = set()
        learnable = knowledge_service.get_next_learnable_points(3, mastered_ids)

        print(f"可学习知识点数: {len(learnable)}")
        assert len(learnable) > 0, "应该有可学习的知识点"

        # 假设学生掌握了第一个知识点
        if learnable:
            mastered_ids.add(learnable[0].id)
            new_learnable = knowledge_service.get_next_learnable_points(3, mastered_ids)
            print(f"掌握1个后可学习: {len(new_learnable)}个")

        print("[OK] 下一个可学习知识点测试通过")

    def test_learning_path_generation(self, knowledge_service):
        """测试6: 学习路径生成"""
        print("\n=== 测试6: 学习路径生成 ===")

        # 获取一个有前置依赖的知识点
        grade4_points = knowledge_service.get_points_by_grade(4)
        target_point = None
        for point in grade4_points:
            prereq_ids = knowledge_service.get_prerequisite_ids(point.id)
            if len(prereq_ids) > 0:
                target_point = point
                break

        if not target_point:
            pytest.skip("没有找到有前置依赖的知识点")

        # 生成学习路径（假设没有掌握任何知识点）
        mastered_ids = set()
        path = knowledge_service.find_learning_path(target_point.id, mastered_ids)

        print(f"目标知识点: {target_point.name}")
        print(f"学习路径长度: {len(path)}")
        print(f"路径: {path[:5]}...")  # 显示前5个

        # 路径应该包含目标知识点
        assert target_point.id in path, "路径应该包含目标知识点"

        print("[OK] 学习路径生成测试通过")

    def test_knowledge_detail_completeness(self, knowledge_service):
        """测试7: 知识点详情完整性"""
        print("\n=== 测试7: 知识点详情完整性 ===")

        # 测试3年级第一个知识点
        grade3_points = knowledge_service.get_points_by_grade(3)
        if not grade3_points:
            pytest.skip("没有3年级知识点")

        point_id = grade3_points[0].id
        detail = knowledge_service.get_knowledge_detail(point_id)

        print(f"知识点: {detail.name}")
        print(f"  定义: {detail.definition[:50] if detail.definition else '无'}...")
        print(f"  示例数: {len(detail.examples)}")
        print(f"  常见错误数: {len(detail.common_mistakes)}")
        print(f"  别名数: {len(detail.aliases)}")
        print(f"  前置依赖: {len(detail.prerequisites)}")
        print(f"  后续依赖: {len(detail.dependents)}")

        # 验证关键字段
        assert detail.id == point_id, "ID应该匹配"
        assert detail.name, "应该有名称"
        assert detail.grade == 3, "年级应该正确"

        print("[OK] 知识点详情完整性测试通过")

    def test_search_functionality(self, knowledge_service):
        """测试8: 搜索功能"""
        print("\n=== 测试8: 搜索功能 ===")

        # 搜索"分数"
        results = knowledge_service.search_knowledge("分数", limit=5)

        print(f"搜索结果数: {len(results)}")
        for r in results[:3]:
            print(f"  - {r.name}")

        # 搜索不存在的词
        empty_results = knowledge_service.search_knowledge("不存在的知识点xyz", limit=5)
        print(f"空搜索结果: {len(empty_results)}")

        print("[OK] 搜索功能测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])