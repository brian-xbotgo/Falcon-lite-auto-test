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
from PyQt6.QtCore import QObject, pyqtSignal
from .config import LOG_DIR, LOG_LEVEL, LOG_MAX_SIZE, LOG_RETENTION_DAYS
from .common import get_current_time_str


class QtLogHandler(logging.Handler, QObject):
    """日志转发到UI的handler - 线程安全版本"""
    log_received = pyqtSignal(str)
    
    def __init__(self, callback: Callable):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.log_received.connect(callback)

    def emit(self, record):
        log_entry = self.format(record)
        self.log_received.emit(log_entry)


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
        self.qt_handlers = []

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

        # 确保日志目录存在（打包环境需在 _internal/data/logs）
        from .config import LOG_DIR
        os.makedirs(LOG_DIR, exist_ok=True)

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

    def debug(self, message: str, **kwargs) -> None:
        """输出DEBUG级别日志"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """输出INFO级别日志"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """输出WARNING级别日志"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """输出ERROR级别日志"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """输出CRITICAL级别日志"""
        self.logger.critical(message, **kwargs)

    def add_qt_handler(self, callback: Callable) -> None:
        """添加Qt日志回调"""
        handler = QtLogHandler(callback)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.logger.addHandler(handler)
        self.qt_handlers.append(handler)

    def remove_all_qt_handlers(self) -> None:
        """移除所有Qt日志回调"""
        for handler in self.qt_handlers:
            self.logger.removeHandler(handler)
        self.qt_handlers.clear()


# 全局日志实例，其他模块直接导入使用
log = LogService()

__all__ = ["LogService", "log", "QtLogHandler"]
