"""
日志配置模块 - 增强版
提供统一的日志配置和获取方法，支持按服务分类日志
"""

import logging
import re
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as loguru_logger

from app.config import settings

_SENSITIVE_LOG_PATTERN = re.compile(
    r"(?i)(password|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization)"
    r"\s*[:=]\s*([^\s,;]+)"
)


def redact_log_message(message: str) -> str:
    """替换日志文本中的常见敏感字段值。"""
    return _SENSITIVE_LOG_PATTERN.sub(r"\1=***", message)


def _redact_log_record(record: dict) -> None:
    """Loguru patcher：统一脱敏所有 sink 的消息。"""
    record["message"] = redact_log_message(record["message"])


class InterceptHandler(logging.Handler):
    """
    将标准 logging 日志转发到 loguru

    这使得第三方库使用 logging 的日志也能被 loguru 处理
    """

    def emit(self, record: logging.LogRecord) -> None:
        """转发日志记录到 loguru"""
        # 获取对应的 loguru level
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, redact_log_message(record.getMessage())
        )


def setup_logger(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "500 MB",
    retention: str = "30 days",
    compression: str = "zip",
) -> None:
    """
    配置 loguru 日志系统

    Args:
        log_file: 主日志文件路径
        log_level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
        compression: 压缩格式
    """
    # 移除默认的 handler
    loguru_logger.remove()
    loguru_logger.configure(patcher=_redact_log_record)

    # 定义日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    file_log_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )

    # 添加控制台输出
    loguru_logger.add(
        sys.stdout,
        level=log_level,
        format=log_format,
        colorize=True,
    )

    # 添加主日志文件输出（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        loguru_logger.add(
            log_file,
            level=log_level,
            format=file_log_format,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
        )

    # 添加错误日志文件（记录所有错误和警告）
    error_log_file = log_path.parent / "error.log" if log_file else None
    if error_log_file:
        loguru_logger.add(
            error_log_file,
            level="WARNING",
            format=file_log_format,
            rotation="100 MB",
            retention="7 days",
            compression=compression,
            encoding="utf-8",
        )

    # 添加API访问日志（记录所有API请求）
    api_log_file = log_path.parent / "api.log" if log_file else None
    if api_log_file:
        loguru_logger.add(
            api_log_file,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            rotation="200 MB",
            retention="14 days",
            compression=compression,
            encoding="utf-8",
            filter=lambda record: "api/v1/" in record["name"].lower()
            or "api" in record["name"].lower(),
        )

    # 添加数据库查询日志
    db_log_file = log_path.parent / "db.log" if log_file else None
    if db_log_file:
        loguru_logger.add(
            db_log_file,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            rotation="200 MB",
            retention="7 days",
            compression=compression,
            encoding="utf-8",
            filter=lambda record: "sqlalchemy" in record["name"].lower()
            or "db" in record["name"].lower(),
        )

    # 拦截标准 logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # 在开发环境中，记录更详细的日志
    if settings.DEBUG:
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def get_logger(name: str):
    """
    获取 logger 实例

    Args:
        name: logger 名称，通常使用 __name__

    Returns:
        logger 实例
    """
    return loguru_logger.bind(name=name)


def get_service_logger(service_name: str):
    """
    获取服务的专用logger

    Args:
        service_name: 服务名称（如 'task', 'email', 'customer'）

    Returns:
        logger 实例
    """
    return loguru_logger.bind(service=service_name)


# 初始化日志系统
if settings.DEBUG:
    setup_logger(log_level="DEBUG", log_file=settings.LOG_FILE)
else:
    setup_logger(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
