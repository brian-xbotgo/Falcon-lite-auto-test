# -*- coding: utf-8 -*-
"""
通用工具函数
所有项目通用的工具方法，不绑定任何业务逻辑
作者：wuzhibin
创建时间：2026-04-13
"""
import os
import time
import shutil
from typing import Optional
from .config import LOG_DIR, REPORT_DIR, FIRMWARE_DIR


def ensure_dirs() -> None:
    """
    确保所有必要的数据目录存在，不存在则自动创建
    程序启动时必须调用此方法
    """
    for dir_path in [LOG_DIR, REPORT_DIR, FIRMWARE_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def get_current_time_str(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    获取当前时间字符串，用于日志、报告文件名
    :param format: 时间格式
    :return: 格式化后的时间字符串
    """
    return time.strftime(format, time.localtime())


def format_file_size(size_bytes: int) -> str:
    """
    将字节数转换为可读的文件大小格式
    :param size_bytes: 文件大小（字节）
    :return: 格式化后的文件大小（如 1.2 MB）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def safe_delete_file(file_path: str) -> bool:
    """
    安全删除文件，不存在则返回 False
    :param file_path: 文件路径
    :return: 删除成功返回 True，失败返回 False
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return True
        return False
    except PermissionError:
        print(f"权限不足，无法删除文件：{file_path}")
        return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"删除文件异常：{file_path}，错误信息：{str(e)}")
        return False


def safe_delete_dir(dir_path: str) -> bool:
    """
    安全删除目录，不存在则返回 False
    :param dir_path: 目录路径
    :return: 删除成功返回 True，失败返回 False
    """
    try:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            return True
        return False
    except Exception:
        return False


def get_file_modify_time(file_path: str) -> Optional[str]:
    """
    获取文件最后修改时间
    :param file_path: 文件路径
    :return: 格式化后的修改时间，失败返回 None
    """
    try:
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        return None
    except Exception:
        return None


def check_device_time_sync(device_serial: str) -> tuple[bool, int]:
    """
    检查设备与PC的时间同步状态
    :param device_serial: 设备序列号
    :return: (是否同步, 时间差秒数)
    """
    from .adb_service import ADBService

    try:
        # 获取设备当前时间戳
        success, device_time_str = ADBService.exec_shell(device_serial, "date +%s")
        if not success:
            return False, 0

        device_timestamp = int(device_time_str.strip())
        pc_timestamp = int(time.time())
        time_diff = abs(device_timestamp - pc_timestamp)

        # 认为5分钟以内时间同步良好
        return time_diff <= 300, time_diff
    except Exception:
        return False, 0


def validate_recorded_file(device_serial: str, file_path: str, operation_start: float,
                          max_age_seconds: int = 300) -> tuple[bool, str]:
    """
    在设备端验证录制文件的生成时间，避免时间同步问题
    :param device_serial: 设备序列号
    :param file_path: 文件在设备上的路径
    :param operation_start: 操作开始时间戳（PC时间）
    :param max_age_seconds: 最大允许年龄（秒），默认5分钟
    :return: (验证结果, 详细信息)
    """
    from .adb_service import ADBService

    try:
        # 1. 检查时间同步状态
        is_synced, sync_diff = check_device_time_sync(device_serial)

        if not is_synced:
            from .log_service import log
            log.warning(f"检测到设备时间与PC不同步: {sync_diff}秒，将使用设备端验证")

        # 2. 在设备端获取文件修改时间
        # Android设备兼容性处理，尝试多种方法
        from .log_service import log

        # 方法1: 尝试使用busybox兼容的ls命令
        success, file_time_str = ADBService.exec_shell(device_serial,
            f"ls -la '{file_path}' 2>/dev/null | awk '{{print $6\" \"$7\" \"$8}}' || echo 'fallback'")
        log.debug(f"方法1输出: '{file_time_str}'")

        file_timestamp = None

        if success and file_time_str.strip() and file_time_str.strip() != 'fallback':
            # 解析ls输出的时间字符串，如 "Apr 28 10:51"
            try:
                time_str = file_time_str.strip()
                # 转换为Unix时间戳（这里简化处理，实际可能需要更复杂的解析）
                # 由于Android设备时间可能与PC不同步，我们直接使用文件名时间戳
                log.debug(f"ls时间字符串: '{time_str}'")
            except:
                pass

        # 方法2: 直接从文件名解析时间戳（最可靠的方法）
        filename = file_path.split('/')[-1]
        if 'IMG_' in filename or 'VID_' in filename:
            import re
            match = re.search(r'_(20\d{6})_(\d{6})_', filename)
            if match:
                date_str, time_str = match.groups()
                from datetime import datetime
                try:
                    dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                    file_timestamp = int(dt.timestamp())
                    log.debug(f"从文件名成功解析时间戳: {file_timestamp} ({dt})")
                except Exception as e:
                    log.error(f"文件名时间戳解析失败: {e}")
                    return False, f"文件名时间戳解析失败: {e}"
            else:
                return False, f"文件名格式不匹配时间戳模式: {filename}"

        # 方法3: 如果文件名解析也失败，尝试其他系统命令
        if file_timestamp is None:
            # 尝试stat命令的不同变体
            success, file_time_str = ADBService.exec_shell(device_serial,
                f"stat '{file_path}' 2>/dev/null | grep Modify | head -1 || echo '0'")
            log.debug(f"方法3输出: '{file_time_str}'")

            try:
                # 这里可能需要解析stat的输出格式
                if file_time_str and 'Modify' in file_time_str:
                    # 解析stat输出，简化处理
                    pass
                else:
                    file_timestamp = 0  # 降级到基本检查
            except:
                file_timestamp = 0

        if file_timestamp is None:
            return False, "所有文件时间获取方法都失败了"

        # 3. 获取设备当前时间进行对比
        success, device_time_str = ADBService.exec_shell(device_serial, "date +%s")
        device_timestamp = None

        if success and device_time_str.strip():
            try:
                device_timestamp = int(device_time_str.strip())
                from .log_service import log
                log.debug(f"设备当前时间戳: {device_timestamp}")

                # 计算时间差（设备时间 - 文件时间）
                time_diff = device_timestamp - file_timestamp

                # 验证文件是否在合理时间范围内生成
                if time_diff < 0:
                    return False, f"文件时间异常: 文件时间晚于设备当前时间 {abs(time_diff)}秒"

                if time_diff > max_age_seconds:
                    return False, f"文件生成时间超出限制: {time_diff}秒（最大允许{max_age_seconds}秒）"

            except ValueError:
                from .log_service import log
                log.warning(f"设备时间戳解析失败: '{device_time_str}'，使用简化验证")

        # 4. 如果设备时间获取失败，使用基于operation_start的验证
        if device_timestamp is None:
            from .log_service import log
            current_time = time.time()
            time_since_operation = current_time - operation_start

            log.debug(f"使用PC时间验证，操作开始: {operation_start}, 当前: {current_time}, 经过: {time_since_operation}秒")

            # 验证文件时间是否在操作开始后的合理范围内
            if time_since_operation < 0:
                return False, f"操作时间异常: 当前时间早于操作开始时间"

            if time_since_operation > max_age_seconds:
                return False, f"文件生成时间超出限制: {time_since_operation}秒（最大允许{max_age_seconds}秒）"

        # 5. 验证成功
        time_diff_desc = f"{device_timestamp - file_timestamp}秒" if device_timestamp else f"约{int(time.time() - operation_start)}秒"
        return True, f"文件验证通过，生成时间差: {time_diff_desc}"

    except Exception as e:
        return False, f"文件验证异常: {str(e)}"


def get_device_timestamp(device_serial: str) -> Optional[int]:
    """
    获取设备当前时间戳
    :param device_serial: 设备序列号
    :return: 时间戳，失败返回 None
    """
    from .adb_service import ADBService

    try:
        success, time_str = ADBService.exec_shell(device_serial, "date +%s")
        if success:
            return int(time_str.strip())
        return None
    except Exception:
        return None


def get_file_timestamp_on_device(device_serial: str, file_path: str) -> Optional[int]:
    """
    在设备端获取文件的修改时间戳
    :param device_serial: 设备序列号
    :param file_path: 文件在设备上的路径
    :return: 文件时间戳，失败返回 None
    """
    from .adb_service import ADBService

    try:
        success, time_str = ADBService.exec_shell(device_serial, f"stat -c %Y '{file_path}' 2>/dev/null || echo 0")
        if success:
            return int(time_str.strip())
        return None
    except Exception:
        return None