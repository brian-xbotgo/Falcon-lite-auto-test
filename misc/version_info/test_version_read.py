# -*- coding: utf-8 -*-
"""
自动测试用例：读取设备版本号
功能：读取/oem/usr/bin/version.txt或/proc/version获取设备版本信息
作者：wuzhibin
创建时间：2026-04-14
"""
from commons import ADBService, DEFAULT_TEST_TIMEOUT, log, register_test_case


@register_test_case("A", name="设备版本号读取", module="系统", priority="P0")
def test_version_read(device_serial: str) -> tuple[bool, str]:
    """自动测试用例：读取设备版本号 /oem/usr/bin/version.txt"""
    log.debug("读取设备版本文件: /oem/usr/bin/version.txt")
    success, output = ADBService.exec_shell(
        device_serial,
        "cat /oem/usr/bin/version.txt",
        timeout=DEFAULT_TEST_TIMEOUT
    )

    if success and output.strip():
        return True, f"版本号: {output.strip()}"
    elif success:
        return False, "版本文件为空"
        return False, output
