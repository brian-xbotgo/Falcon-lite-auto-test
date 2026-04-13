# utils/config.py
import os

# 项目根目录（自动获取，无需手动修改）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------
# 数据目录配置（程序启动自动创建）
# --------------------------
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(DATA_DIR, "logs")
REPORT_DIR = os.path.join(DATA_DIR, "reports")
FIRMWARE_DIR = os.path.join(DATA_DIR, "firmware")
SCRIPTS_DIR = os.path.join(DATA_DIR, "scripts")

# 自动创建所有目录
for dir_path in [DATA_DIR, LOG_DIR, REPORT_DIR, FIRMWARE_DIR, SCRIPTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# --------------------------
# ADB 核心配置
# --------------------------
ADB_TIMEOUT = 300  # ADB命令超时时间（秒）
DEFAULT_PING_ADDR = "192.168.1.1"  # 网络测试默认网关

# --------------------------
# 测试项默认配置
# --------------------------
DEFAULT_MANUAL_RETRY = 3  # 人工确认项默认重试次数
DEFAULT_REBOOT_TIMES = 1  # 开关机测试默认循环次数