"""出题引擎 - 调用LLM生成数学题"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from src.config.settings import get_config
from src.knowledge.loader import KnowledgePoint, get_points_by_grade
from src.knowledge.service import get_knowledge_service


@dataclass
class Quiz:
    """生成的题目"""
    question: str
    options: list[str] | None = None
    answer: str = ""  # 标准答案
    explanation: str = ""  # 答案解释
    question_type: str = "free"  # free, choice, calculation


@dataclass
class QuizGenerationResult:
    """出题结果"""
    quiz: Quiz
    point_id: str
    difficulty: int


class QuizEngine:
    """出题引擎"""

    def __init__(self):
        """初始化出题引擎"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None
        self._prompt_template = self._load_prompt_template()
        self._knowledge_service = get_knowledge_service()

    def _load_prompt_template(self) -> str:
        """加载出题prompt模板"""
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "quiz_gen.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """你是小学数学老师，请根据知识点生成适合学生的题目。

知识点：{name}
年级：{grade}
难度：{difficulty}（1-5级，1最简单）
描述：{description}

要求：
1. 题目类型可以是：填空题、选择题、计算题、应用题
2. 题目要有趣味性，贴近生活
3. 难度要符合要求
4. 如果是选择题，提供4个选项
5. 不要直接给答案，只输出题目

请用JSON格式返回：
{{
    "question_type": "free/choice/calculation",
    "question": "题目内容",
    "options": ["选项A", "选项B", "选项C", "选项D"]（选择题才需要），
    "answer": "标准答案",
    "explanation": "答案解释"
}}
"""

    async def generate(
        self,
        knowledge_point: KnowledgePoint,
        difficulty: int | None = None,
        student_history: list[Any] | None = None,
        use_common_mistakes: bool = True,
    ) -> Quiz:
        """生成题目

        Args:
            knowledge_point: 知识点对象
            difficulty: 难度等级，默认使用知识点的难度
            student_history: 学生历史记录
            use_common_mistakes: 是否使用常见错误生成干扰项
        """
        if difficulty is None:
            difficulty = knowledge_point.difficulty.value if hasattr(knowledge_point.difficulty, 'value') else int(knowledge_point.difficulty)

        # 从知识库获取详细信息
        description = knowledge_point.description or ""
        definition = getattr(knowledge_point, 'definition', '') or description
        examples = getattr(knowledge_point, 'examples', []) or []

        # 获取常见错误（用于生成干扰项）
        common_mistakes = []
        if use_common_mistakes:
            common_mistakes = self._knowledge_service.get_common_mistakes(knowledge_point.id)

        # 构建prompt
        prompt_parts = [
            f"知识点：{knowledge_point.name}",
            f"年级：{knowledge_point.grade}",
            f"难度：{difficulty}（1-5级，1最简单）",
            f"描述：{description}",
        ]

        if definition and definition != description:
            prompt_parts.append(f"定义：{definition}")

        if examples:
            prompt_parts.append(f"示例：{'; '.join(examples[:2])}")

        if common_mistakes:
            prompt_parts.append(f"常见错误：{'; '.join(common_mistakes[:3])}")

        prompt = "\n".join(prompt_parts) + """

要求：
1. 题目类型可以是：填空题、选择题、计算题、应用题
2. 题目要有趣味性，贴近生活
3. 难度要符合要求
4. 如果是选择题，提供4个选项，其中可以参考常见错误设置干扰项
5. 不要直接给答案，只输出题目

请用JSON格式返回：
{{
    "question_type": "free/choice/calculation",
    "question": "题目内容",
    "options": ["选项A", "选项B", "选项C", "选项D"]（选择题才需要），
    "answer": "标准答案",
    "explanation": "答案解释"
}}
"""

        # 添加历史参考
        if student_history:
            correct_count = sum(1 for h in student_history if h.get('is_correct'))
            accuracy = correct_count / len(student_history) if student_history else 0
            prompt += f"\n\n学生最近做过：{len(student_history)}道题，正确率{accuracy:.1%}"

        # 调用LLM
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {"role": "system", "content": "你是专业的数学出题老师，请用JSON格式返回题目。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        # 解析结果
        content = response.choices[0].message.content
        return self._parse_quiz_result(content, knowledge_point)

    def _parse_quiz_result(self, content: str, knowledge_point: KnowledgePoint) -> Quiz:
        """解析LLM返回的题目结果"""
        import json
        import re

        # 提取JSON部分
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return Quiz(
                    question=data.get("question", content),
                    options=data.get("options"),
                    answer=data.get("answer", ""),
                    explanation=data.get("explanation", ""),
                    question_type=data.get("question_type", "free"),
                )
            except json.JSONDecodeError:
                pass

        # 降级处理
        return Quiz(
            question=content,
            options=None,
            answer="（请老师批改）",
            explanation="",
            question_type="free",
        )

    async def generate_batch(
        self,
        knowledge_point: KnowledgePoint,
        count: int = 5,
    ) -> list[Quiz]:
        """批量生成题目"""
        tasks = [self.generate(knowledge_point) for _ in range(count)]
        return await asyncio.gather(*tasks)


# 默认出题引擎实例
_default_engine: QuizEngine | None = None


async def get_quiz_engine() -> QuizEngine:
    """获取默认出题引擎实例（懒加载）"""
    global _default_engine
    if _default_engine is None:
        _default_engine = QuizEngine()
    return _default_engine