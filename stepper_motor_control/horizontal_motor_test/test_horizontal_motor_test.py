# -*- coding: utf-8 -*-
"""
测试用例：水平电机测试
功能：水平方向步进电机运动测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("B", name="水平电机测试", module=Module.STEPPER_MOTOR, priority="P0", supported_devices=[1, 2, 3])
def test_horizontal_test(device_serial: str) -> tuple[bool | None, str, str] | tuple[bool, str]:
    """
    测试用例B005：水平电机测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行水平电机测试")
    
    # 获取设备类型
    device_type = ADBService._identify_device_type(device_serial)
    
    # 根据设备类型执行不同测试命令
    if device_type == 1:
        # Chameleon设备
        test_cmd = r'''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
        reset_cmd = r'''printf '\x00\x62\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
    elif device_type in (2, 3):
        # Falcon / Falcon-Air设备
        test_cmd = r'''printf '\x2A\x00\x00\x23\x28\x00\x02' | mosquitto_pub -h localhost -t AQR -s'''
        reset_cmd = r'''printf '\x2B' | mosquitto_pub -h localhost -t AQR -s'''
    else:
        return False, "未知设备类型"
    
    # 发送水平电机测试命令
    success, output = ADBService.exec_shell(
        device_serial,
        test_cmd,
        timeout=20
    )
    
    if not success:
        return False, f"水平电机测试失败: {output}"
    
    # 人工确认，测试服务会在确认后自动执行复位命令
    return None, "请观察水平电机运动是否正常，点击确认后发送复位命令", reset_cmd
    
    
