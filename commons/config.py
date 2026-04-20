# -*- coding: utf-8 -*-
"""
全局配置文件
所有项目常量、路径、参数统一在此定义，禁止在其他文件硬编码
作者：wuzhibin
创建时间：2026-04-13
"""
import os

# ====================== 项目基本信息 ======================
APP_NAME = "冒烟测试工具"
APP_VERSION = "v1.0.0"
AUTHOR = "wuzhibin"

# ====================== 窗口配置 ======================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 670
WINDOW_MIN_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# ====================== 数据目录配置（唯一出口） ======================
# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 数据根目录
DATA_DIR = os.path.join(BASE_DIR, "data")
# 日志目录
LOG_DIR = os.path.join(DATA_DIR, "logs")
# 测试报告目录
REPORT_DIR = os.path.join(DATA_DIR, "reports")
# 固件存储目录
FIRMWARE_DIR = os.path.join(DATA_DIR, "firmware")

# ====================== ADB 配置（USB 专属） ======================
# ADB 命令默认超时时间（秒）
ADB_DEFAULT_TIMEOUT = 300
# ADB 服务端口（USB 连接无需修改）
ADB_DEFAULT_PORT = 5555
# 设备扫描间隔（毫秒）
DEVICE_SCAN_INTERVAL = 1000

# ====================== 日志配置 ======================
# 日志保留天数
LOG_RETENTION_DAYS = 30
# 单个日志文件最大大小（MB）
LOG_MAX_SIZE = 100
# 日志级别
LOG_LEVEL = "DEBUG"

# ====================== 测试默认参数 ======================
# 默认开关机循环次数
DEFAULT_LOOP_COUNT = 1
# 默认人工项重试次数
DEFAULT_MANUAL_RETRY = 3
# 默认测试超时时间（秒）
DEFAULT_TEST_TIMEOUT = 300
# 默认 Ping 目标地址
# DEFAULT_PING_TARGET = "192.168.1.1"

# ====================== 报告配置 ======================
# 支持的报告格式
SUPPORTED_REPORT_FORMATS = ["html"]
# 默认报告格式
DEFAULT_REPORT_FORMAT = "html"