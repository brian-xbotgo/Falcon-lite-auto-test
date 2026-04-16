# -*- coding: utf-8 -*-
"""
测试用例：自动追踪测试
功能：目标自动追踪功能测试
作者：系统自动生成
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("A", name="自动追踪测试", module="目标跟踪", priority="P0", supported_devices=[1, 2, 3])
def test_auto_track(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A008：自动追踪测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行自动追踪测试")
    
    # 获取设备类型
    device_type = ADBService._identify_device_type(device_serial)
    
    # 根据设备类型执行不同命令
    if device_type == 1:
        # Chameleon设备
        cmd = "ai_track test 10"
    elif device_type in (2, 3):
        # Falcon / Falcon-Air设备
        cmd = "auto_track test 10"
    else:
        return False, "未知设备类型"
    
    # 启动自动追踪功能测试
    success, output = ADBService.exec_shell(
        device_serial,
        cmd,
        timeout=15
    )

    if success:
        return True, "自动追踪功能正常"
    else:
        return False, f"自动追踪测试失败: {output}"
