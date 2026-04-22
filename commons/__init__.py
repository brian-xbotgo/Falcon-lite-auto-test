# -*- coding: utf-8 -*-
"""
全局公共工具库
包含日志、字符串处理、文件操作、时间戳、错误码定义、通用数据结构等所有模块共用的基础代码
"""

# 导出所有公共模块
from .log_service import log, LogService
from .common import *
from .config import *
from .device_model import DeviceModel
from .test_model import TestModel, Priority, Module
from .adb_service import ADBService
from .ble_service import BleService
from .ffmpeg_service import FFMPEGService
# 引擎核心模块
from .engine.test_service import TestService, TestStatus, register_test_case, auto_discover_test_cases
from .engine.report_service import ReportService

__all__ = [
    'log', 'LogService',
    'DeviceModel', 'TestModel', 'Priority', 'Module',
    'ADBService',
    'BleService',
    'FFMPEGService',
    'TestService', 'TestStatus',
    'ReportService',
    'register_test_case', 'auto_discover_test_cases',
]
