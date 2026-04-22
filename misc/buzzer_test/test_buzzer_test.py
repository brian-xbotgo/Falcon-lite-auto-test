# -*- coding: utf-8 -*-
"""
测试用例：蜂鸣器测试检查
功能：蜂鸣器发声测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("B", name="蜂鸣器测试", module=Module.MISC, priority="P1", supported_devices=[2, 3])
def test_beep_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例B002：蜂鸣器测试检查
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行蜂鸣器测试")
    
    # 发送蜂鸣器命令
    success, output = ADBService.exec_shell(
        device_serial,
        r'''mosquitto_pub -h localhost -t "CGA" -m "$(printf '\xFE')"''',
        timeout=2
    )

    if not success:
        return False, f"发送蜂鸣器命令失败: {output}"

    return None, "请确认蜂鸣器是否发出正常提示音"
