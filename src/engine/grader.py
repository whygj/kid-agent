"""批改引擎 - 调用LLM批改学生答案"""

import asyncio
import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from src.config.settings import get_config
from src.engine.quiz import Quiz


@dataclass
class GradeResult:
    """批改结果"""
    is_correct: bool
    feedback: str  # 反馈（鼓励或提示）
    error_reason: str | None = None  # 错误原因（如果错误）
    hint: str | None = None  # 提示（如果错误）


class GraderEngine:
    """批改引擎"""

    def __init__(self):
        """初始化批改引擎"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None

    async def grade(
        self,
        quiz: Quiz,
        student_answer: str,
        knowledge_name: str = "",
    ) -> GradeResult:
        """批改学生答案"""
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        prompt = self._build_grading_prompt(quiz, student_answer, knowledge_name)

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": """你是温柔的小学数学老师，批改学生作业时：
1. 如果正确，给正面鼓励和表扬
2. 如果错误，不给正确答案，先给提示引导学生自己思考
3. 用亲切、鼓励的语气，像朋友不像老师
4. 适度使用emoji
请用JSON格式返回批改结果。""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        content = response.choices[0].message.content
        return self._parse_grading_result(content)

    def _build_grading_prompt(
        self,
        quiz: Quiz,
        student_answer: str,
        knowledge_name: str,
    ) -> str:
        """构建批改prompt"""
        prompt_parts = [
            f"题目：{quiz.question}",
            f"正确答案：{quiz.answer}",
            f"学生答案：{student_answer}",
        ]

        if quiz.options:
            prompt_parts.append(f"选项：{', '.join(quiz.options)}")

        if knowledge_name:
            prompt_parts.append(f"知识点：{knowledge_name}")

        prompt_parts.append("\n请判断学生的答案是否正确，并给出反馈。")

        return "\n".join(prompt_parts)

    def _parse_grading_result(self, content: str) -> GradeResult:
        """解析LLM返回的批改结果"""
        # 尝试提取JSON
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return GradeResult(
                    is_correct=data.get("is_correct", False),
                    feedback=data.get("feedback", content),
                    error_reason=data.get("error_reason"),
                    hint=data.get("hint"),
                )
            except json.JSONDecodeError:
                pass

        # 简单判断：包含"正确""对的"等关键词
        is_correct = any(
            kw in content for kw in ["正确", "对的", "太棒了", "完全正确", "很好"]
        )

        return GradeResult(
            is_correct=is_correct,
            feedback=content,
        )

    async def grade_batch(
        self,
        quizzes_and_answers: list[tuple[Quiz, str]],
    ) -> list[GradeResult]:
        """批量批改"""
        tasks = [self.grade(q, a) for q, a in quizzes_and_answers]
        return await asyncio.gather(*tasks)


# 默认批改引擎实例
_default_engine: GraderEngine | None = None


async def get_grader_engine() -> GraderEngine:
    """获取默认批改引擎实例（懒加载）"""
    global _default_engine
    if _default_engine is None:
        _default_engine = GraderEngine()
    return _default_engine


