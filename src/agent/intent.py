"""意图识别 - 使用LLM识别用户意图"""

from dataclasses import dataclass
from typing import Literal

from openai import AsyncOpenAI

from src.config.settings import get_config


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: Literal["quiz", "answer", "explain", "diagnose", "plan", "report", "chat"]
    confidence: float  # 0.0-1.0


class IntentRecognizer:
    """意图识别器"""

    INTENT_PROMPT = """你是数学教学助手的意图识别器。分析用户输入，判断用户的意图。

可能的意图：
- quiz: 用户想做题（如"出题"、"下一题"、"开始"）
- answer: 用户在回答题目（如数字、算式、选择题选项）
- explain: 用户想了解某个知识点（如"讲解"、"为什么"、"不懂"）
- diagnose: 用户想查看学习情况（如"诊断"、"分析"、"看看"）
- plan: 用户想查看学习计划（如"学习计划"、"路线"、"学什么"）
- report: 用户想查看学习报告（如"学习报告"、"成绩"、"总结"）
- chat: 普通聊天（打招呼、闲聊、其他）

请用JSON格式返回，格式如下：
{{"intent": "意图类型", "confidence": 0.0-1.0}}

用户输入：{message}
当前状态：{state}
"""

    FALLBACK_KEYWORDS = {
        "quiz": ["出题", "题目", "做道题", "开始", "next", "下一题", "再来一题"],
        "answer": ["答案", "答", "答案是", "选择", "是"],
        "explain": ["讲解", "解释", "为什么", "不懂", "教我", "怎么"],
        "diagnose": ["诊断", "分析", "看看", "情况", "复习", "统计"],
        "plan": ["学习计划", "计划", "路线", "学什么", "目标"],
        "report": ["学习报告", "报告", "成绩", "总结", "表现"],
    }

    def __init__(self):
        """初始化意图识别器"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None

    async def recognize(
        self,
        message: str,
        state: str = "idle",
    ) -> IntentResult:
        """识别用户意图"""
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

        # 尝试用LLM识别
        try:
            prompt = self.INTENT_PROMPT.format(message=message, state=state)
            response = await self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是意图识别器，只返回JSON格式的intent和confidence。"
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=100,
            )

            import json
            import re

            content = response.choices[0].message.content
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                intent = data.get("intent", "chat")
                confidence = float(data.get("confidence", 0.5))

                # 验证intent是否有效
                valid_intents = ["quiz", "answer", "explain", "diagnose", "plan", "report", "chat"]
                if intent not in valid_intents:
                    intent = "chat"

                return IntentResult(intent=intent, confidence=min(max(confidence, 0.0), 1.0))
        except Exception:
            pass

        # Fallback到关键词匹配
        return self._fallback_recognize(message, state)

    def _fallback_recognize(self, message: str, state: str) -> IntentResult:
        """降级意图识别（关键词匹配）"""
        message_lower = message.strip().lower()

        for intent, keywords in self.FALLBACK_KEYWORDS.items():
            if any(word in message_lower for word in keywords):
                return IntentResult(intent=intent, confidence=0.7)

        # 如果在做题状态且消息不为空，可能是在回答
        if state == "quiz" and message.strip():
            return IntentResult(intent="answer", confidence=0.5)

        return IntentResult(intent="chat", confidence=0.4)


# 默认意图识别器实例
_default_recognizer: IntentRecognizer | None = None


def get_intent_recognizer() -> IntentRecognizer:
    """获取默认意图识别器实例（懒加载）"""
    global _default_recognizer
    if _default_recognizer is None:
        _default_recognizer = IntentRecognizer()
    return _default_recognizer