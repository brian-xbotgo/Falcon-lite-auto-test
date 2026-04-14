# -*- coding: utf-8 -*-
"""
自动测试用例：网络连通性测试
功能：执行ping命令测试网络连通性
作者：wuzhibin
创建时间：2026-04-14
"""
from commons import ADBService, log, register_test_case


@register_test_case("A", name="网络连通性测试", module="网络", priority="P0")
def test_network_connectivity(device_serial: str) -> tuple[bool, str]:
    """自动测试用例：网络连通性测试"""
    log.debug("执行网络连通性测试: ping -c 3 192.168.1.1")
    success, output = ADBService.exec_shell(
        device_serial,
        "ping -c 3 192.168.1.1",
        timeout=30
    )

    if success and "0% packet loss" in output:
        return True, "网络连通正常"
    elif success:
        return False, f"网络丢包: {output.splitlines()[-1]}"
    else:
        return False, output
