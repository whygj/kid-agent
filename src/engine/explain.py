"""讲解引擎 - 调用LLM生成讲解内容"""

from dataclasses import dataclass

from openai import AsyncOpenAI

from src.config.settings import get_config


@dataclass
class Explanation:
    """讲解内容"""
    summary: str  # 简短总结
    detail: str  # 详细讲解
    examples: list[str]  # 例题
    tips: str  # 小技巧


class ExplainEngine:
    """讲解引擎"""

    def __init__(self):
        """初始化讲解引擎"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None

    async def explain(
        self,
        knowledge_name: str,
        knowledge_desc: str,
        student_question: str = "",
        grade: int = 3,
    ) -> Explanation:
        """生成讲解内容"""
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        prompt = self._build_explain_prompt(
            knowledge_name,
            knowledge_desc,
            student_question,
            grade,
        )

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": f"""你是亲切的小学{grade}年级数学老师，叫小助手。你给孩子讲解时：
1. 用简单易懂的语言，像讲故事一样
2. 多举生活中的例子
3. 一步步引导，让孩子能跟上
4. 用亲切、鼓励的语气
5. 适度使用emoji，增加趣味性
6. 孩子听不懂就换一种方式解释

请用JSON格式返回讲解内容：
{{
    "summary": "一句话总结（不超过50字）",
    "detail": "详细讲解内容",
    "examples": ["例题1", "例题2"],
    "tips": "记忆小技巧"
}}
""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        return self._parse_explanation(content, knowledge_name)

    async def explain_quiz(
        self,
        quiz_question: str,
        correct_answer: str,
        student_wrong_answer: str,
        knowledge_name: str,
    ) -> Explanation:
        """讲解一道错题"""
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        prompt = f"""题目：{quiz_question}
正确答案：{correct_answer}
学生错误答案：{student_wrong_answer}
知识点：{knowledge_name}

请讲解这道题，帮助学生理解为什么正确答案是{correct_answer}，并且引导学生找出自己错在哪里。"""

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {
                    "role": "system",
                    "content": """你是亲切的小学数学老师，讲解错题时：
1. 不直接给答案，先引导学生思考
2. 找出学生错误的原因
3. 用温和的语气，不批评孩子
4. 给出清晰的解题步骤
5. 适度使用emoji

请用JSON格式返回讲解内容：
{{
    "summary": "一句话总结错误原因",
    "detail": "详细讲解和正确解题步骤",
    "examples": ["类似例题"],
    "tips": "解题小技巧"
}}
""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=800,
        )

        content = response.choices[0].message.content
        return self._parse_explanation(content, knowledge_name)

    def _build_explain_prompt(
        self,
        knowledge_name: str,
        knowledge_desc: str,
        student_question: str,
        grade: int,
    ) -> str:
        """构建讲解prompt"""
        parts = [
            f"知识点：{knowledge_name}",
            f"知识点描述：{knowledge_desc}",
        ]

        if student_question:
            parts.append(f"学生问题：{student_question}")

        parts.append("\n请给小朋友讲解这个知识点。")

        return "\n\n".join(parts)

    def _parse_explanation(self, content: str, fallback_name: str) -> Explanation:
        """解析LLM返回的讲解内容"""
        import json
        import re

        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return Explanation(
                    summary=data.get("summary", content[:50]),
                    detail=data.get("detail", content),
                    examples=data.get("examples", []),
                    tips=data.get("tips", ""),
                )
            except json.JSONDecodeError:
                pass

        return Explanation(
            summary=content[:50],
            detail=content,
            examples=[],
            tips="",
        )


# 默认讲解引擎实例
_default_engine: ExplainEngine | None = None


async def get_explain_engine() -> ExplainEngine:
    """获取默认讲解引擎实例（懒加载）"""
    global _default_engine
    if _default_engine is None:
        _default_engine = ExplainEngine()
    return _default_engine