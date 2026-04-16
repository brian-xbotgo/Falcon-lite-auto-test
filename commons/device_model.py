# -*- coding: utf-8 -*-
"""
设备数据模型
功能：定义USB-ADB设备的统一数据结构，存储设备基础信息
"""
from dataclasses import dataclass

# 设备类型宏定义
DEVICE_TYPE_CHAMELEON = 1
DEVICE_TYPE_FALCON = 2
DEVICE_TYPE_FALCON_AIR = 3

# 设备类型名称映射
DEVICE_TYPE_NAMES = {
    0: "未知",
    1: "Chameleon",
    2: "Falcon",
    3: "Falcon-Air"
}

@dataclass
class DeviceModel:
    """
    USB设备数据模型
    :param serial: 设备序列号（唯一标识）
    :param device_name: 蓝牙设备名称
    :param conn_type: 连接方式，固定为USB
    :param status: 设备状态（在线/离线）
    :param version: 设备固件版本
    :param device_type: 设备类型标识
    """
    # 设备序列号（必填）
    serial: str = ""
    # 蓝牙设备名称
    device_name: str = ""
    # 连接方式（固定USB，不支持网络ADB）
    conn_type: str = "USB"
    # 设备状态：在线/离线
    status: str = "离线"
    # 固件版本号
    version: str = "unknown"
    # 设备类型标识
    device_type: int = 0
    
    def get_device_type_name(self) -> str:
        """获取设备类型名称"""
        return DEVICE_TYPE_NAMES.get(self.device_type, "未知")