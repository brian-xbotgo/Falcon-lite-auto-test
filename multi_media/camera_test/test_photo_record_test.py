# -*- coding: utf-8 -*-
"""
测试用例：拍照功能测试
功能：图片拍照功能测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("A", name="拍照功能测试", module="多媒体", priority="P0")
def test_photo_capture(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A004：拍照功能测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行拍照功能测试")
    
    # 拍照
    success, output = ADBService.exec_shell(
        device_serial,
        "capture_photo",
        timeout=10
    )

    if success:
        return True, "拍照成功"
    else:
        return False, f"拍照失败: {output}"
