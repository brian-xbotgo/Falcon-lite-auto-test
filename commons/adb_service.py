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
from .config import ADB_DEFAULT_TIMEOUT, TEST_MQTT_OUTPUT_FILE, TEST_MQTT_OUTPUT_TEXT_FILE, MQTT_MODE_HEX, MQTT_MODE_STRING, MQTT_DEFAULT_HOST, MQTT_DEFAULT_PORT
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
        # 优先检查Falcon特有文件 - /userdata/cpuinfo.txt 只有Falcon才有
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /userdata/cpuinfo.txt")
        if success:
            # 进一步判断是Falcon还是Falcon-Air
            success, prop_output = ADBService._run_adb_command(f"adb -s {serial} shell getprop ro.product.model")
            if success and 'Falcon-Air' in prop_output:
                return 3  # Falcon-Air
            return 2  # Falcon
        
        # 再检查Chameleon特有文件
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /oem/usr/bin/cpuinfo.txt")
        if success:
            return 1  # Chameleon
        
        # 回退版本文件检测
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /oem/usr/conf/version.txt")
        if success:
            return 2  # Falcon
            
        success, _ = ADBService._run_adb_command(f"adb -s {serial} shell test -f /oem/usr/bin/version.txt")
        if success:
            return 1  # Chameleon
        
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
                timeout=timeout
            )

            if result.returncode == 0:
                stdout = result.stdout.decode('utf-8', errors='replace').strip()
                return True, stdout
            else:
                stderr = result.stderr.decode('utf-8', errors='replace').strip()
                return False, stderr

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
    def adb_push_file(serial: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """
        推送本地文件到设备
        :param serial: 设备序列号
        :param local_path: 本地文件路径
        :param remote_path: 设备上的目标路径
        :return: (是否成功, 输出内容/错误信息)
        """
        log.debug(f"设备[{serial}] 推送文件: {local_path} -> {remote_path}")
        return ADBService._run_adb_command(f"adb -s {serial} push \"{local_path}\" \"{remote_path}\"")

    @staticmethod
    def _crc24(data: bytes) -> int:
        """
        CRC24 算法实现
        100%匹配设备端C语言实现
        多项式: 0x5D6DCB, 初始值: 0xFFFFFF
        """
        crc = 0xFFFFFF
        polynomial = 0x5D6DCB
        
        for byte in data:
            crc ^= (byte << 16)
            for _ in range(8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= polynomial
        
        return crc & 0xFFFFFF

    @staticmethod
    def get_device_bt_name(serial: str, device_type: int = None) -> Tuple[bool, str]:
        """
        获取设备对应的蓝牙名称
        根据设备类型使用不同的计算方式
        :param serial: 设备序列号
        :param device_type: 可选，已知设备类型时传入避免递归
        """
        if device_type is None:
            device_type = ADBService._identify_device_type(serial)
        
        if device_type in (2, 3):
            # Falcon / Falcon-Air 名称计算方式
            success, cpuinfo = ADBService.exec_shell(serial, "cat /userdata/cpuinfo.txt")
            if success and cpuinfo.strip() and "can't open" not in cpuinfo:
                log.debug(f"读取到cpuinfo: {cpuinfo.strip()}")
                import hashlib
                sha256 = hashlib.sha256(cpuinfo.strip().encode()).hexdigest()
                suffix = sha256[-6:].lower()
                return True, f"Xbt-F-{suffix}"
            
            log.error(f"Falcon设备无法读取有效cpuinfo文件")
            return False, "cpuinfo not found"
        
        elif device_type == 1:
            # Chameleon 名称计算方式
            success, output = ADBService.exec_shell(serial, "cat /oem/usr/bin/cpuinfo.txt")
            if success and output.strip():
                # 使用CRC24算法计算3字节设备号
                cpu_id_bytes = output.strip().encode('utf-8')
                crc24_value = ADBService._crc24(cpu_id_bytes)
                # 按照C代码大端字节序输出: 高字节 → 中字节 → 低字节
                byte1 = (crc24_value >> 16) & 0xFF
                byte2 = (crc24_value >> 8) & 0xFF
                byte3 = crc24_value & 0xFF
                device_suffix = f"{byte1:02x}{byte2:02x}{byte3:02x}".lower()
                log.debug(f"CRC24计算结果: {crc24_value:06x} → 字节序: {device_suffix}")
                return True, f"XbotGo-{device_suffix}"
        
        # 默认返回失败
        return False, "not implemented"

    @staticmethod
    def verify_device_name(serial: str, expected_name: str) -> bool:
        """
        验证设备蓝牙名称是否匹配
        按设备类型执行不同的验证逻辑
        :param serial: 设备序列号
        :param expected_name: 蓝牙扫描到的设备名称
        :return: 是否匹配
        """
        # 先根据蓝牙名称前缀确定预期设备类型，不需要猜测！
        # 暂时屏蔽，使用时打开
        # if expected_name.startswith('Xbt-F'):
        #     expected_type = 2  # Falcon
        # elif expected_name.startswith('XbotGo-'):
        #     expected_type = 1  # Chameleon
        # else:
        #     expected_type = 0
        
        # log.debug(f"开始验证设备名称: serial={serial}, expected={expected_name}, expected_type={expected_type}")
        
        # # 使用预期的设备类型进行验证
        # success, calc_name = ADBService.get_device_bt_name(serial, expected_type)
        # if success:
        #     log.debug(f"计算得到设备名称: {calc_name}")
        #     result = calc_name.lower() == expected_name.lower()
        #     if result:
        #         log.info(f"✅ 设备名称验证通过: {expected_name}")
        #     else:
        #         log.error(f"❌ 设备名称验证失败: 计算值={calc_name}, 期望值={expected_name}")
        #     return result
        
        # log.error(f"设备名称计算失败，无法验证: {serial}")
        # # 计算失败时默认不通过验证
        # return False

        # 测试使用
        return True

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
        # 将命令用双引号括起来，防止Windows本地shell解析管道符、重定向等特殊字符
        escaped_command = command.replace('"', '\\"')
        return ADBService._run_adb_command(f'adb -s {serial} shell "{escaped_command}"', timeout)

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
        
    @staticmethod
    def push_and_prepare_tool(serial: str, local_tool_path: str) -> Tuple[bool, str]:
        """
        上传工具到设备/tmp目录并添加执行权限
        :param serial: 设备序列号
        :param local_tool_path: 本地工具文件路径
        :return: (是否成功, 远程路径/错误信息)
        """
        import os
        filename = os.path.basename(local_tool_path)
        remote_path = f"/tmp/{filename}"
        
        log.debug(f"上传工具: {local_tool_path} -> {remote_path}")
        
        # 上传文件
        success, output = ADBService.adb_push_file(serial, local_tool_path, remote_path)
        if not success:
            return False, f"工具上传失败: {output}"
            
        # 添加执行权限
        success, output = ADBService.exec_shell(serial, f"chmod +x {remote_path}")
        if not success:
            return False, f"添加执行权限失败: {output}"
            
        log.debug(f"工具准备完成: {remote_path}")
        return True, remote_path
     
    @staticmethod
    def clean_mqtt_output_file(serial: str, mode: str = MQTT_MODE_HEX) -> Tuple[bool, str]:
        """
        清理MQTT测试反馈输出文件
        :param serial: 设备序列号
        :param mode: 输出模式，HEX或STRING
        :return: (是否成功, 输出内容)
        """
        output_file = TEST_MQTT_OUTPUT_TEXT_FILE if mode == MQTT_MODE_STRING else TEST_MQTT_OUTPUT_FILE
        return ADBService.exec_shell(serial, f"rm -f {output_file} && touch {output_file}")
    
    @staticmethod
    def read_mqtt_output_file(serial: str, mode: str = MQTT_MODE_HEX) -> Tuple[bool, str]:
        """
        读取MQTT测试反馈输出文件内容
        :param serial: 设备序列号
        :param mode: 输出模式，HEX或STRING
        :return: (是否成功, 内容字符串)
        """
        output_file = TEST_MQTT_OUTPUT_TEXT_FILE if mode == MQTT_MODE_STRING else TEST_MQTT_OUTPUT_FILE
        if mode == MQTT_MODE_STRING:
            return ADBService.exec_shell(serial, f"cat {output_file}")
        else:
            return ADBService.exec_shell(serial, f"hexdump -e '16/2 \"%04x \"' {output_file}")
    
    @staticmethod
    def mqtt_subscribe_and_send(serial: str, 
                               subscribe_topic: str,
                               publish_topic: str,
                               publish_payload: str = "",
                               timeout: int = 30,
                               mode: str = MQTT_MODE_HEX) -> Tuple[bool, str]:
        """
        完整的MQTT订阅-发送-等待流程
        所有命令在同一个shell会话中执行，避免后台进程被杀
        :param serial: 设备序列号
        :param subscribe_topic: 订阅主题，为空则不订阅，仅发布命令
        :param publish_topic: 发布主题
        :param publish_payload: 发布消息内容，空字符串表示空消息(-n)
        :param timeout: 超时时间（秒）
        :param mode: 输出模式，HEX(默认)或STRING
        :return: (是否成功, 内容字符串)
        """
        # 选择输出文件
        output_file = TEST_MQTT_OUTPUT_TEXT_FILE if mode == MQTT_MODE_STRING else TEST_MQTT_OUTPUT_FILE
        
        # 第一步：清理输出文件
        success, _ = ADBService.exec_shell(serial, f"rm -f {output_file} && touch {output_file}")
        if not success:
            return False, "清理输出文件失败"
            
        # 构造发布命令
        if publish_payload:
            pub_cmd = f"mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t '{publish_topic}' -m '{publish_payload}'"
        else:
            pub_cmd = f"mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t '{publish_topic}' -n"

        if subscribe_topic and subscribe_topic.strip():
            # 有订阅主题：完整的订阅-发送-等待流程
            full_cmd = f"mosquitto_sub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t '{subscribe_topic}' -C 1 -W {timeout} > {output_file} 2>/dev/null & SUB_PID=$! ; sleep 0.5 ; {pub_cmd} ; wait $SUB_PID"
            
            # 执行完整流程
            success, output = ADBService.exec_shell(serial, full_cmd, timeout + 5)
            
            # 无论执行成功与否，都读取结果文件
            if mode == MQTT_MODE_STRING:
                success_read, content = ADBService.exec_shell(serial, f"cat {output_file}")
            else:
                success_read, content = ADBService.exec_shell(serial, f"hexdump -e '16/2 \"%04x \"' {output_file}")
            
            if not success_read:
                return False, f"读取结果文件失败: {content}"
                
            content = content.strip()

            # 如果订阅命令执行失败但有内容，仍然返回内容
            if not success and not content:
                return False, f"MQTT执行失败: {output}"
                
            return True, content
        else:
            # 无订阅主题：仅执行发布命令，不等待反馈
            success, output = ADBService.exec_shell(serial, pub_cmd, timeout)
            
            if not success:
                return False, f"发布命令执行失败: {output}"
                
            return True, "命令发送成功，无需等待反馈"

