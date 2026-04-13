# core/adb_manager.py
import subprocess
import time
from typing import Tuple, List, Optional
from core.logger import logger
from utils.config import ADB_TIMEOUT

class ADBManager:
    """ADB命令封装类，负责与RV1126B设备通信"""
    def __init__(self, serial: Optional[str] = None):
        self._serial = serial  # 多设备时指定序列号
        self._timeout = ADB_TIMEOUT

    def _build_adb_cmd(self, cmd: List[str]) -> List[str]:
        """构建ADB命令前缀，自动添加设备序列号"""
        adb_cmd = ["adb"]
        if self._serial:
            adb_cmd.extend(["-s", self._serial])
        adb_cmd.extend(cmd)
        return adb_cmd

    def execute_command(self, shell_cmd: str) -> Tuple[int, str, str]:
        """执行ADB Shell命令，返回(返回码, 标准输出, 标准错误)"""
        adb_cmd = self._build_adb_cmd(["shell", shell_cmd])
        logger.info(f"执行ADB命令: {' '.join(adb_cmd)}")

        try:
            result = subprocess.run(
                adb_cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            logger.debug(f"命令返回码: {result.returncode}, 输出: {stdout}, 错误: {stderr}")
            return result.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            error_msg = f"命令执行超时: {' '.join(adb_cmd)}"
            logger.error(error_msg)
            return -1, "", error_msg

    def get_device_list(self) -> List[str]:
        """获取当前连接的所有ADB设备列表"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            lines = result.stdout.strip().split("\n")[1:]  # 跳过标题行
            devices = [line.split("\t")[0] for line in lines if line.strip()]
            logger.info(f"检测到{len(devices)}台ADB设备: {devices}")
            return devices
        except Exception as e:
            logger.error(f"获取设备列表失败: {str(e)}")
            return []

    def push_file(self, local_path: str, remote_path: str) -> bool:
        """推送本地文件到设备"""
        adb_cmd = self._build_adb_cmd(["push", local_path, remote_path])
        logger.info(f"推送文件: {' '.join(adb_cmd)}")

        try:
            result = subprocess.run(
                adb_cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            if result.returncode == 0:
                logger.info("文件推送成功")
                return True
            else:
                logger.error(f"文件推送失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"推送文件异常: {str(e)}")
            return False

    def reboot_device(self) -> bool:
        """重启设备"""
        adb_cmd = self._build_adb_cmd(["reboot"])
        logger.info("执行设备重启命令")

        try:
            subprocess.Popen(adb_cmd)  # 异步执行，不等待
            time.sleep(5)
            logger.info("设备重启命令已发送，等待重连...")
            return True
        except Exception as e:
            logger.error(f"重启设备失败: {str(e)}")
            return False

# 测试函数（直接运行验证）
if __name__ == "__main__":
    adb = ADBManager()
    print("当前连接设备:", adb.get_device_list())