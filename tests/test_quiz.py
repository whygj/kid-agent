"""测试出题引擎"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from src.engine.quiz import Quiz, QuizEngine, QuizGenerationResult
from src.knowledge.math_g3g5 import get_point_by_id, KnowledgePoint, Difficulty


@pytest.fixture
def sample_point():
    """示例知识点"""
    return KnowledgePoint(
        id="test_001",
        name="测试知识点",
        grade=3,
        difficulty=Difficulty.EASY,
        description="这是一个测试知识点",
        examples=["1+1=2"],
        common_mistakes=["计算错误"],
    )


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
def quiz_engine(mock_client):
    """创建出题引擎（使用 mock 客户端）"""
    with patch("src.engine.quiz.get_config") as mock_config:
        config = Mock()
        config.llm.model = "test-model"
        config.get_client.return_value = mock_client
        mock_config.return_value = config

        # Mock 返回值
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "question_type": "choice",
            "question": "5 × 6 = ?",
            "options": ["25", "30", "35", "40"],
            "answer": "30",
            "explanation": "5乘6等于30"
        })
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        engine = QuizEngine()
        yield engine


class TestQuiz:
    """测试 Quiz 数据类"""

    def test_quiz_creation(self):
        """测试创建题目"""
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
        assert quiz.explanation == "1加1等于2"
        assert quiz.question_type == "choice"

    def test_quiz_defaults(self):
        """测试题目默认值"""
        quiz = Quiz(question="1+1=?")

        assert quiz.question == "1+1=?"
        assert quiz.answer == ""
        assert quiz.options is None
        assert quiz.explanation == ""
        assert quiz.question_type == "free"


class TestQuizEngine:
    """测试出题引擎"""

    def test_quiz_engine_initialization(self, quiz_engine):
        """测试出题引擎初始化"""
        assert quiz_engine._prompt_template is not None

    def test_load_prompt_template(self):
        """测试加载 prompt 模板"""
        with patch("src.engine.quiz.get_config"):
            engine = QuizEngine()
            template = engine._load_prompt_template()
            assert "{name}" in template
            assert "{grade}" in template
            assert "{difficulty}" in template
            assert "{description}" in template

    @pytest.mark.asyncio
    async def test_generate_quiz(self, quiz_engine, sample_point):
        """测试生成题目"""
        quiz = await quiz_engine.generate(sample_point)

        assert isinstance(quiz, Quiz)
        assert quiz.question_type == "choice"
        assert quiz.question == "5 × 6 = ?"
        assert quiz.answer == "30"
        assert len(quiz.options) == 4

    @pytest.mark.asyncio
    async def test_generate_quiz_with_difficulty(self, quiz_engine, sample_point):
        """测试指定难度生成题目"""
        quiz = await quiz_engine.generate(sample_point, difficulty=3)

        assert isinstance(quiz, Quiz)

    @pytest.mark.asyncio
    async def test_generate_quiz_with_history(self, quiz_engine, sample_point):
        """测试带历史记录生成题目"""
        history = [
            {"is_correct": True},
            {"is_correct": False},
            {"is_correct": True},
        ]

        quiz = await quiz_engine.generate(sample_point, student_history=history)

        assert isinstance(quiz, Quiz)

    def test_parse_quiz_result(self, quiz_engine, sample_point):
        """测试解析题目结果"""
        content = json.dumps({
            "question_type": "choice",
            "question": "5 × 6 = ?",
            "options": ["25", "30", "35", "40"],
            "answer": "30",
            "explanation": "5乘6等于30"
        })

        quiz = quiz_engine._parse_quiz_result(content, sample_point)

        assert quiz.question_type == "choice"
        assert quiz.question == "5 × 6 = ?"
        assert quiz.answer == "30"

    def test_parse_quiz_result_fallback(self, quiz_engine, sample_point):
        """测试解析题目结果降级处理"""
        # 无效 JSON
        content = "这是普通的文本题目"

        quiz = quiz_engine._parse_quiz_result(content, sample_point)

        assert quiz.question == content
        assert quiz.answer == "（请老师批改）"
        assert quiz.question_type == "free"

    def test_parse_quiz_result_json_error(self, quiz_engine, sample_point):
        """测试 JSON 解析错误"""
        content = '{"invalid": json'

        quiz = quiz_engine._parse_quiz_result(content, sample_point)

        assert quiz.question == content
        assert quiz.answer == "（请老师批改）"

    def test_parse_quiz_result_with_missing_fields(self, quiz_engine, sample_point):
        """测试解析缺少字段的 JSON"""
        content = json.dumps({
            "question": "5 × 6 = ?",
            "answer": "30",
        })

        quiz = quiz_engine._parse_quiz_result(content, sample_point)

        assert quiz.question == "5 × 6 = ?"
        assert quiz.answer == "30"
        assert quiz.options is None  # 缺少字段
        assert quiz.question_type == "free"  # 默认值

    @pytest.mark.asyncio
    async def test_generate_batch(self, quiz_engine, sample_point):
        """测试批量生成题目"""
        quizzes = await quiz_engine.generate_batch(sample_point, count=3)

        assert len(quizzes) == 3
        assert all(isinstance(q, Quiz) for q in quizzes)


class TestQuizGenerationResult:
    """测试出题结果"""

    def test_quiz_generation_result(self, sample_point, sample_quiz):
        """测试出题结果数据类"""
        result = QuizGenerationResult(
            quiz=sample_quiz,
            point_id=sample_point.id,
            difficulty=2,
        )

        assert result.quiz == sample_quiz
        assert result.point_id == sample_point.id
        assert result.difficulty == 2


class TestGetPointById:
    """测试获取知识点"""

    def test_get_existing_point(self):
        """测试获取存在的知识点"""
        point = get_point_by_id("math_g3_001")
        assert point is not None
        assert point.name == "乘法口诀"
        assert point.grade == 3

    def test_get_nonexistent_point(self):
        """测试获取不存在的知识点"""
        point = get_point_by_id("nonexistent_id")
        assert point is None


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_quiz_generation_flow(self):
        """测试完整出题流程"""
        with patch("openai.AsyncOpenAI") as mock_class:
            client = Mock()
            mock_class.return_value = client

            # Mock 响应
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "question_type": "calculation",
                "question": "23 × 4 = ?",
                "answer": "92",
                "explanation": "20×4=80, 3×4=12, 80+12=92"
            })
            client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch("src.engine.quiz.get_config") as mock_config:
                config = Mock()
                config.llm.model = "test-model"
                config.get_client.return_value = client
                mock_config.return_value = config

                engine = QuizEngine()
                point = get_point_by_id("math_g3_002")  # 一位数乘两位数

                quiz = await engine.generate(point)

                assert quiz.question_type == "calculation"
                assert quiz.question == "23 × 4 = ?"
                assert quiz.answer == "92"

    @pytest.mark.asyncio
    async def test_quiz_generation_with_different_difficulties(self):
        """测试不同难度的出题"""
        with patch("openai.AsyncOpenAI") as mock_class:
            client = Mock()
            mock_class.return_value = client

            difficulties = [1, 2, 3, 4, 5]

            for difficulty in difficulties:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = json.dumps({
                    "question_type": "choice",
                    "question": f"难度{difficulty}的题目",
                    "answer": "30",
                    "options": ["25", "30", "35", "40"]
                })
                client.chat.completions.create = AsyncMock(return_value=mock_response)

                with patch("src.engine.quiz.get_config") as mock_config:
                    config = Mock()
                    config.llm.model = "test-model"
                    config.get_client.return_value = client
                    mock_config.return_value = config

                    engine = QuizEngine()
                    point = get_point_by_id("math_g3_001")

                    quiz = await engine.generate(point, difficulty=difficulty)

                    assert isinstance(quiz, Quiz)

    @pytest.mark.asyncio
    async def test_quiz_generation_with_student_history(self):
        """测试根据学生历史记录生成题目"""
        with patch("openai.AsyncOpenAI") as mock_class:
            client = Mock()
            mock_class.return_value = client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "question_type": "free",
                "question": "根据你的表现出的题目",
                "answer": "10",
            })
            client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch("src.engine.quiz.get_config") as mock_config:
                config = Mock()
                config.llm.model = "test-model"
                config.get_client.return_value = client
                mock_config.return_value = config

                engine = QuizEngine()
                point = get_point_by_id("math_g3_001")

                # 学生正确率 66%
                history = [
                    {"is_correct": True},
                    {"is_correct": True},
                    {"is_correct": False},
                ]

                quiz = await engine.generate(point, student_history=history)

                assert isinstance(quiz, Quiz)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
