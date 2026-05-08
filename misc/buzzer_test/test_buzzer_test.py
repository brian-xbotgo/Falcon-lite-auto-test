# -*- coding: utf-8 -*-
"""
测试用例：蜂鸣器测试检查
功能：蜂鸣器发声测试
作者：wuzhibin
创建时间：2026-04-16
"""
import os
import time
import re
from datetime import datetime
from commons import ADBService, log, register_test_case, Module, Priority


@register_test_case("B", name="蜂鸣器测试", module=Module.MISC, priority="P1", supported_devices=[2, 3], test_case_number='')
def test_beep_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B002：蜂鸣器测试检查
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行蜂鸣器测试")
    
    # 改用其他方案 AIR命令被注释
    # # 发送蜂鸣器命令
    # success, output = ADBService.exec_shell(
    #     device_serial,
    #     r'''mosquitto_pub -t "FIR" -m "$(printf '\x01')"''',
    #     timeout=2
    # )
    # time.sleep(2)
    # success, output = ADBService.exec_shell(
    #     device_serial,
    #     r'''mosquitto_pub -t "FIR" -m "$(printf '\x01')"''',
    #     timeout=2
    # )

    # success, output = ADBService.exec_shell(
    #     device_serial,
    #     r'''printf '\x02' | mosquitto_pub -h localhost -t "AIR" -s''',
    #     timeout=2
    # )

    success, output = ADBService.exec_shell(device_serial, "ls -la /tmp/record_test")
    if not success or "No such file" in output:
        record_test_local = os.path.join(os.getcwd(), "tools", "record_tool", "record_test")
        log.info("推送record_test工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
        if not success:
            log.error(f"推送record_test失败: {remote_path}")
            return False, f"推送record_test失败: {remote_path}"

    log.info("工具准备完成")
    log.info("发送蜂鸣器命令")
    success, output = ADBService.exec_shell(device_serial, "/tmp/record_test m_key 1 1")
    if not success:
        return False, f"发送蜂鸣器命令失败: {output}"
    time.sleep(4)
    success, output = ADBService.exec_shell(device_serial, "/tmp/record_test m_key 1 0")
    if not success:
        return False, f"发送蜂鸣器命令失败: {output}"

    return None, "请确认蜂鸣器是否发出正常提示音"
