# -*- coding: utf-8 -*-
"""
测试用例：LED指示灯检查
功能：人工检查LED指示灯状态
作者：wuzhibin
创建时间：2026-04-16
"""
import time
from commons import ADBService, log, register_test_case, Module


@register_test_case("B", name="LED指示灯检查", module=Module.MISC, priority="P1", test_case_number='')
def test_led_check(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B001：LED指示灯检查
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行LED指示灯检查测试")
    
    # 获取设备类型
    device_type = ADBService._identify_device_type(device_serial)
    
    # time.sleep(35)
    # 根据设备类型发送不同的闪烁命令
    if device_type == 1:
        # Chameleon设备
        cmd = r'''mosquitto_pub -h localhost -t "L" -m "$(printf '\x03')"'''
    elif device_type in (2, 3):
        # Falcon / Falcon-Air设备
        cmd = r"mosquitto_pub -h localhost -t FSR -m $'\x01'"
        
    else:
        return False, "未知设备类型"
    
    # 发送LED闪烁命令
    success, output = ADBService.exec_shell(
        device_serial,
        cmd,
        timeout=10
    )
    success, output = ADBService.exec_shell(
        device_serial,
        cmd,
        timeout=10
    )

    if not success:
        return False, f"发送LED命令失败: {output}"

    return None, "请观察设备侧灯是否闪烁"
