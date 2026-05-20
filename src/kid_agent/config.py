#!/usr/bin/env python
"""
Kid Agent Configuration
=======================

Loads environment variables and provides configuration for the agent.
GLM API is used as the LLM backend via OpenAI-compatible interface.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from config directory
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = _PROJECT_ROOT / "config" / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration — uses OpenAI-compatible API (GLM)."""
    binding: str = os.getenv("LLM_BINDING", "openai")
    api_key: str = os.getenv("LLM_API_KEY", os.getenv("GLM_API_KEY", ""))
    api_base: str = os.getenv("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
    model: str = os.getenv("LLM_MODEL", "glm-4-flash")
    timeout: int = int(os.getenv("LLM_TIMEOUT", "60"))


@dataclass
class KBConfig:
    """Knowledge base configuration."""
    kb_dir: str = os.getenv("KID_KB_DIR", str(_PROJECT_ROOT / "data"))
    db_path: str = ""

    def __post_init__(self):
        if not self.db_path:
            self.db_path = str(Path(self.kb_dir) / "knowledge.db")


@dataclass
class AgentConfig:
    """Complete agent configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    kb: KBConfig = field(default_factory=KBConfig)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")

    @classmethod
    def load(cls) -> AgentConfig:
        """Load configuration from environment."""
        return cls()

    def to_deeptutor_env(self) -> dict[str, str]:
        """Export as environment variables for DeepTutor runtime."""
        return {
            "LLM_BINDING": self.llm.binding,
            "LLM_API_KEY": self.llm.api_key,
            "LLM_API_BASE": self.llm.api_base,
            "LLM_MODEL": self.llm.model,
            "KID_KB_DIR": self.kb.kb_dir,
        }


# Global config singleton
_config: AgentConfig | None = None


def get_config(reload: bool = False) -> AgentConfig:
    """Get or create the global configuration."""
    global _config
    if _config is None or reload:
        _config = AgentConfig.load()
    return _config
