# -*- coding: utf-8 -*-
"""
设备重连服务模块
功能：设备重连和重启后重连，用于配合测试流程中需要重启的场景
作者：系统自动生成
创建时间：2026-05-06
"""
import time
from typing import Tuple
from .adb_service import ADBService
from .log_service import log


class ReconnectService:
    """
    设备重连服务类
    
    设计原则：
    - 仅在测试流程中显式调用，不自动重连断线
    - 支持配置等待时间和重连次数
    - 返回清晰的成功/失败状态和消息
    """
    
    # 默认参数
    DEFAULT_WAIT_TIME = 30      # 重启后等待时间（秒）
    DEFAULT_MAX_ATTEMPTS = 10   # 最大重连次数
    DEFAULT_RETRY_INTERVAL = 5  # 重连间隔（秒）
    
    @staticmethod
    def reconnect(
        serial: str,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_interval: int = DEFAULT_RETRY_INTERVAL
    ) -> Tuple[bool, str]:
        """
        设备重连（不重启）
        
        仅当设备当前未连接时执行重连流程
        
        :param serial: 设备序列号
        :param max_attempts: 最大重连次数，默认10次
        :param retry_interval: 重连间隔（秒），默认5秒
        :return: (是否成功, 消息)
        """
        log.info(f"开始设备重连流程: {serial}")
        
        # 检查当前连接状态
        devices = ADBService.scan_devices()
        for device in devices:
            if device.serial == serial and device.status == "在线":
                log.info(f"设备已在线，无需重连: {serial}")
                return True, "设备已在线，无需重连"
        
        # 设备未连接，开始重连循环
        log.info(f"设备未连接，开始重连循环，最多{max_attempts}次")
        for attempt in range(1, max_attempts + 1):
            log.debug(f"重连尝试 {attempt}/{max_attempts}")
            
            devices = ADBService.scan_devices()
            for device in devices:
                if device.serial == serial and device.status == "在线":
                    log.info(f"重连成功: {serial}")
                    return True, f"设备重连成功（第{attempt}次尝试）"
            
            if attempt < max_attempts:
                log.debug(f"等待{retry_interval}秒后重试")
                time.sleep(retry_interval)
        
        # 所有尝试失败
        log.error(f"重连失败: {serial} 在{max_attempts}次尝试后未连接")
        return False, f"设备重连失败，经过{max_attempts}次尝试"
    
    @staticmethod
    def reboot_and_reconnect(
        serial: str,
        wait_time: int = DEFAULT_WAIT_TIME,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_interval: int = DEFAULT_RETRY_INTERVAL
    ) -> Tuple[bool, str]:
        """
        设备重启并重连
        
        流程：
        1. 执行reboot命令
        2. 等待设备完全断开
        3. 等待指定时间(wait_time)
        4. 调用reconnect方法进行重连
        
        :param serial: 设备序列号
        :param wait_time: 重启后等待时间（秒），默认30秒
        :param max_attempts: 最大重连次数，默认10次
        :param retry_interval: 重连间隔（秒），默认5秒
        :return: (是否成功, 消息)
        """
        log.info(f"开始设备重启重连流程: {serial}")
        
        # 步骤1：执行重启命令
        log.debug("步骤1：发送重启命令")
        success, result = ADBService._run_adb_command(f"adb -s {serial} reboot")
        if not success:
            return False, f"发送重启命令失败: {result}"
        
        log.debug("重启命令已发送，等待设备断开...")
        
        # 步骤2：等待设备断开（最多10秒）
        log.debug("步骤2：等待设备断开")
        for _ in range(10):
            devices = ADBService.scan_devices()
            device_exists = any(d.serial == serial for d in devices)
            if not device_exists:
                log.debug("设备已断开")
                break
            time.sleep(1)
        else:
            log.warning("设备断开超时，但继续等待重连")
        
        # 步骤3：等待指定时间
        log.info(f"步骤3：等待{wait_time}秒后开始重连")
        time.sleep(wait_time)
        
        # 步骤4：调用重连方法
        log.debug("步骤4：调用重连方法")
        return ReconnectService.reconnect(serial, max_attempts, retry_interval)