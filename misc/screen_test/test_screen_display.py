# -*- coding: utf-8 -*-
"""
测试用例：屏幕显示测试
功能：屏幕显示功能测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case, DeviceModel


@register_test_case("B", name="屏幕显示测试", module="系统杂项", priority="P1")
def test_screen_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B004：屏幕显示测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行屏幕显示测试")
    
    # 显示测试图案
    success, output = ADBService.exec_shell(
        device_serial,
        "display_test_pattern",
        timeout=5
    )

    return True, "请观察屏幕显示是否正常，有无坏点、色差、条纹"
