"""测试批改引擎"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from src.engine.grader import GraderEngine, GradeResult
from src.engine.quiz import Quiz


@pytest.fixture
def sample_quiz():
    """示例题目"""
    return Quiz(
        question="5 × 6 = ?",
        options=["25", "30", "35", "40"],
        answer="30",
        explanation="5乘6等于30",
        question_type="choice",
    )


@pytest.fixture
def mock_client():
    """Mock OpenAI 客户端"""
    with patch("openai.AsyncOpenAI") as mock_class:
        client = Mock()
        mock_class.return_value = client
        yield client


@pytest.fixture
def grader_engine(mock_client):
    """创建批改引擎（使用 mock 客户端）"""
    with patch("src.engine.grader.get_config") as mock_config:
        config = Mock()
        config.llm.model = "test-model"
        config.get_client.return_value = mock_client
        mock_config.return_value = config

        engine = GraderEngine()
        yield engine


class TestGradeResult:
    """测试批改结果数据类"""

    def test_grade_result_correct(self):
        """测试正确批改结果"""
        result = GradeResult(
            is_correct=True,
            feedback="太棒了！答对了！",
            error_reason=None,
            hint=None,
        )

        assert result.is_correct is True
        assert result.feedback == "太棒了！答对了！"
        assert result.error_reason is None
        assert result.hint is None

    def test_grade_result_wrong(self):
        """测试错误批改结果"""
        result = GradeResult(
            is_correct=False,
            feedback="不太对哦，再想想？",
            error_reason="计算错误",
            hint="检查一下乘法口诀",
        )

        assert result.is_correct is False
        assert result.error_reason == "计算错误"
        assert result.hint == "检查一下乘法口诀"

    def test_grade_result_minimal(self):
        """测试最小批改结果"""
        result = GradeResult(is_correct=True, feedback="正确！")

        assert result.is_correct is True
        assert result.feedback == "正确！"


class TestGraderEngine:
    """测试批改引擎"""

    def test_grader_engine_initialization(self, grader_engine):
        """测试批改引擎初始化"""
        assert grader_engine.config is not None
        assert grader_engine.client is None

    def test_build_grading_prompt(self, grader_engine, sample_quiz):
        """测试构建批改 prompt"""
        prompt = grader_engine._build_grading_prompt(
            sample_quiz,
            "30",
            "乘法口诀"
        )

        assert "题目：5 × 6 = ?" in prompt
        assert "正确答案：30" in prompt
        assert "学生答案：30" in prompt
        assert "知识点：乘法口诀" in prompt

    def test_build_grading_prompt_with_options(self, grader_engine, sample_quiz):
        """测试构建带选项的批改 prompt"""
        prompt = grader_engine._build_grading_prompt(
            sample_quiz,
            "35",
            ""
        )

        assert "选项：" in prompt
        assert "25, 30, 35, 40" in prompt

    @pytest.mark.asyncio
    async def test_grade_correct_answer(self, grader_engine, sample_quiz, mock_client):
        """测试批改正确答案"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "太棒了！答对了！🌟",
            "error_reason": None,
            "hint": None
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(sample_quiz, "30", "乘法口诀")

        assert result.is_correct is True
        assert "太棒了" in result.feedback or "正确" in result.feedback
        assert result.error_reason is None
        assert result.hint is None

    @pytest.mark.asyncio
    async def test_grade_wrong_answer(self, grader_engine, sample_quiz, mock_client):
        """测试批改错误答案"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": False,
            "feedback": "不太对哦，再想想？5乘6应该是多少？💭",
            "error_reason": "计算错误",
            "hint": "背一下口诀：五六？"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(sample_quiz, "35", "乘法口诀")

        assert result.is_correct is False
        assert "再想想" in result.feedback or "提示" in result.feedback
        assert result.error_reason == "计算错误"
        assert result.hint == "背一下口诀：五六？"

    @pytest.mark.asyncio
    async def test_grade_without_knowledge_name(self, grader_engine, sample_quiz, mock_client):
        """测试不带知识点名称的批改"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "正确！"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(sample_quiz, "30")

        assert result.is_correct is True

    def test_parse_grading_result(self, grader_engine):
        """测试解析批改结果"""
        content = json.dumps({
            "is_correct": True,
            "feedback": "太棒了！",
            "error_reason": None,
            "hint": None
        })

        result = grader_engine._parse_grading_result(content)

        assert result.is_correct is True
        assert result.feedback == "太棒了！"
        assert result.error_reason is None
        assert result.hint is None

    def test_parse_grading_result_fallback(self, grader_engine):
        """测试解析批改结果降级处理"""
        # 无 JSON，但包含正确关键词
        content = "太棒了！完全正确！"

        result = grader_engine._parse_grading_result(content)

        assert result.is_correct is True
        assert result.feedback == content

    def test_parse_grading_result_wrong_fallback(self, grader_engine):
        """测试解析错误答案降级处理"""
        # 无 JSON，不包含正确关键词
        content = "不太对哦，再想想"

        result = grader_engine._parse_grading_result(content)

        assert result.is_correct is False
        assert result.feedback == content

    def test_parse_grading_result_json_error(self, grader_engine):
        """测试 JSON 解析错误"""
        content = '{"invalid": json'

        result = grader_engine._parse_grading_result(content)

        # 降级处理：不包含正确关键词
        assert result.is_correct is False

    def test_parse_grading_result_with_missing_fields(self, grader_engine):
        """测试解析缺少字段的 JSON"""
        content = json.dumps({
            "is_correct": True,
            "feedback": "正确！"
        })

        result = grader_engine._parse_grading_result(content)

        assert result.is_correct is True
        assert result.feedback == "正确！"
        assert result.error_reason is None  # 缺少字段
        assert result.hint is None

    @pytest.mark.asyncio
    async def test_grade_batch(self, grader_engine, sample_quiz, mock_client):
        """测试批量批改"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "正确！"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        results = await grader_engine.grade_batch([
            (sample_quiz, "30"),
            (sample_quiz, "30"),
            (sample_quiz, "30"),
        ])

        assert len(results) == 3
        assert all(r.is_correct for r in results)

    @pytest.mark.asyncio
    async def test_grade_batch_mixed(self, grader_engine, sample_quiz, mock_client):
        """测试混合答案的批量批改"""
        correct_response = Mock()
        correct_response.choices = [Mock()]
        correct_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "正确！"
        })

        wrong_response = Mock()
        wrong_response.choices = [Mock()]
        wrong_response.choices[0].message.content = json.dumps({
            "is_correct": False,
            "feedback": "错误！"
        })

        call_count = 0
        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return correct_response if call_count % 2 == 1 else wrong_response

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)

        results = await grader_engine.grade_batch([
            (sample_quiz, "30"),
            (sample_quiz, "35"),
        ])

        assert len(results) == 2
        assert results[0].is_correct is True
        assert results[1].is_correct is False


class TestDifferentQuizTypes:
    """测试不同类型题目的批改"""

    @pytest.mark.asyncio
    async def test_grade_choice_quiz(self, grader_engine, mock_client):
        """测试批改选择题"""
        quiz = Quiz(
            question="5 × 6 = ?",
            options=["25", "30", "35", "40"],
            answer="30",
            question_type="choice",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "选对了！"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(quiz, "30")

        assert result.is_correct is True

    @pytest.mark.asyncio
    async def test_grade_calculation_quiz(self, grader_engine, mock_client):
        """测试批改计算题"""
        quiz = Quiz(
            question="23 × 4 = ?",
            answer="92",
            question_type="calculation",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": False,
            "feedback": "再算一下",
            "error_reason": "计算错误"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(quiz, "85")

        assert result.is_correct is False

    @pytest.mark.asyncio
    async def test_grade_free_response_quiz(self, grader_engine, mock_client):
        """测试批改自由作答题"""
        quiz = Quiz(
            question="解释什么是乘法",
            question_type="free",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "解释得很好！"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(
            quiz,
            "乘法是重复相加的方法，比如3×5就是把5加3次"
        )

        assert result.is_correct is True


class TestEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_grade_empty_answer(self, grader_engine, sample_quiz, mock_client):
        """测试批改空答案"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": False,
            "feedback": "请提供答案"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(sample_quiz, "")

        assert result.is_correct is False

    @pytest.mark.asyncio
    async def test_grade_whitespace_answer(self, grader_engine, sample_quiz, mock_client):
        """测试批改只有空格的答案"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": False,
            "feedback": "请提供有效答案"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await grader_engine.grade(sample_quiz, "   ")

        assert result.is_correct is False

    @pytest.mark.asyncio
    async def test_grade_numeric_string_answer(self, grader_engine, sample_quiz, mock_client):
        """测试批改数字字符串答案"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_correct": True,
            "feedback": "正确！"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # 答案是字符串形式的数字
        result = await grader_engine.grade(sample_quiz, "30")

        assert result.is_correct is True


class TestKeywordMatching:
    """测试关键词匹配降级处理"""

    def test_correct_keywords(self):
        """测试正确答案关键词"""
        test_cases = [
            ("太棒了！", True),
            ("完全正确", True),
            ("答对了", True),
            ("对的", True),
            ("很好", True),
        ]

        for feedback, expected in test_cases:
            is_correct = any(
                kw in feedback for kw in ["正确", "对的", "太棒了", "完全正确", "很好"]
            )
            assert is_correct == expected, f"Failed for: {feedback}"

    def test_wrong_keywords(self):
        """测试错误答案判断"""
        test_cases = [
            ("再想想", False),
            ("不对哦", False),
            ("不太对", False),
            ("错误", False),
        ]

        for feedback in test_cases:
            is_correct = any(
                kw in feedback for kw in ["正确", "对的", "太棒了", "完全正确", "很好"]
            )
            assert is_correct is False, f"Failed for: {feedback}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
