"""微信公众号消息服务器"""

import logging
import xml.etree.ElementTree as ET
from typing import Any

from src.wechat.handler import WeChatHandler

logger = logging.getLogger(__name__)


class WeChatMessage:
    """微信消息数据类"""

    def __init__(
        self,
        to_user_name: str,
        from_user_name: str,
        create_time: str,
        msg_type: str,
        content: str = "",
        event: str = "",
        event_key: str = "",
    ):
        self.to_user_name = to_user_name
        self.from_user_name = from_user_name
        self.create_time = create_time
        self.msg_type = msg_type
        self.content = content
        self.event = event
        self.event_key = event_key

    @classmethod
    def from_xml(cls, xml_data: str) -> "WeChatMessage | None":
        """从XML解析消息

        Args:
            xml_data: XML格式的消息数据

        Returns:
            WeChatMessage | None: 解析后的消息对象
        """
        try:
            root = ET.fromstring(xml_data)

            to_user_name = root.findtext("ToUserName", "")
            from_user_name = root.findtext("FromUserName", "")
            create_time = root.findtext("CreateTime", "")
            msg_type = root.findtext("MsgType", "")
            content = root.findtext("Content", "")
            event = root.findtext("Event", "")
            event_key = root.findtext("EventKey", "")

            return cls(
                to_user_name=to_user_name,
                from_user_name=from_user_name,
                create_time=create_time,
                msg_type=msg_type,
                content=content,
                event=event,
                event_key=event_key,
            )
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML message: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing message: {e}")
            return None

    def to_text_reply(self, content: str) -> str:
        """生成文本消息回复XML

        Args:
            content: 回复内容

        Returns:
            str: XML格式的回复
        """
        return f"""<xml>
<ToUserName><
![CDATA[{self.from_user_name}]]></ToUserName>
<FromUserName><![CDATA[{self.to_user_name}]]></FromUserName>
<CreateTime>{int(self.create_time)}</CreateTime>
<MsgType><
![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""


class WeChatServer:
    """微信公众号消息服务器"""

    def __init__(self):
        """初始化服务器"""
        self.handler = WeChatHandler()

    async def verify(
        self, signature: str, timestamp: str, nonce: str, echostr: str
    ) -> str | None:
        """验证微信服务器签名（GET请求）

        Args:
            signature: 微信签名
            timestamp: 时间戳
            nonce: 随机数
            echostr: 随机字符串

        Returns:
            str | None: 验证成功返回echostr，失败返回None
        """
        from src.wechat.client import get_wechat_client

        client = await get_wechat_client()

        if not client.verify_signature(signature, timestamp, nonce):
            logger.warning("Signature verification failed")
            return None

        logger.info("Signature verification successful")
        return echostr

    async def handle_message(self, xml_data: str) -> str:
        """处理微信消息（POST请求），返回XML回复

        Args:
            xml_data: XML格式的消息数据

        Returns:
            str: XML格式的回复
        """
        message = WeChatMessage.from_xml(xml_data)

        if not message:
            logger.error("Failed to parse message")
            return message.to_text_reply("消息解析失败，请重试") if message else ""

        logger.info(
            f"Received message from {message.from_user_name}: type={message.msg_type}, content={message.content[:50]}"
        )

        try:
            # 路由到对应的处理器
            if message.msg_type == "text":
                reply_content = await self.handler.handle_text(
                    message.from_user_name, message.content
                )
            elif message.msg_type == "event":
                reply_content = await self.handler.handle_event(
                    message.from_user_name, message.event, message.event_key
                )
            elif message.msg_type == "voice":
                reply_content = await self.handler.handle_voice(
                    message.from_user_name, xml_data
                )
            else:
                reply_content = "暂时还不支持这种消息类型哦~"

            return message.to_text_reply(reply_content)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return message.to_text_reply("出错了，请稍后再试~")


# 默认服务器实例
_default_server: WeChatServer | None = None


async def get_wechat_server() -> WeChatServer:
    """获取默认服务器实例（懒加载）"""
    global _default_server
    if _default_server is None:
        _default_server = WeChatServer()
    return _default_server