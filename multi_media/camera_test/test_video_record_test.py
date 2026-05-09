# -*- coding: utf-8 -*-
"""
测试用例：视频录制测试
功能：自动测试视频录制功能并验证录制文件完整性
作者：wuzhibin
创建时间：2026-04-16
"""
import os
import time
import re
from datetime import datetime
from commons import ADBService, log, register_test_case, Priority, Module, extract_file_path_from_acr_output, TEST_MQTT_OUTPUT_TEXT_FILE, TOOLS_DIR


@register_test_case("A", name="视频录制测试", module=Module.MULTI_MEDIA, priority=Priority.P0, supported_devices=[2, 3], test_case_number='')
def test_video_record(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A：视频录制测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行视频录制自动化测试")
    
    try:
        # 第一步：识别设备类型，确定使用哪个版本的mp4info
        device_type = ADBService._identify_device_type(device_serial)
        if device_type == 0:
            log.error("无法识别设备类型")
            return False, "无法识别设备类型"
            
        log.debug(f"设备类型: {device_type}")
        
        # 第二步：推送所需工具（不做存在检查，直接推送确保文件存在且版本正确）
        tools_ready = True
        
        # 推送record_test工具
        record_test_local = os.path.join(TOOLS_DIR, "record_tool", "record_test")
        log.info("推送record_test工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
        if not success:
            log.error(f"推送record_test失败: {remote_path}")
            tools_ready = False
        
        # 推送对应版本的mp4info
        if device_type == 2:  # Falcon
            mp4info_local = os.path.join(TOOLS_DIR, "mp4info", "mp4info_rk3576")
            mp4info_remote = "/tmp/mp4info_rk3576"
        elif device_type == 3:  # Falcon-Air
            mp4info_local = os.path.join(TOOLS_DIR, "mp4info", "mp4info_rv1126b")
            mp4info_remote = "/tmp/mp4info_rv1126b"
        else:
            return False, f"不支持的设备类型: {device_type}"
            
        log.info(f"推送{os.path.basename(mp4info_local)}工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, mp4info_local)
        if not success:
            log.error(f"推送mp4info失败: {remote_path}")
            tools_ready = False
        
        if not tools_ready:
            return False, "必要工具推送失败，无法继续测试"
            
        log.info("所有工具准备完成")
        
        # 第三步：执行录制流程
        log.info("开始执行录制流程")
        
        # 订阅 ACR 主题获取录制反馈
        log.info("订阅 ACR 主题")
        # 先创建输出文件
        # success, _ = ADBService.exec_shell(device_serial, f"rm -rf {TEST_MQTT_OUTPUT_TEXT_FILE}")
        success, _ = ADBService.exec_shell(device_serial, f"touch {TEST_MQTT_OUTPUT_TEXT_FILE}")
        if not success:
            log.warning("创建输出文件失败")

        acr_sub_cmd = f'''mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 > "{TEST_MQTT_OUTPUT_TEXT_FILE}"'''
        # 异步执行订阅命令（避免阻塞主线程）
        import threading
        def run_acr_subscribe():
            ADBService.exec_shell(device_serial, acr_sub_cmd)

        subscribe_thread = threading.Thread(target=run_acr_subscribe)
        subscribe_thread.start()

        time.sleep(1)

        # 配置
        success, _ = ADBService.exec_shell(device_serial, "/tmp/record_test mute 0")
        if not success:
            log.warning("设置静音失败，继续录制")
        time.sleep(1)

        # 启动录制
        log.info("开始录制视频")
        success, _ = ADBService.exec_shell(device_serial, "/tmp/record_test record 0 1 0 0")
        if not success:
            return False, "启动录制失败"
        time.sleep(1)

        # Sleep 5
        time.sleep(5)

        # 结束录制
        log.info("停止录制视频")
        success, _ = ADBService.exec_shell(device_serial, "/tmp/record_test record 3 1 0 0")
        if not success:
            return False, "停止录制失败"

        # 等待录制完成和消息处理
        time.sleep(3)

        # 获取录制文件的路径
        log.info("获取录制文件路径")
        success, acr_output = ADBService.exec_shell(device_serial, f"cat {TEST_MQTT_OUTPUT_TEXT_FILE}")
        if not success or not acr_output.strip():
            return False, "ACR订阅反馈：(无内容)"

        # 提取文件路径
        success_extract, video_path = extract_file_path_from_acr_output(acr_output)
        if not success_extract:
            log.error(f"提取文件路径失败: {video_path}")
            return False, f"ACR订阅反馈：{acr_output.strip()}"

        log.info(f"录制文件路径: {video_path}")
        # 验证文件是否存在
        success, _ = ADBService.exec_shell(device_serial, f"ls {video_path}")
        if not success:
            log.error(f"录制文件不存在: {video_path}")
            return False, f"ACR订阅反馈：{acr_output.strip()}"

        log.info(f"录制文件路径: {video_path}")

        # 第五步：执行mp4info检查
        log.info("开始分析视频文件")
        success, mp4info_output = ADBService.exec_shell(device_serial, f"{mp4info_remote} {video_path}")
        if not success:
            log.error(f"mp4info执行失败: {mp4info_output}")
            # 执行失败也继续，尝试清理文件
            ADBService.exec_shell(device_serial, f"rm -rf {video_path}")
            return False, f"视频文件分析失败: {mp4info_output}"
            
        log.debug(f"mp4info输出:\n{mp4info_output}")
        
        # 第六步：自动判断检查
        video_track_found = False
        audio_track_found = False
        video_info = ""
        
        # 解析输出内容
        for line in mp4info_output.split('\n'):
            line = line.strip()
            if line.startswith('1') and 'video' in line:
                video_track_found = True
                video_info = line
                log.info(f"视频轨道信息: {video_info}")
            elif line.startswith('2') and 'audio' in line:
                audio_track_found = True
                log.info(f"音频轨道信息: {line}")
        
        ADBService.exec_shell(device_serial, f"rm -rf /tmp/record_test")
        ADBService.exec_shell(device_serial, f"rm -rf {mp4info_remote}")
        # 第七步：清理文件
        if video_track_found and audio_track_found:
            log.info("视频文件验证通过")
            # ADBService.exec_shell(device_serial, f"rm -rf {video_path}")
            return True, f"视频录制测试通过, {video_info}"
        else:
            # 测试不通过，保留文件用于调试，返回详细信息
            error_msg = []
            if not video_track_found:
                error_msg.append("未找到视频轨道")
            if not audio_track_found:
                error_msg.append("未找到音频轨道")
            error_detail = "、".join(error_msg)
            log.error(f"视频文件验证失败: {error_detail}")
            log.error(f"完整输出:\n{mp4info_output}")
            return False, f"视频验证失败: {error_detail}, 输出: {mp4info_output[:200]}..."
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"
