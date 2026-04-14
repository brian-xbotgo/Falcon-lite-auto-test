# -*- coding: utf-8 -*-
"""
测试用例A001：读取设备版本号
功能：读取/oem/usr/bin/version.txt或/proc/version获取设备版本信息
作者：wuzhibin
创建时间：2026-04-14
"""
from commons import ADBService, DEFAULT_TEST_TIMEOUT, log, register_test_case


@register_test_case("A001")
def test_version_read(device_serial: str) -> tuple[bool, str]:
    """测试用例A001：读取设备版本号 /oem/usr/bin/version.txt"""
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
    else:
        # 兼容性处理：如果文件不存在，尝试通用版本获取
        log.debug("尝试通用版本获取方式")
        success2, output2 = ADBService.exec_shell(device_serial, "cat /proc/version")
        if success2 and output2.strip():
            return True, f"内核版本: {output2.strip()[:100]}..."
        return False, output
