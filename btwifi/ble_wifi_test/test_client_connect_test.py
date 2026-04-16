# -*- coding: utf-8 -*-
"""
测试用例：手机连接设备测试
功能：BLE蓝牙连接测试
作者：系统自动生成
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("B", name="手机连接设备测试", module="BLE蓝牙", priority="P1")
def test_connect_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B003：手机连接设备测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行手机连接设备测试")
    
    # 启用BLE广播
    success, output = ADBService.exec_shell(
        device_serial,
        "ble_advertise on",
        timeout=5
    )

    return True, "请使用手机蓝牙搜索并连接设备，确认连接正常"
