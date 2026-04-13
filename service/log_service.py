# -*- coding: utf-8 -*-
"""
日志服务模块
功能：全项目统一日志输出，自动写入data/logs目录，支持分级日志
作者：wuzhibin
创建时间：2026-04-13
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Callable
from utils.config import LOG_DIR, LOG_LEVEL, LOG_MAX_SIZE, LOG_RETENTION_DAYS
from utils.common import get_current_time_str


class QtLogHandler(logging.Handler):
    """日志转发到UI的handler"""
    def __init__(self, callback: Callable):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)


class LogService:
    """
    统一日志服务类
    采用单例模式，全局唯一实例
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger("RV1126B_Test")
        self.logger.setLevel(self._get_log_level())
        self.logger.propagate = False
        self.qt_handler = None

        # 避免重复添加handler
        if self.logger.handlers:
            self._initialized = True
            return

        # 日志格式
        log_format = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台输出handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

        # 文件输出handler（按大小轮转）
        log_filename = f"{get_current_time_str()}_test.log"
        log_file_path = os.path.join(LOG_DIR, log_filename)

        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=LOG_MAX_SIZE * 1024 * 1024,  # MB转字节
            backupCount=LOG_RETENTION_DAYS,
            encoding="utf-8"
        )
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

        self._initialized = True

    def _get_log_level(self):
        """转换配置中的日志级别为logging常量"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(LOG_LEVEL.upper(), logging.INFO)

    def debug(self, message: str) -> None:
        """输出DEBUG级别日志"""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """输出INFO级别日志"""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """输出WARNING级别日志"""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """输出ERROR级别日志"""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """输出CRITICAL级别日志"""
        self.logger.critical(message)


# 全局日志实例，其他模块直接导入使用
log = LogService()

__all__ = ["LogService", "log", "QtLogHandler"]
