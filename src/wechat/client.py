"""微信API客户端"""

import hashlib
import logging
import time
from typing import Any

import httpx

from src.config.settings import get_config

logger = logging.getLogger(__name__)


class WeChatClient:
    """微信API客户端"""

    def __init__(self):
        """初始化微信客户端"""
        config = get_config()
        self.app_id = config.wechat.app_id
        self.app_secret = config.wechat.app_secret
        self.token = config.wechat.token
        self.api_base = "https://api.weixin.qq.com"

        self._access_token: str | None = None
        self._token_expire_time: float = 0
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端（懒加载）"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """关闭HTTP客户端"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    def verify_signature(self, signature: str, timestamp: str, nonce: str) -> bool:
        """验证微信服务器签名

        Args:
            signature: 微信签名
            timestamp: 时间戳
            nonce: 随机数

        Returns:
            bool: 签名是否有效
        """
        if not self.token:
            logger.warning("WeChat token not configured")
            return False

        sort_list = sorted([self.token, timestamp, nonce])
        sort_str = "".join(sort_list)
        sha1 = hashlib.sha1()
        sha1.update(sort_str.encode("utf-8"))
        hashcode = sha1.hexdigest()

        return hashcode == signature

    async def get_access_token(self) -> str:
        """获取access_token（带缓存）

        Returns:
            str: access_token

        Raises:
            RuntimeError: 获取失败
        """
        current_time = time.time()

        if self._access_token and current_time < self._token_expire_time:
            return self._access_token

        url = f"{self.api_base}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }

        client = await self._get_http_client()
        response = await client.get(url, params=params)
        data = response.json()

        if "access_token" not in data:
            error_msg = data.get("errmsg", "Unknown error")
            logger.error(f"Failed to get access token: {error_msg}")
            raise RuntimeError(f"Failed to get access token: {error_msg}")

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self._token_expire_time = current_time + expires_in - 300

        logger.info("Access token refreshed successfully")
        return self._access_token

    async def send_customer_message(self, user_id: str, content: str) -> bool:
        """发送客服消息（用于主动推送）

        Args:
            user_id: 微信用户OpenID
            content: 消息内容

        Returns:
            bool: 是否发送成功
        """
        try:
            access_token = await self.get_access_token()
            url = f"{self.api_base}/cgi-bin/message/custom/send?access_token={access_token}"

            payload = {
                "touser": user_id,
                "msgtype": "text",
                "text": {"content": content},
            }

            client = await self._get_http_client()
            response = await client.post(url, json=payload)
            data = response.json()

            if data.get("errcode") == 0:
                logger.info(f"Message sent to {user_id} successfully")
                return True

            error_msg = data.get("errmsg", "Unknown error")
            logger.error(f"Failed to send message to {user_id}: {error_msg}")
            return False

        except Exception as e:
            logger.error(f"Error sending customer message: {e}")
            return False

    async def create_menu(self, menu_data: dict) -> bool:
        """创建自定义菜单

        Args:
            menu_data: 菜单配置字典

        Returns:
            bool: 是否创建成功
        """
        try:
            access_token = await self.get_access_token()
            url = f"{self.api_base}/cgi-bin/menu/create?access_token={access_token}"

            client = await self._get_http_client()
            response = await client.post(url, json=menu_data)
            data = response.json()

            if data.get("errcode") == 0:
                logger.info("Menu created successfully")
                return True

            error_msg = data.get("errmsg", "Unknown error")
            logger.error(f"Failed to create menu: {error_msg}")
            return False

        except Exception as e:
            logger.error(f"Error creating menu: {e}")
            return False

    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        """获取用户基本信息

        Args:
            user_id: 微信用户OpenID

        Returns:
            dict: 用户信息，失败返回None
        """
        try:
            access_token = await self.get_access_token()
            url = f"{self.api_base}/cgi-bin/user/info"
            params = {
                "access_token": access_token,
                "openid": user_id,
                "lang": "zh_CN",
            }

            client = await self._get_http_client()
            response = await client.get(url, params=params)
            data = response.json()

            if "errcode" in data:
                logger.error(f"Failed to get user info: {data.get('errmsg')}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None


# 默认客户端实例
_default_client: WeChatClient | None = None


async def get_wechat_client() -> WeChatClient:
    """获取默认微信客户端实例（懒加载）"""
    global _default_client
    if _default_client is None:
        _default_client = WeChatClient()
    return _default_client