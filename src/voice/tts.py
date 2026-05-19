"""语音合成服务 - TTS (Text to Speech)"""

import asyncio
import logging
from enum import Enum
from typing import Optional

import httpx
from openai import AsyncOpenAI

from src.config.settings import get_config
from src.utils.errors import ConfigError

logger = logging.getLogger(__name__)


class TTSProvider(Enum):
    """TTS提供商"""
    GLM = "glm"
    EDGE = "edge"


class TTSError(Exception):
    """TTS错误"""
    pass


class TTSService:
    """文字转语音服务"""

    def __init__(self, provider: Optional[TTSProvider] = None):
        """初始化TTS服务

        Args:
            provider: TTS提供商，默认从配置读取
        """
        config = get_config()

        # 从配置或参数获取provider
        provider_name = getattr(config, "tts_provider", "edge").lower()
        self.provider = provider or TTSProvider(provider_name)
        self.tts_voice = getattr(config, "tts_voice", "zh-CN-XiaoxiaoNeural")

        # GLM TTS 配置
        if self.provider == TTSProvider.GLM:
            self.glm_client = AsyncOpenAI(
                api_key=config.llm.api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4",
            )
            self.glm_model = "tts-1"
            self.glm_voice = "alloy"  # alloy|echo|fable|onyx|nova|shimmer

        logger.info(f"TTS服务初始化完成，提供商: {self.provider.value}")

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """文字转语音

        Args:
            text: 要转换的文本
            voice: 语音类型（可选，默认使用配置的语音）

        Returns:
            bytes: MP3音频数据

        Raises:
            TTSError: 合成失败时抛出
        """
        if not text or not text.strip():
            raise TTSError("文本不能为空")

        text = text.strip()

        try:
            if self.provider == TTSProvider.GLM:
                return await self._synthesize_glm(text, voice)
            else:
                return await self._synthesize_edge(text, voice)
        except Exception as e:
            logger.error(f"TTS合成失败: {e}")
            # 尝试fallback
            if self.provider == TTSProvider.GLM:
                logger.warning("GLM TTS失败，尝试使用edge-tts fallback")
                try:
                    return await self._synthesize_edge(text, voice)
                except Exception as fallback_error:
                    raise TTSError(f"GLM和edge-tts都失败: {fallback_error}") from fallback_error
            raise TTSError(f"TTS合成失败: {e}") from e

    async def _synthesize_glm(self, text: str, voice: Optional[str] = None) -> bytes:
        """使用智谱GLM TTS API合成语音

        Args:
            text: 要转换的文本
            voice: 语音类型

        Returns:
            bytes: MP3音频数据
        """
        # GLM TTS voice参数
        glm_voice = voice or self.glm_voice

        try:
            response = await self.glm_client.audio.speech.create(
                model=self.glm_model,
                voice=glm_voice,
                input=text,
                response_format="mp3",
            )

            audio_bytes = response.content
            logger.info(f"GLM TTS合成成功，文本长度: {len(text)} 字符，音频大小: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"GLM TTS API调用失败: {e}")
            raise TTSError(f"GLM TTS API调用失败: {e}") from e

    async def _synthesize_edge(self, text: str, voice: Optional[str] = None) -> bytes:
        """使用edge-tts合成语音

        Args:
            text: 要转换的文本
            voice: 语音类型

        Returns:
            bytes: MP3音频数据
        """
        try:
            import edge_tts
        except ImportError:
            raise TTSError("edge-tts未安装，请运行: pip install edge-tts") from None

        edge_voice = voice or self.tts_voice

        try:
            # 使用edge-tts
            communicate = edge_tts.Communicate(text, edge_voice)

            # 收集音频数据
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]

            logger.info(f"edge-tts合成成功，文本长度: {len(text)} 字符，音频大小: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"edge-tts合成失败: {e}")
            raise TTSError(f"edge-tts合成失败: {e}") from e

    def is_available(self) -> bool:
        """检查TTS服务是否可用

        Returns:
            bool: 是否可用
        """
        try:
            if self.provider == TTSProvider.GLM:
                return True  # GLM TTS可用
            else:
                import edge_tts
                return True
        except ImportError:
            return False


# 全局TTS服务实例
_tts_service: Optional[TTSService] = None


async def get_tts_service() -> TTSService:
    """获取全局TTS服务实例（懒加载）

    Returns:
        TTSService: TTS服务实例
    """
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
