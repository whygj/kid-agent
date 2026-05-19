"""配置管理 - 读取环境变量和API配置"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

from src.utils.errors import ConfigError, check_api_key

logger = logging.getLogger(__name__)


class Provider(Enum):
    """LLM提供商"""
    GLM = "glm"
    DEEPSEEK = "deepseek"


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: Provider
    api_key: str
    api_base: str
    model: str
    timeout: int = 60


@dataclass
class DBConfig:
    """数据库配置"""
    path: str


@dataclass
class Config:
    """全局配置"""
    llm: LLMConfig
    db: DBConfig
    log_level: str = "INFO"

    @classmethod
    def load(cls, validate: bool = True) -> "Config":
        """从环境变量加载配置

        Args:
            validate: 是否验证配置有效性

        Returns:
            Config: 配置对象

        Raises:
            ConfigError: 配置无效时抛出
        """
        load_dotenv()

        env_path = Path(__file__).parent.parent.parent / "config" / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # 默认使用GLM，如果失败则使用DeepSeek
        provider_name = os.getenv("LLM_PROVIDER", "glm").lower()
        try:
            provider = Provider(provider_name)
        except ValueError:
            logger.warning(f"Unknown provider '{provider_name}', defaulting to GLM")
            provider = Provider.GLM

        if provider == Provider.GLM:
            llm_config = LLMConfig(
                provider=Provider.GLM,
                api_key=os.getenv("GLM_API_KEY", ""),
                api_base=os.getenv("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4"),
                model=os.getenv("GLM_MODEL", "glm-4"),
                timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            )
        else:
            llm_config = LLMConfig(
                provider=Provider.DEEPSEEK,
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            )

        db_config = DBConfig(
            path=os.getenv("DB_PATH", str(Path(__file__).parent.parent.parent / "data" / "kid_agent.db"))
        )

        config = cls(
            llm=llm_config,
            db=db_config,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

        if validate:
            config.validate()

        return config

    def validate(self) -> None:
        """验证配置有效性

        Raises:
            ConfigError: 配置无效时抛出
        """
        # 验证 API key
        check_api_key(self.llm.api_key, self.llm.provider.value)

        # 验证 API base URL 格式
        if not self.llm.api_base.startswith(("http://", "https://")):
            raise ConfigError(
                f"API base URL 必须以 http:// 或 https:// 开头",
                config_key=f"{self.llm.provider.value.upper()}_API_BASE",
            )

        # 验证日志级别
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ConfigError(
                f"无效的日志级别 '{self.log_level}'，可选值：{', '.join(valid_levels)}",
                config_key="LOG_LEVEL",
            )

        # 验证超时值
        if self.llm.timeout <= 0:
            raise ConfigError(
                f"超时时间必须大于 0，当前值：{self.llm.timeout}",
                config_key="LLM_TIMEOUT",
            )

        # 确保数据目录存在
        db_path = Path(self.db.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    def print_config(self) -> None:
        """打印当前配置（不包含敏感信息）"""
        logger.info("═════════════════════════════════════════════════════════")
        logger.info("Kid-Agent 配置")
        logger.info("═════════════════════════════════════════════════════════")
        logger.info(f"  LLM 提供商  : {self.llm.provider.value.upper()}")
        logger.info(f"  LLM 模型    : {self.llm.model}")
        logger.info(f"  API Base    : {self.llm.api_base}")
        logger.info(f"  超时时间    : {self.llm.timeout}s")
        logger.info(f"  数据库路径  : {self.db.path}")
        logger.info(f"  日志级别    : {self.log_level.upper()}")
        logger.info("═════════════════════════════════════════════════════════")

    def get_client(self, async_client: bool = False) -> OpenAI | AsyncOpenAI:
        """获取OpenAI客户端

        Args:
            async_client: 是否返回异步客户端

        Returns:
            OpenAI 或 AsyncOpenAI 客户端
        """
        if async_client:
            return AsyncOpenAI(
                api_key=self.llm.api_key,
                base_url=self.llm.api_base,
                timeout=self.llm.timeout,
            )
        return OpenAI(
            api_key=self.llm.api_key,
            base_url=self.llm.api_base,
            timeout=self.llm.timeout,
        )


# 全局配置实例
_config: Optional[Config] = None


def get_config(reload: bool = False, validate: bool = True) -> Config:
    """获取全局配置（懒加载）

    Args:
        reload: 是否重新加载配置
        validate: 是否验证配置

    Returns:
        Config: 配置对象
    """
    global _config
    if _config is None or reload:
        _config = Config.load(validate=validate)
    return _config


def reload_config() -> Config:
    """重新加载配置

    Returns:
        Config: 配置对象
    """
    return get_config(reload=True, validate=True)