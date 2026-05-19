"""配置管理 - 读取环境变量和API配置"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI


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
    def load(cls) -> "Config":
        """从环境变量加载配置"""
        load_dotenv()

        env_path = Path(__file__).parent.parent.parent / "config" / ".env"
        load_dotenv(env_path)

        # 默认使用GLM，如果失败则使用DeepSeek
        provider_name = os.getenv("LLM_PROVIDER", "glm").lower()
        provider = Provider(provider_name)

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

        return cls(
            llm=llm_config,
            db=db_config,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def get_client(self, async_client: bool = False) -> OpenAI | AsyncOpenAI:
        """获取OpenAI客户端"""
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


def get_config() -> Config:
    """获取全局配置（懒加载）"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """重新加载配置"""
    global _config
    _config = Config.load()
    return _config