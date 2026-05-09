# -*- coding: utf-8 -*-
"""
测试用例：俯仰电机测试
功能：自动测试俯仰方向步进电机运动
作者：wuzhibin
创建时间：2026-04-16
"""
import os
from commons import ADBService, log, register_test_case, Priority, Module, TOOLS_DIR


@register_test_case("A", name="俯仰电机测试", module=Module.STEPPER_MOTOR, priority=Priority.P0, supported_devices=[2, 3], test_case_number='')
def test_pitch_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A：俯仰电机测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行俯仰电机自动化测试")
    
    try:
        # 第一步：推送测试脚本
        script_local = os.path.join(TOOLS_DIR, "shell_script", "pitch_motor_test.sh")
        log.info("推送pitch_motor_test.sh到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, script_local)
        if not success:
            log.error(f"推送测试脚本失败: {remote_path}")
            return False, f"测试脚本推送失败: {remote_path}"
        
        log.info("测试脚本准备完成")
        
        # 第二步：执行测试脚本
        log.info("执行俯仰电机测试脚本")
        success, script_output = ADBService.exec_shell(device_serial, f"{remote_path}", timeout=30)
        if not success:
            log.error(f"脚本执行失败: {script_output}")
            # 清理脚本
            ADBService.exec_shell(device_serial, f"rm -rf {remote_path}")
            return False, f"脚本执行失败: {script_output}"
            
        log.debug(f"脚本输出:\n{script_output}")
        
        # 第三步：解析输出并自动判断
        motor_status_normal = False
        
        # 检查输出中是否包含motor status:normal
        for line in script_output.split('\n'):
            line = line.strip()
            if line == "motor status:normal":
                motor_status_normal = True
                break
        
        # 第四步：清理脚本文件
        ADBService.exec_shell(device_serial, f"rm -rf {remote_path}")
        
        # 返回测试结果
        if motor_status_normal:
            log.info("俯仰电机测试通过")
            return True, f"俯仰电机测试通过, {script_output.strip()}"
        else:
            log.error(f"俯仰电机测试失败: {script_output}")
            return False, f"俯仰电机测试失败, {script_output.strip()}"
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"
    
    
