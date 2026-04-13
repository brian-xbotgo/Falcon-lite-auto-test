# core/logger.py
import logging
import os
from datetime import datetime
from utils.config import LOG_DIR

# 全局日志实例
logger = logging.getLogger("RV1126B_Test")
logger.setLevel(logging.DEBUG)
logger.propagate = False  # 避免重复输出

# 日志格式：[时间] [级别] 内容
formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 控制台输出（INFO及以上级别）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 文件输出（DEBUG及以上，按日期命名）
log_file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_test.log"
log_file_path = os.path.join(LOG_DIR, log_file_name)
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# 绑定处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 测试函数（直接运行验证）
if __name__ == "__main__":
    logger.info("日志系统初始化成功")
    logger.debug("调试日志示例")
    logger.warning("警告日志示例")
    logger.error("错误日志示例")