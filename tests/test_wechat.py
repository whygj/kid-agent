"""微信公众号模块单元测试"""

import hashlib
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.wechat.client import WeChatClient
from src.wechat.server import WeChatServer, WeChatMessage
from src.wechat.binding import UserBinding
from src.wechat.handler import WeChatHandler


class TestWeChatClient:
    """微信客户端测试"""

    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        c = WeChatClient()
        c.token = "test_token"
        return c

    def test_verify_signature_valid(self, client):
        """测试签名验证 - 有效签名"""
        token = "test_token"
        timestamp = "1234567890"
        nonce = "test_nonce"
        client.token = token

        sort_list = sorted([token, timestamp, nonce])
        sort_str = "".join(sort_list)
        sha1 = hashlib.sha1()
        sha1.update(sort_str.encode("utf-8"))
        signature = sha1.hexdigest()

        assert client.verify_signature(signature, timestamp, nonce) is True

    def test_verify_signature_invalid(self, client):
        """测试签名验证 - 无效签名"""
        assert client.verify_signature("invalid", "123", "nonce") is False

    def test_verify_signature_no_token(self, client):
        """测试签名验证 - 无token"""
        client.token = ""
        assert client.verify_signature("any", "123", "nonce") is False


class TestWeChatMessage:
    """微信消息测试"""

    def test_from_xml_text_message(self):
        """测试解析文本消息"""
        xml_data = """<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1234567890</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好]]></Content>
</xml>"""

        msg = WeChatMessage.from_xml(xml_data)

        assert msg.to_user_name == "toUser"
        assert msg.from_user_name == "fromUser"
        assert msg.create_time == "1234567890"
        assert msg.msg_type == "text"
        assert msg.content == "你好"

    def test_from_xml_event_message(self):
        """测试解析事件消息"""
        xml_data = """<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1234567890</CreateTime>
<MsgType><![CDATA[event]]></MsgType>
<Event><![CDATA[subscribe]]></Event>
<EventKey><![CDATA[]]></EventKey>
</xml>"""

        msg = WeChatMessage.from_xml(xml_data)

        assert msg.msg_type == "event"
        assert msg.event == "subscribe"
        assert msg.event_key == ""

    def test_from_xml_invalid(self):
        """测试解析无效XML"""
        msg = WeChatMessage.from_xml("invalid xml")
        assert msg is None

    def test_to_text_reply(self):
        """测试生成文本回复"""
        msg = WeChatMessage("toUser", "fromUser", "1234567890", "text", "test")
        reply = msg.to_text_reply("你好")

        assert "fromUser" in reply
        assert "toUser" in reply
        assert "你好" in reply
        assert "<![CDATA[" in reply


class TestWeChatServer:
    """微信服务器测试"""

    @pytest.fixture
    def server(self):
        """创建服务器实例"""
        return WeChatServer()

    @pytest.mark.asyncio
    async def test_verify_signature(self, server):
        """测试服务器验证签名"""
        token = "test_token"
        timestamp = "1234567890"
        nonce = "test_nonce"

        sort_list = sorted([token, timestamp, nonce])
        sort_str = "".join(sort_list)
        sha1 = hashlib.sha1()
        sha1.update(sort_str.encode("utf-8"))
        signature = sha1.hexdigest()

        with patch("src.wechat.client.get_wechat_client") as mock_client:
            mock = AsyncMock()
            mock.verify_signature.return_value = True
            mock_client.return_value = mock

            result = await server.verify(signature, timestamp, nonce, "echo123")
            assert result == "echo123"


class TestWeChatHandler:
    """微信处理器测试"""

    @pytest.fixture
    def handler(self):
        """创建处理器实例"""
        return WeChatHandler()

    @pytest.mark.asyncio
    async def test_handle_bind_command(self, handler):
        """测试绑定命令"""
        with patch.object(handler.binding, "bind") as mock_bind:
            mock_bind.return_value = "✅ 绑定成功！你的账号已关联到：小明"
            result = await handler.handle_text("test_user", "绑定 student01")
            mock_bind.assert_called_once_with("test_user", "student01", "student")
            assert "绑定成功" in result

    @pytest.mark.asyncio
    async def test_handle_bind_command_not_found(self, handler):
        """测试绑定命令 - 学生不存在"""
        with patch.object(handler.binding, "bind") as mock_bind:
            mock_bind.return_value = "❌ 找不到学生 'student01'，请检查学生ID是否正确"
            result = await handler.handle_text("test_user", "绑定 student01")
            mock_bind.assert_called_once_with("test_user", "student01", "student")
            assert "找不到学生" in result

    @pytest.mark.asyncio
    async def test_handle_help_command(self, handler):
        """测试帮助命令"""
        result = await handler.handle_text("test_user", "帮助")
        assert "帮助" in result or "绑定" in result

    @pytest.mark.asyncio
    async def test_handle_text_no_binding(self, handler):
        """测试文本消息 - 未绑定"""
        with patch.object(handler.binding, "get_student_id") as mock_get:
            mock_get.return_value = None
            result = await handler.handle_text("test_user", "你好")
            assert "还没有绑定" in result or "绑定" in result

    @pytest.mark.asyncio
    async def test_handle_event_subscribe(self, handler):
        """测试关注事件"""
        result = await handler._handle_subscribe("test_user")
        assert "欢迎" in result

    @pytest.mark.asyncio
    async def test_handle_event_click_start_learn(self, handler):
        """测试点击开始学习菜单"""
        result = await handler._handle_start_learn("test_user")
        # 未绑定时返回绑定提示
        assert result is not None

    def test_get_help_message(self, handler):
        """测试获取帮助消息"""
        help_msg = handler._get_help_message()
        assert "绑定" in help_msg
        assert "学习" in help_msg
        assert "报告" in help_msg


class TestUserBinding:
    """用户绑定测试"""

    @pytest.fixture
    def binding(self):
        """创建绑定管理器实例"""
        return UserBinding()

    @pytest.mark.asyncio
    async def test_get_student_id_not_bound(self, binding):
        """测试获取学生ID - 未绑定"""
        with patch("src.wechat.binding.get_store") as mock_store:
            mock = AsyncMock()
            mock.get_wechat_binding.return_value = None
            mock_store.return_value = mock

            result = await binding.get_student_id("wechat_123", "student")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_parent_binding(self, binding):
        """测试获取家长绑定"""
        with patch("src.wechat.binding.get_store") as mock_store:
            mock = AsyncMock()
            mock_binding = MagicMock()
            mock_binding.wechat_user_id = "parent_wechat"
            mock.get_wechat_binding_by_student.return_value = mock_binding
            mock_store.return_value = mock

            result = await binding.get_parent_binding("student01")
            assert result == "parent_wechat"

    @pytest.mark.asyncio
    async def test_get_student_binding(self, binding):
        """测试获取学生绑定"""
        with patch("src.wechat.binding.get_store") as mock_store:
            mock = AsyncMock()
            mock_binding = MagicMock()
            mock_binding.wechat_user_id = "student_wechat"
            mock.get_wechat_binding_by_student.return_value = mock_binding
            mock_store.return_value = mock

            result = await binding.get_student_binding("student01")
            assert result == "student_wechat"

    @pytest.mark.asyncio
    async def test_unbind(self, binding):
        """测试解绑"""
        with patch("src.wechat.binding.get_store") as mock_store:
            mock = AsyncMock()
            mock.delete_wechat_binding.return_value = True
            mock_store.return_value = mock

            result = await binding.unbind("wechat_123", "student")
            assert result is True

    @pytest.mark.asyncio
    async def test_unbind_not_found(self, binding):
        """测试解绑 - 未找到"""
        with patch("src.wechat.binding.get_store") as mock_store:
            mock = AsyncMock()
            mock.delete_wechat_binding.return_value = False
            mock_store.return_value = mock

            result = await binding.unbind("wechat_123", "student")
            assert result is False


class TestWeChatIntegration:
    """微信集成测试"""

    @pytest.mark.asyncio
    async def test_message_flow(self):
        """测试完整消息流程"""
        # 创建服务器
        server = WeChatServer()

        xml_data = """<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1234567890</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[帮助]]></Content>
</xml>"""

        with patch("src.wechat.server.get_wechat_server") as mock_server:
            mock_server.return_value = server

            reply = await server.handle_message(xml_data)
            assert reply is not None
            assert "帮助" in reply or "还没有绑定" in reply

    def test_menu_config_exists(self):
        """测试菜单配置文件存在"""
        from pathlib import Path

        menu_path = Path(__file__).parent.parent / "src" / "wechat" / "menu.json"
        assert menu_path.exists()

    def test_menu_config_valid(self):
        """测试菜单配置有效"""
        import json
        from pathlib import Path

        menu_path = Path(__file__).parent.parent / "src" / "wechat" / "menu.json"
        with open(menu_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "button" in data
        assert isinstance(data["button"], list)
        assert len(data["button"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])