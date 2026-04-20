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
    module: str = ""
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