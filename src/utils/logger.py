"""日志系统 - 支持彩色输出和文件记录"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


# 颜色映射
LOG_COLORS = {
    "DEBUG": "dim blue",
    "INFO": "blue",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold red",
}


def get_logger(
    name: str,
    log_level: Optional[str] = None,
    log_file: Optional[str | Path] = None,
    console_output: bool = True,
) -> logging.Logger:
    """获取配置好的日志记录器

    Args:
        name: 日志记录器名称（通常是模块名 __name__）
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（如为None则使用默认路径）
        console_output: 是否输出到控制台

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复配置
    if logger.handlers:
        return logger

    # 设置日志级别
    level = LOG_LEVELS.get((log_level or "").upper(), logging.INFO)
    logger.setLevel(level)

    # 日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 控制台输出（使用 RichHandler 实现彩色输出）
    if console_output:
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            log_time_format=date_format,
        )
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    # 文件输出
    if log_file is None:
        log_file = Path(__file__).parent.parent.parent / "logs" / "kid-agent.log"

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
        mode="a",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    return logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str | Path] = None,
) -> None:
    """全局配置日志系统

    Args:
        log_level: 全局日志级别
        log_file: 日志文件路径
    """
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 配置控制台处理器
    console_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s")
    )
    console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)

    # 配置文件处理器
    if log_file is None:
        log_file = Path(__file__).parent.parent.parent / "logs" / "kid-agent.log"

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s")
    )
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)


# 默认日志记录器
def _get_default_logger() -> logging.Logger:
    """获取默认日志记录器"""
    return get_logger(__name__)


# 导出便捷函数
def debug(msg: str, *args, **kwargs) -> None:
    """输出 DEBUG 级别日志"""
    _get_default_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """输出 INFO 级别日志"""
    _get_default_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """输出 WARNING 级别日志"""
    _get_default_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """输出 ERROR 级别日志"""
    _get_default_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """输出 CRITICAL 级别日志"""
    _get_default_logger().critical(msg, *args, **kwargs)
