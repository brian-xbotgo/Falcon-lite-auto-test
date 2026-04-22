# -*- coding: utf-8 -*-
"""
测试数据模型
功能：定义测试用例、测试结果的统一数据结构
"""
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """测试用例优先级枚举
    P0最高，P4最低
    """
    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    
    def __str__(self):
        return self.name


class Module(Enum):
    """测试模块枚举
    与功能目录一一对应
    """
    MISC = 1                 # 系统杂项
    BTWIFI = 2               # 蓝牙+WiFi
    BLE_CONFIGURE_WIFI = 3   # 蓝牙配网
    BLE_CENTRAL = 4          # BLE主机
    HTTP_AGENT = 5           # HTTP客户端
    MQTT_WRAPPER = 6         # MQTT通信
    OTA_UPDATE = 7           # OTA升级
    SDCARD_FIRMING = 8       # SD卡功能
    LVGL_APP = 9             # LVGL界面
    MULTI_MEDIA = 10         # 多媒体
    STEPPER_MOTOR = 11       # 步进电机
    BRUSHLESS_MOTOR = 12     # 无刷电机
    DETECT = 13              # AI检测
    TRACKING = 14            # 目标跟踪
    STREAM = 15              # 流媒体
    
    def __str__(self):
        # 返回中文名称用于显示
        module_names = {
            Module.MISC: "系统杂项",
            Module.BTWIFI: "蓝牙WiFi",
            Module.BLE_CONFIGURE_WIFI: "蓝牙配网",
            Module.BLE_CENTRAL: "BLE主机",
            Module.HTTP_AGENT: "HTTP客户端",
            Module.MQTT_WRAPPER: "MQTT通信",
            Module.OTA_UPDATE: "OTA升级",
            Module.SDCARD_FIRMING: "SD卡功能",
            Module.LVGL_APP: "LVGL界面",
            Module.MULTI_MEDIA: "多媒体",
            Module.STEPPER_MOTOR: "步进电机",
            Module.BRUSHLESS_MOTOR: "无刷电机",
            Module.DETECT: "AI检测",
            Module.TRACKING: "目标跟踪",
            Module.STREAM: "流媒体"
        }
        return module_names.get(self, "未知模块")


@dataclass
class TestModel:
    """
    测试用例数据模型
    :param test_id: 测试用例唯一ID
    :param module: 测试模块
    :param name: 测试用例名称
    :param test_type: 测试类型（自动化（A）/人工（B））
    :param priority: 用例优先级（P0/P1/P2/P3/P4）
    :param status: 执行状态（等待中/执行中/通过/失败/待确认）
    :param duration: 执行耗时（单位：秒）
    :param remark: 测试备注/失败原因
    """
    # 测试用例ID
    test_id: str = ""
    # 归属模块
    module: Module = Module.MISC
    # 用例名称
    name: str = ""
    # 测试类型：自动化/人工
    test_type: str = "自动化"
    # 优先级：P0(最高)/P1/P2/...
    priority: Priority = Priority.P1
    # 执行状态
    status: str = "等待中"
    # 执行耗时（秒）
    duration: float = 0.0
    # 备注信息
    remark: str = ""