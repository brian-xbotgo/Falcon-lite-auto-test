# -*- coding: utf-8 -*-
"""
测试用例：版本信息读取
功能：读取设备版本号并验证格式
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case, Module


@register_test_case("A", name="版本信息读取", module=Module.MISC, priority="P0")
def test_version_read(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A001：版本信息读取
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行版本信息读取测试")
    
    # 获取设备类型
    device_type = ADBService._identify_device_type(device_serial)
    
    # 根据设备类型读取不同路径的version.txt
    if device_type == 1:
        # Chameleon设备
        success, output = ADBService.exec_shell(
            device_serial,
            "cat /oem/usr/bin/version.txt",
            timeout=30
        )
    elif device_type in (2, 3):
        # Falcon / Falcon-Air设备
        success, output = ADBService.exec_shell(
            device_serial,
            "cat /oem/usr/conf/version.txt",
            timeout=30
        )
    else:
        return False, "未知设备类型"

    if success and output.strip():
        log.debug(f"读取到版本信息: {output.strip()}")
        return True, f"版本号: {output.strip()}"
    else:
        return False, "文件内容异常"
