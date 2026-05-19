"""测试批改引擎"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.engine.grader import GraderEngine, GradeResult
from src.engine.quiz import Quiz


@pytest.fixture
def mock_client():
    """Mock OpenAI client"""
    with patch("src.config.settings.get_config") as mock_config:
        config = MagicMock()
        config.llm.model = "test-model"
        mock_config.return_value = config

        with patch("openai.AsyncOpenAI") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client


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


@pytest.mark.asyncio
async def test_grade_correct_answer(mock_client, sample_quiz):
    """测试批改正确答案"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''{
        "is_correct": true,
        "feedback": "太棒了！答对了！🌟",
        "error_reason": null,
        "hint": null
    }'''
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = GraderEngine()
    result = await engine.grade(sample_quiz, "30", "乘法口诀")

    assert result.is_correct is True
    assert "太棒了" in result.feedback or "正确" in result.feedback
    assert result.error_reason is None


@pytest.mark.asyncio
async def test_grade_wrong_answer(mock_client, sample_quiz):
    """测试批改错误答案"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''{
        "is_correct": false,
        "feedback": "不太对哦，再想想？5乘6应该是多少？💭",
        "error_reason": "计算错误",
        "hint": "背一下口诀：五六？"
    }'''
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = GraderEngine()
    result = await engine.grade(sample_quiz, "35", "乘法口诀")

    assert result.is_correct is False
    assert "再想想" in result.feedback or "提示" in result.feedback
    assert result.hint is not None


@pytest.mark.asyncio
async def test_grade_with_knowledge_name(mock_client, sample_quiz):
    """测试带知识点名称的批改"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"is_correct": true, "feedback": "正确！"}'
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = GraderEngine()
    result = await engine.grade(sample_quiz, "30", knowledge_name="乘法口诀")

    assert result.is_correct is True


def test_grade_result_dataclass():
    """测试GradeResult数据类"""
    result = GradeResult(
        is_correct=True,
        feedback="太棒了！",
        error_reason=None,
        hint=None,
    )

    assert result.is_correct is True
    assert result.feedback == "太棒了！"
    assert result.error_reason is None

    result = GradeResult(
        is_correct=False,
        feedback="再想想",
        error_reason="计算错误",
        hint="检查一下",
    )

    assert result.is_correct is False
    assert result.error_reason == "计算错误"
    assert result.hint == "检查一下"


@pytest.mark.asyncio
async def test_grade_batch(mock_client, sample_quiz):
    """测试批量批改"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"is_correct": true, "feedback": "正确！"}'
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = GraderEngine()
    results = await engine.grade_batch([(sample_quiz, "30"), (sample_quiz, "30")])

    assert len(results) == 2
    assert all(r.is_correct for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])