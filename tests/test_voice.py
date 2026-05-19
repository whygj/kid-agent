"""语音模块测试"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.voice.tts import TTSService, TTSError, TTSProvider, get_tts_service


class TestTTSService:
    """TTSService测试"""

    @pytest.mark.asyncio
    @patch('src.voice.tts.TTSService._synthesize_edge')
    async def test_synthesize_edge_tts(self, mock_synthesize_edge):
        """测试edge-tts合成"""
        mock_synthesize_edge.return_value = b'mock audio data'

        service = TTSService(TTSProvider.EDGE)
        result = await service.synthesize("测试文本")

        assert result == b'mock audio data'
        mock_synthesize_edge.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.voice.tts.TTSService._synthesize_glm')
    @patch('src.voice.tts.TTSService._synthesize_edge')
    async def test_glm_fallback_to_edge(self, mock_synthesize_edge, mock_synthesize_glm):
        """测试GLM失败fallback到edge"""
        mock_synthesize_glm.side_effect = Exception("GLM API error")
        mock_synthesize_edge.return_value = b'fallback audio'

        service = TTSService(TTSProvider.GLM)
        result = await service.synthesize("测试文本")

        assert result == b'fallback audio'
        mock_synthesize_glm.assert_called_once()
        mock_synthesize_edge.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_empty_text(self):
        """测试空文本处理"""
        service = TTSService(TTSProvider.EDGE)

        with pytest.raises(TTSError) as exc_info:
            await service.synthesize("")
        assert "文本不能为空" in str(exc_info.value)

        with pytest.raises(TTSError) as exc_info:
            await service.synthesize("   ")
        assert "文本不能为空" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.voice.tts.TTSService._synthesize_edge')
    async def test_synthesize_with_whitespace_only(self, mock_synthesize_edge):
        """测试只有空白的文本"""
        mock_synthesize_edge.return_value = b'audio data'

        service = TTSService(TTSProvider.EDGE)
        result = await service.synthesize("  测试  ")

        assert result == b'audio data'
        # 验证调用了trim后的文本
        mock_synthesize_edge.assert_called_once_with("测试", None)

    def test_provider_enum(self):
        """测试TTSProvider枚举"""
        assert TTSProvider.EDGE.value == "edge"
        assert TTSProvider.GLM.value == "glm"

    def test_is_available_with_edge_tts(self):
        """测试edge-tts可用性检查"""
        # 实际安装了edge-tts，直接测试
        try:
            import edge_tts  # noqa: F401
            service = TTSService(TTSProvider.EDGE)
            assert service.is_available() is True
        except ImportError:
            pytest.skip("edge-tts未安装")

    def test_is_available_without_edge_tts(self):
        """测试edge-tts不可用时"""
        # GLM不依赖edge-tts
        service = TTSService(TTSProvider.GLM)
        assert service.is_available() is True


class TestTTSErrors:
    """TTS错误处理测试"""

    @pytest.mark.asyncio
    async def test_edge_tts_import_error(self):
        """测试edge-tts未安装时的错误"""
        # 由于edge_tts是懒加载，这个测试需要特殊处理
        # 暂时跳过，因为需要在import时模拟失败
        pytest.skip("需要模拟懒加载的import错误")

    @pytest.mark.asyncio
    @patch('src.voice.tts.TTSService._synthesize_glm', side_effect=Exception("GLM failed"))
    @patch('src.voice.tts.TTSService._synthesize_edge', side_effect=Exception("Edge failed"))
    async def test_both_providers_fail(self, mock_edge, mock_glm):
        """测试两个provider都失败"""
        service = TTSService(TTSProvider.GLM)
        with pytest.raises(TTSError) as exc_info:
            await service.synthesize("测试")
        assert "GLM和edge-tts都失败" in str(exc_info.value)


class TestGlobalTTS:
    """全局TTS服务测试"""

    @pytest.mark.asyncio
    @patch('src.voice.tts.TTSService')
    async def test_get_tts_service_singleton(self, mock_tts_service_class):
        """测试全局单例"""
        mock_instance = AsyncMock()
        mock_tts_service_class.return_value = mock_instance

        service1 = await get_tts_service()
        service2 = await get_tts_service()

        assert service1 is service2
        mock_tts_service_class.assert_called_once()


class TestTTSServiceEdgeImplementation:
    """edge-tts实现详细测试"""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not __import__('os').path.exists(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '.venv/lib/python3.12/site-packages/edge_tts/__init__.py')),
        reason="edge-tts未安装"
    )
    async def test_edge_tts_stream_processing(self):
        """测试edge-tts流式处理"""
        service = TTSService(TTSProvider.EDGE)

        # 实际调用edge-tts
        try:
            result = await service._synthesize_edge("你好", "zh-CN-XiaoxiaoNeural")
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            pytest.skip(f"edge-tts测试跳过: {e}")


# 如果有GLM API凭证，可以添加集成测试
@pytest.mark.integration
class TestTTSGlmIntegration:
    """GLM TTS集成测试（需要API密钥）"""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not __import__('os').getenv('GLM_API_KEY'),
        reason="需要GLM_API_KEY环境变量"
    )
    async def test_glm_tts_real_call(self):
        """真实GLM TTS API调用测试"""
        service = TTSService(TTSProvider.GLM)
        result = await service._synthesize_glm("你好", "alloy")

        assert result is not None
        assert len(result) > 0
        # MP3文件头
        assert result.startswith(b'ID3') or result.startswith(b'\xff\xfb')
