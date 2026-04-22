# -*- coding: utf-8 -*-
"""
测试用例：开关机检查
功能：设备开关机功能测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("A", name="开关机检查", module=Module.MISC, priority="P0")
def test_power_check(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A002：开关机检查
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行开关机检查测试")
    
    # 检查开机状态
    success, output = ADBService.exec_shell(
        device_serial,
        "uptime",
        timeout=10
    )

    if success and output.strip():
        return True, f"设备正常运行，开机时长: {output.strip()}"
    else:
        return False, "设备状态异常"
