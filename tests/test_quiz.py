"""测试出题引擎"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.engine.quiz import Quiz, QuizEngine
from src.knowledge.math_g3g5 import get_point_by_id


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


@pytest.mark.asyncio
async def test_generate_quiz(mock_client):
    """测试生成题目"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''{
        "question_type": "choice",
        "question": "5 × 6 = ?",
        "options": ["25", "30", "35", "40"],
        "answer": "30",
        "explanation": "5乘6等于30"
    }'''
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = QuizEngine()
    point = get_point_by_id("math_g3_001")

    quiz = await engine.generate(point)

    assert isinstance(quiz, Quiz)
    assert quiz.question_type == "choice"
    assert quiz.question == "5 × 6 = ?"
    assert quiz.answer == "30"
    assert len(quiz.options) == 4


@pytest.mark.asyncio
async def test_generate_calculation_quiz(mock_client):
    """测试生成计算题"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''{
        "question_type": "calculation",
        "question": "23 × 4 = ?",
        "answer": "92",
        "explanation": "20×4=80, 3×4=12, 80+12=92"
    }'''
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    engine = QuizEngine()
    point = get_point_by_id("math_g3_002")

    quiz = await engine.generate(point)

    assert isinstance(quiz, Quiz)
    assert quiz.question_type == "calculation"
    assert quiz.answer == "92"


def test_quiz_dataclass():
    """测试Quiz数据类"""
    quiz = Quiz(
        question="1+1=?",
        options=["1", "2", "3", "4"],
        answer="2",
        explanation="1加1等于2",
        question_type="choice",
    )

    assert quiz.question == "1+1=?"
    assert quiz.answer == "2"
    assert quiz.options == ["1", "2", "3", "4"]


def test_get_point_by_id():
    """测试获取知识点"""
    point = get_point_by_id("math_g3_001")
    assert point is not None
    assert point.name == "乘法口诀"
    assert point.grade == 3

    point = get_point_by_id("nonexistent")
    assert point is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])