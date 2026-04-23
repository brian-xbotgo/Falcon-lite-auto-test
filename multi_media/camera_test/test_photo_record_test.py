# -*- coding: utf-8 -*-
"""
测试用例：拍照功能测试
功能：自动测试拍照功能并验证图片完整性
作者：wuzhibin
创建时间：2026-04-16
"""
import os
import time
import re
from datetime import datetime
from commons import ADBService, log, register_test_case, Priority, Module


@register_test_case("A", name="拍照功能测试", module=Module.MULTI_MEDIA, priority=Priority.P1, supported_devices=[2, 3])
def test_photo_capture(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A：拍照功能测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行拍照功能自动化测试")
    
    try:
        # 第二步：推送所需工具
        tools_ready = True
        
        # 推送record_test工具
        record_test_local = os.path.join(os.getcwd(), "tools", "record_tool", "record_test")
        log.info("推送record_test工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
        if not success:
            log.error(f"推送record_test失败: {remote_path}")
            tools_ready = False
        
        # 推送IMG_check.sh工具
        img_check_local = os.path.join(os.getcwd(), "tools", "shell_script", "IMG_check.sh")
        log.info("推送IMG_check.sh工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, img_check_local)
        if not success:
            log.error(f"推送IMG_check.sh失败: {remote_path}")
            tools_ready = False
        
        if not tools_ready:
            return False, "必要工具推送失败，无法继续测试"
            
        log.info("所有工具准备完成")
        
        # 第三步：执行拍照流程
        log.info("开始执行拍照流程")
        
        # 拍照
        log.info("执行拍照命令")
        success, _ = ADBService.exec_shell(device_serial, "/tmp/record_test photo 2")
        if not success:
            return False, "拍照命令执行失败"
        time.sleep(2)  # 等待文件写入完成
        
        # 获取最新拍摄的图片文件路径
        log.info("获取最新拍摄的图片文件")
        success, output = ADBService.exec_shell(device_serial, "ls -t /sdcard/falcon/$(date +%Y%m%d)/*.jpg | head -1")
        if not success or not output.strip():
            return False, "未找到拍摄的图片文件"
            
        photo_path = output.strip()
        log.info(f"拍摄文件路径: {photo_path}")
        
        # 第三点五步：文件名校验
        filename = os.path.basename(photo_path)
        log.debug(f"文件名校验: {filename}")
        
        # IMG_YYYYMMDD_HHMMSS_XX.jpg 格式校验
        photo_pattern = r'^IMG_(\d{8})_(\d{6})_\d{2}\.jpg$'
        match = re.match(photo_pattern, filename)
        
        if not match:
            log.error(f"文件名格式异常: {filename}")
            return False, f"文件名格式异常: {filename}"
            
        # 时间范围校验 (1分钟内)
        file_date = match.group(1)
        file_time = match.group(2)
        try:
            file_datetime = datetime.strptime(f"{file_date}{file_time}", "%Y%m%d%H%M%S")
            current_datetime = datetime.now()
            time_diff = abs((current_datetime - file_datetime).total_seconds())
            
            if time_diff > 60:
                log.error(f"文件时间超出范围: {file_datetime}, 当前时间: {current_datetime}, 差值: {time_diff}秒")
                return False, f"文件时间超出1分钟范围: {file_datetime}"
                
            log.debug(f"文件名校验通过，时间差: {time_diff:.1f}秒")
        except Exception as e:
            log.error(f"时间解析失败: {str(e)}")
            return False, f"文件名时间解析失败: {str(e)}"
        
        # 第四步：执行IMG_check.sh检查
        log.info("开始分析图片文件")
        success, img_check_output = ADBService.exec_shell(device_serial, f"/tmp/IMG_check.sh {photo_path}")
        if not success:
            log.error(f"IMG_check.sh执行失败: {img_check_output}")
            # 执行失败也继续
            # ADBService.exec_shell(device_serial, f"rm -rf {photo_path}")
            return False, f"图片分析失败: {img_check_output}"
            
        log.debug(f"IMG_check.sh输出:\n{img_check_output}")
        
        # 第五步：自动判断检查
        status_normal = False
        check_result = img_check_output.strip()
        
        # 解析输出内容
        for line in img_check_output.split('\n'):
            line = line.strip()
            if line == "status:normal":
                status_normal = True
                break
        ADBService.exec_shell(device_serial, f"rm -rf /tmp/record_test")
        ADBService.exec_shell(device_serial, f"rm -rf /tmp/IMG_check.sh")
        # 判断测试结果
        if status_normal:
            log.info("图片测试通过")
            # ADBService.exec_shell(device_serial, f"rm -rf {photo_path}")
            return True, f"拍照功能测试通过, {check_result}"
        else:
            # 测试不通过，保留文件用于调试，返回详细信息
            log.error(f"图片验证失败: {check_result}")
            return False, f"拍照测试不通过；{check_result}"
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"
