# -*- coding: utf-8 -*-
"""
测试用例：音频录制测试
功能：音频录制功能测试
作者：wuzhibin
创建时间：2026-04-16
"""
from commons import ADBService, log, register_test_case


@register_test_case("A", name="音频录制测试", module="多媒体", priority="P0")
def test_audio_record(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A005：音频录制测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行音频录制测试")
    
    # 录制3秒音频
    success, output = ADBService.exec_shell(
        device_serial,
        "record_audio 3",
        timeout=8
    )

    if success:
        return True, "音频录制成功"
    else:
        return False, f"音频录制失败: {output}"
