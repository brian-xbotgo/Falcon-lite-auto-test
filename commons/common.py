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