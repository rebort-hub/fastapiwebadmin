# -*- coding: utf-8 -*-
"""Loguru 日志配置：控制台 + 文件轮转"""

import atexit
import logging
import sys
import warnings

from loguru import logger

from app.config.path_conf import LOG_DIR
from app.config.setting import settings
from app.corelibs.local import g
from app.utils.common import get_str_uuid

_logger_handlers: list[int] = []


class InterceptHandler(logging.Handler):
    """将标准库 logging 转发到 Loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def correlation_id_filter(record) -> bool:
    if not g.trace_id:
        g.trace_id = get_str_uuid()
    record["extra"]["trace_id"] = g.trace_id
    return True


def cleanup_logging() -> None:
    global _logger_handlers
    for handler_id in _logger_handlers:
        try:
            logger.remove(handler_id)
        except ValueError:
            pass
    _logger_handlers.clear()


def setup_logging() -> None:
    """配置控制台与文件日志。"""
    global _logger_handlers

    cleanup_logging()
    logger.remove()

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    logger.configure(extra={"trace_id": "-"})

    console_fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<yellow>{extra[trace_id]}</yellow> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    file_fmt = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[trace_id]} | "
        "{name}:{function}:{line} | {message}"
    )

    handler_id = logger.add(
        sys.stdout,
        format=console_fmt,
        level=settings.LOGGER_LEVEL,
        colorize=True,
        filter=correlation_id_filter,
    )
    _logger_handlers.append(handler_id)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler_id = logger.add(
        str(LOG_DIR / "info.log"),
        format=file_fmt,
        level="INFO",
        rotation=settings.LOGGER_ROTATION,
        retention=settings.LOGGER_RETENTION,
        encoding="utf-8",
        filter=correlation_id_filter,
    )
    _logger_handlers.append(handler_id)

    handler_id = logger.add(
        str(LOG_DIR / "error.log"),
        format=file_fmt,
        level="ERROR",
        rotation=settings.LOGGER_ROTATION,
        retention=settings.LOGGER_RETENTION,
        encoding="utf-8",
        backtrace=True,
        diagnose=settings.DEBUG,
        filter=correlation_id_filter,
    )
    _logger_handlers.append(handler_id)

    logging.basicConfig(handlers=[InterceptHandler()], level=settings.LOGGER_LEVEL, force=True)
    for logger_name in logging.root.manager.loggerDict:
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False

    atexit.register(cleanup_logging)


log = logger
