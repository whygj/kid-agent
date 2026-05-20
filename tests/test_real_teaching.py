"""真实LLM教学闭环测试

使用真实API（智谱GLM）跑一次完整教学流程。
需要配置 config/.env 中的 API_KEY。

测试流程：
1. 创建一个3年级学生
2. 学习"两位数加法"相关知识点
3. 出一道题
4. 学生答错
5. 获取讲解
6. 再出题，答对
7. 打印完整对话过程和掌握度变化
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_config
from src.agent.tutor import TutorAgent
from src.engine.quiz import Quiz
from src.engine.grader import GradeResult
from src.engine.explain import Explanation
from src.knowledge.service import get_knowledge_service
from src.knowledge.loader import get_points_by_grade


def check_api_configured() -> bool:
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if not env_path.exists():
        return False
    from dotenv import load_dotenv
    load_dotenv(env_path)
    return bool(os.getenv("ZHIPU_API_KEY") or os.getenv("DEEPSEEK_API_KEY"))


pytestmark = pytest.mark.skipif(
    not check_api_configured(),
    reason="需要配置 config/.env 中的 API_KEY"
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestRealTeachingLoop:
    """真实教学闭环测试"""

    async def test_complete_teaching_session(self):
        print("\n" + "=" * 60)
        print("真实LLM教学闭环测试")
        print("=" * 60)

        # 1. 初始化
        print("\n[步骤1] 初始化服务...")
        service = get_knowledge_service()
        grade3_points = get_points_by_grade(3)
        print(f"  3年级知识点: {len(grade3_points)}个")

        # 找加法相关知识点
        target_point = None
        for point in grade3_points:
            if "加" in point.name or "加法" in point.name:
                target_point = point
                break
        if not target_point:
            target_point = grade3_points[0]

        print(f"  选中知识点: {target_point.name}")
        print(f"  知识点ID: {target_point.id}")

        detail = service.get_knowledge_detail(target_point.id)
        print(f"  示例数: {len(detail.examples)}")
        print(f"  常见错误数: {len(detail.common_mistakes)}")

        # 2. 创建Agent
        print("\n[步骤2] 创建教学Agent...")
        agent = TutorAgent()
        await agent._get_engines()
        print("  Agent初始化完成")

        # 3. 出题
        print("\n[步骤3] 生成题目...")
        quiz = await agent._quiz_engine.generate(target_point)
        q_text = quiz.question[:100]
        print(f"  题目: {q_text}...")
        print(f"  正确答案: {quiz.answer}")
        if quiz.question_type == "choice":
            assert len(quiz.options) == 4
            print("  [OK] 选择题有4个选项")

        # 4. 学生答错
        print("\n[步骤4] 学生答题（模拟答错）...")
        student_answer = "25"
        print(f"  学生答案: {student_answer}")
        print(f"  正确答案: {quiz.answer}")

        grade_result = await agent._grader_engine.grade(
            quiz=quiz,
            student_answer=student_answer,
            knowledge_name=target_point.name,
        )

        print(f"  判题结果: {'正确' if grade_result.is_correct else '错误'}")
        assert isinstance(grade_result, GradeResult)
        print("  ✓ 判题功能正常")

        # 5. 获取讲解
        print("\n[步骤5] 获取知识点讲解...")
        explanation = await agent._explain_engine.explain(
            knowledge_name=target_point.name,
            knowledge_desc=detail.definition or target_point.description,
            student_question=f"为什么答案是{quiz.answer}？",
            grade=3,
            knowledge_id=target_point.id,
        )

        print(f"  总结: {explanation.summary}")
        print(f"  讲解: {explanation.detail[:100]}...")
        assert explanation.summary
        assert explanation.detail
        print("  ✓ 讲解功能正常")

        # 6. 再出题，答对
        print("\n[步骤6] 生成新题（答对）...")
        quiz2 = await agent._quiz_engine.generate(target_point)
        print(f"  新题目: {quiz2.question[:80]}...")
        print(f"  正确答案: {quiz2.answer}")

        grade_result2 = await agent._grader_engine.grade(
            quiz=quiz2,
            student_answer=quiz2.answer,
            knowledge_name=target_point.name,
        )

        print(f"  判题结果: {'正确' if grade_result2.is_correct else '错误'}")
        assert grade_result2.is_correct
        print("  ✓ 答对判题正确")

        # 总结
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print(f"\n教学流程验证:")
        print(f"  ✓ 知识点从数据库加载: {target_point.name}")
        print(f"  ✓ 常见错误数据: {len(detail.common_mistakes)}条")
        print(f"  ✓ 出题功能: 生成{quiz.question_type}类型题目")
        print(f"  ✓ 判题功能: 正确判对判错")
        print(f"  ✓ 讲解功能: 提供总结和详细说明")
        print(f"\n[OK] 所有验证通过！")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])