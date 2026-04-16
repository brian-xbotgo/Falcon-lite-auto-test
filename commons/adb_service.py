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
    _last_device_status = None  # 记忆上次设备状态，避免重复日志

    @staticmethod
    def _identify_device_type(serial: str) -> int:
        """
        识别设备类型
        :param serial: 设备序列号
        :return: 设备类型标识
        """
        # 优先通过版本文件存在性识别 - 最准确可靠
        # 检查Falcon系列路径
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /oem/usr/conf/version.txt")
        if success:
            # 必须同时匹配设备名称前缀
            success, bt_name = ADBService.get_device_bt_name(serial)
            if success:
                if bt_name.startswith('Xbt-F'):
                    # 进一步判断是Falcon还是Falcon-Air
                    success, prop_output = ADBService._run_adb_command(f"adb -s {serial} shell getprop ro.product.model")
                    if success and 'Falcon-Air' in prop_output:
                        return 3  # Falcon-Air
                    return 2  # Falcon
        
        # 检查Chameleon路径
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /oem/usr/bin/version.txt")
        if success:
            return 1  # Chameleon
        
        # 再尝试蓝牙名称识别
        success, bt_name = ADBService.get_device_bt_name(serial)
        if success:
            if bt_name.startswith('Xbt-F'):
                return 2  # Falcon
            elif bt_name.startswith('Xbotgo-'):
                return 1  # Chameleon
        
        # 尝试通过getprop获取设备型号
        success, prop_output = ADBService._run_adb_command(f"adb -s {serial} shell getprop ro.product.model")
        if success:
            prop_output = prop_output.strip()
            if prop_output.startswith('Xbt-F'):
                return 2
            elif prop_output.startswith('Xbotgo-'):
                return 1
            elif 'Falcon-Air' in prop_output:
                return 3
        
        # 默认返回0（未知）
        return 0

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
                    
                    # 识别设备类型
                    device_type = ADBService._identify_device_type(serial)
                    device.device_type = device_type
                    
                    # 获取设备固件版本
                    version_success, version = ADBService.get_device_version(serial, device_type)
                    if version_success:
                        device.version = version

                    devices.append(device)
                    log.info(f"发现USB设备: {serial} 类型: {device.get_device_type_name()}")

        log.debug(f"扫描完成，共发现 {len(devices)} 个USB设备")
        return devices

    @staticmethod
    def timer_scan_devices() -> List[DeviceModel]:
        """
        定时器扫描所有USB连接的ADB设备
        :return: 设备列表
        """
        success, output = ADBService._run_adb_command("adb devices")
        if not success:
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
                    
                    # 识别设备类型
                    device_type = ADBService._identify_device_type(serial)
                    device.device_type = device_type
                    
                    # 获取设备固件版本
                    version_success, version = ADBService.get_device_version(serial, device_type)
                    if version_success:
                        device.version = version

                    devices.append(device)

        # 状态变化时才输出日志
        current_status = "online" if devices else "offline"
        if current_status != ADBService._last_device_status:
            if current_status == "offline" and ADBService._last_device_status == "online":
                log.warning("设备已离线")
            ADBService._last_device_status = current_status

        return devices

    @staticmethod
    def get_device_version(serial: str, device_type: int = 0) -> Tuple[bool, str]:
        """
        获取设备固件版本
        :param serial: 设备序列号
        :param device_type: 设备类型标识
        :return: (是否成功, 版本号)
        """
        if device_type == 1:
            # Chameleon设备 - 读取旧路径
            success, output = ADBService._run_adb_command(f"adb -s {serial} shell cat /oem/usr/bin/version.txt")
            if success and output:
                version_info = {}
                for line in output.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        version_info[key.strip()] = value.strip()
                
                hw = version_info.get('firmware_hardware', '0')
                sys = version_info.get('firmware_system', '0')
                app = version_info.get('firmware_app', '0')
                version = f"{hw}.{sys}.{app}"
                return True, version
        elif device_type in (2, 3):
            # Falcon / Falcon-Air设备 - 读取新路径
            success, output = ADBService._run_adb_command(f"adb -s {serial} shell cat /oem/usr/conf/version.txt")
            if success and output:
                version_info = {}
                for line in output.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        version_info[key.strip()] = value.strip()
                
                api = version_info.get('api_version', '0')
                sub = version_info.get('sub_version', '0')
                patch = version_info.get('patch_version', '0')
                version = f"{api}.{sub}.{patch}"
                return True, version
        
        return False, "unknown"

    @staticmethod
    def adb_pull_file(serial: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """
        从设备拉取文件到本地
        :param serial: 设备序列号
        :param remote_path: 设备上的文件路径
        :param local_path: 本地保存路径
        :return: (是否成功, 输出内容/错误信息)
        """
        log.debug(f"设备[{serial}] 拉取文件: {remote_path} -> {local_path}")
        return ADBService._run_adb_command(f"adb -s {serial} pull \"{remote_path}\" \"{local_path}\"")

    @staticmethod
    def get_device_bt_name(serial: str) -> Tuple[bool, str]:
        """
        获取设备对应的蓝牙名称
        设备名称计算方式: Xbt-F-xxxxxx
        当前先注释，使用Falcon-Air测试设备时启用
        """
        # Falcon-Air名称计算方式
        # success, output = ADBService.exec_shell(serial, "cat /userdata/cpuinfo.txt | sha256sum | tail -c 6")
        # if success:
        #     return True, f"Xbt-F-{output.strip().lower()}"
        
        # 暂时不做检验
        return False, "not implemented"

    @staticmethod
    def verify_device_name(serial: str, expected_name: str) -> bool:
        """
        验证设备蓝牙名称是否匹配
        :param serial: 设备序列号
        :param expected_name: 蓝牙扫描到的设备名称
        :return: 是否匹配
        """
        # 变色龙测试设备暂时直接返回True，后续启用名称校验
        return True
        
        # Falcon-Air设备校验逻辑（后续取消注释）
        # success, calc_name = ADBService.get_device_bt_name(serial)
        # return success and calc_name.lower() == expected_name.lower()

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

