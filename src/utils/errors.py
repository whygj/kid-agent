"""错误处理系统 - 自定义异常和全局错误处理装饰器"""

import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

from openai import AuthenticationError, APITimeoutError, RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class KidAgentError(Exception):
    """KidAgent 基础异常类"""

    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)
        self.message = message


class LLMError(KidAgentError):
    """LLM 调用错误"""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.original_error = original_error


class StorageError(KidAgentError):
    """存储错误（数据库错误）"""

    def __init__(self, message: str, operation: str = "", original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.operation = operation
        self.original_error = original_error


class ConfigError(KidAgentError):
    """配置错误"""

    def __init__(self, message: str, config_key: str = "") -> None:
        super().__init__(message)
        self.config_key = config_key


class ValidationError(KidAgentError):
    """数据验证错误"""

    def __init__(self, message: str, field: str = "") -> None:
        super().__init__(message)
        self.field = field


def handle_errors(
    default_return: Any = None,
    log_error: bool = True,
    raise_on: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """全局错误处理装饰器

    Args:
        default_return: 出错时的默认返回值（如为None则重新抛出异常）
        log_error: 是否记录错误日志
        raise_on: 指定需要重新抛出的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except raise_on:
                raise  # 重新抛出指定的异常
            except KidAgentError as e:
                if log_error:
                    logger.error(f"KidAgent error in {func.__name__}: {e.message}")
                if default_return is not None:
                    return cast(T, default_return)
                raise
            except AuthenticationError as e:
                error_msg = _format_auth_error(e)
                if log_error:
                    logger.error(f"Authentication error in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except APITimeoutError as e:
                error_msg = "请求超时，请检查网络连接后重试"
                if log_error:
                    logger.warning(f"Timeout in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except RateLimitError as e:
                error_msg = "请求过于频繁，请稍后再试"
                if log_error:
                    logger.warning(f"Rate limit in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except Exception as e:
                if log_error:
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                if default_return is not None:
                    return cast(T, default_return)
                raise

        return wrapper

    return decorator


def async_handle_errors(
    default_return: Any = None,
    log_error: bool = True,
    raise_on: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """异步全局错误处理装饰器

    Args:
        default_return: 出错时的默认返回值（如为None则重新抛出异常）
        log_error: 是否记录错误日志
        raise_on: 指定需要重新抛出的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except raise_on:
                raise
            except KidAgentError as e:
                if log_error:
                    logger.error(f"KidAgent error in {func.__name__}: {e.message}")
                if default_return is not None:
                    return cast(T, default_return)
                raise
            except AuthenticationError as e:
                error_msg = _format_auth_error(e)
                if log_error:
                    logger.error(f"Authentication error in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except APITimeoutError as e:
                error_msg = "请求超时，请检查网络连接后重试"
                if log_error:
                    logger.warning(f"Timeout in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except RateLimitError as e:
                error_msg = "请求过于频繁，请稍后再试"
                if log_error:
                    logger.warning(f"Rate limit in {func.__name__}: {error_msg}")
                if default_return is not None:
                    return cast(T, default_return)
                raise LLMError(error_msg, e) from e
            except Exception as e:
                if log_error:
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                if default_return is not None:
                    return cast(T, default_return)
                raise

        return wrapper

    return decorator


def retry_on_error(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """重试装饰器（指数退避）

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 退避因子（每次重试延迟乘以该因子）
        retry_on: 需要重试的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None
            delay = initial_delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} after {delay:.1f}s: {e}"
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}")

            if last_exception:
                raise last_exception
            raise RuntimeError(f"Max retries ({max_retries}) exceeded")

        return wrapper

    return decorator


def async_retry_on_error(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """异步重试装饰器（指数退避）

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 退避因子（每次重试延迟乘以该因子）
        retry_on: 需要重试的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            import asyncio

            last_exception: Exception | None = None
            delay = initial_delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} after {delay:.1f}s: {e}"
                        )
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}")

            if last_exception:
                raise last_exception
            raise RuntimeError(f"Max retries ({max_retries}) exceeded")

        return wrapper

    return decorator


def _format_auth_error(error: AuthenticationError) -> str:
    """格式化认证错误信息"""
    return """API 密钥无效或未配置

请检查 .env 文件中的配置：

- 如果使用 GLM：
  GLM_API_KEY=your_key_here

- 如果使用 DeepSeek：
  DEEPSEEK_API_KEY=your_key_here

获取 API 密钥：
- GLM: https://open.bigmodel.cn/
- DeepSeek: https://platform.deepseek.com/
"""


def check_api_key(config_key: str, provider: str) -> None:
    """检查 API key 是否已配置

    Args:
        config_key: 配置键名
        provider: 提供商名称

    Raises:
        ConfigError: 当 API key 未配置时
    """
    if not config_key or config_key in ("", "your_key_here", "YOUR_API_KEY"):
        raise ConfigError(
            f"请配置 {provider} 的 API 密钥",
            config_key=f"{provider.upper()}_API_KEY",
        )
