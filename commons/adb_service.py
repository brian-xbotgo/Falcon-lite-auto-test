# -*- coding: utf-8 -*-
"""
ADB服务模块
功能：USB有线ADB设备扫描、连接、命令执行，仅支持USB连接
作者：wuzhibin
创建时间：2026-04-13
"""
import subprocess
import re
import time
from typing import List, Optional, Tuple
from .device_model import DeviceModel
from .config import ADB_DEFAULT_TIMEOUT
from .log_service import log


class ADBService:
    """
    USB-ADB服务类
    仅支持USB有线连接，不支持网络ADB
    """

    @staticmethod
    def _run_adb_command(command: str, timeout: int = ADB_DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """
        内部执行ADB命令的通用方法
        :param command: ADB命令字符串
        :param timeout: 超时时间（秒）
        :return: (是否成功, 输出内容/错误信息)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8"
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, f"执行异常: {str(e)}"

    @staticmethod
    def scan_devices() -> List[DeviceModel]:
        """
        扫描所有USB连接的ADB设备
        :return: 设备列表
        """
        log.debug("开始扫描USB-ADB设备")

        success, output = ADBService._run_adb_command("adb devices")
        if not success:
            log.error(f"扫描设备失败: {output}")
            return []

        devices = []
        lines = output.strip().split('\n')

        # 跳过第一行标题行
        for line in lines[1:]:
            if not line.strip():
                continue

            # 解析设备行 格式: 序列号  状态
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                serial = parts[0]
                status = parts[1]

                # 只处理USB设备
                if status == "device":
                    device = DeviceModel(serial=serial, status="在线")
                    # 获取设备固件版本
                    version_success, version = ADBService.get_device_version(serial)
                    if version_success:
                        device.version = version

                    # 检查Root权限
                    root_success, is_rooted = ADBService.check_root(serial)
                    if root_success:
                        device.is_rooted = is_rooted

                    devices.append(device)
                    log.info(f"发现USB设备: {serial}")

        log.debug(f"扫描完成，共发现 {len(devices)} 个USB设备")
        return devices

    @staticmethod
    def get_device_version(serial: str) -> Tuple[bool, str]:
        """
        获取设备固件版本
        :param serial: 设备序列号
        :return: (是否成功, 版本号)
        """
        success, output = ADBService._run_adb_command(f"adb -s {serial} shell getprop ro.build.display.id")
        if success and output:
            return True, output.strip()
        return False, "unknown"

    @staticmethod
    def check_root(serial: str) -> Tuple[bool, bool]:
        """
        检查设备是否拥有Root权限
        :param serial: 设备序列号
        :return: (是否成功, 是否Root)
        """
        success, output = ADBService._run_adb_command(f"adb -s {serial} shell su -c 'echo root'")
        if success and "root" in output:
            return True, True
        return True, False

    @staticmethod
    def exec_shell(serial: str, command: str, timeout: int = ADB_DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """
        在指定设备上执行Shell命令
        :param serial: 设备序列号
        :param command: Shell命令
        :param timeout: 超时时间
        :return: (是否成功, 输出内容/错误信息)
        """
        log.debug(f"设备[{serial}] 执行命令: {command}")
        return ADBService._run_adb_command(f"adb -s {serial} shell {command}", timeout)

    @staticmethod
    def reboot(serial: str) -> bool:
        """
        重启设备
        :param serial: 设备序列号
        :return: 是否成功
        """
        log.info(f"重启设备: {serial}")
        success, _ = ADBService._run_adb_command(f"adb -s {serial} reboot")
        return success

    @staticmethod
    def wait_for_device(serial: str, timeout: int = 120) -> bool:
        """
        等待设备上线
        :param serial: 设备序列号
        :param timeout: 等待超时时间（秒）
        :return: 是否成功
        """
        log.debug(f"等待设备上线: {serial}")
        start_time = time.time()

        while time.time() - start_time < timeout:
            devices = ADBService.scan_devices()
            for device in devices:
                if device.serial == serial and device.status == "在线":
                    log.info(f"设备已上线: {serial}")
                    return True
            time.sleep(1)

        log.error(f"等待设备超时: {serial}")
        return False
