# -*- coding: utf-8 -*-
"""
测试用例：睡眠唤醒测试
功能：睡眠唤醒功能测试
作者：系统自动生成
创建时间：2026-04-24
"""
import time
from commons import ADBService, log, register_test_case, Module, Priority


@register_test_case("B", name="睡眠唤醒测试", module=Module.MISC, priority=Priority.P2, supported_devices=[2, 3], test_case_number='')
def test_wakeup_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B：睡眠唤醒测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行睡眠唤醒测试")

    # time.sleep(35)
    # 发送ADB命令：printf '\x01' | mosquitto_pub -h localhost -t "FSR" -s
    test_cmd = r'''printf '\x01' | mosquitto_pub -h localhost -t "FSR" -s'''
    success, output = ADBService.exec_shell(device_serial, test_cmd)

    if not success:
        return False, f"发送唤醒命令失败: {output}"

    # 通知人工观察设备屏幕是否唤醒，侧灯是否闪烁
    return None, "请观察设备屏幕是否唤醒，侧灯是否闪烁"