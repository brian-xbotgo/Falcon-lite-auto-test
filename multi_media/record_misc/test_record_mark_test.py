# -*- coding: utf-8 -*-
"""
测试用例：录制打点测试
功能：录制过程中打点功能测试
作者：系统自动生成
创建时间：2026-04-27
"""
import os
import time
import re
from datetime import datetime
from commons import ADBService, log, register_test_case, Module, Priority, validate_recorded_file,extract_file_path_from_acr_output, TEST_MQTT_OUTPUT_TEXT_FILE, TOOLS_DIR


@register_test_case("A", name="录制打点测试", module=Module.MULTI_MEDIA, priority=Priority.P2, supported_devices=[2, 3], test_case_number='')
def test_record_mark_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A：录制打点测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行录制打点自动化测试")

    try:
        # 第一步：识别设备类型，确定使用哪个版本的mp4info
        device_type = ADBService._identify_device_type(device_serial)
        if device_type == 0:
            log.error("无法识别设备类型")
            return False, "无法识别设备类型"

        log.debug(f"设备类型: {device_type}")

        # 第二步：检查并推送必要工具
        tools_ready = True

        # 检查/tmp/中是否有record_test工具，没有则推送
        success, output = ADBService.exec_shell(device_serial, "ls -la /tmp/record_test")
        if not success or "No such file" in output:
            record_test_local = os.path.join(TOOLS_DIR, "record_tool", "record_test")
            log.info("推送record_test工具到设备")
            success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
            if not success:
                log.error(f"推送record_test失败: {remote_path}")
                tools_ready = False

        # 检查/tmp/中是否有mp4info工具，没有则推送对应版本
        if device_type == 2:  # Falcon
            mp4info_local = os.path.join(TOOLS_DIR, "mp4info", "mp4info_rk3576")
            mp4info_remote = "/tmp/mp4info_rk3576"
            check_cmd = "ls -la /tmp/mp4info_rk3576"
        elif device_type == 3:  # Falcon-Air
            mp4info_local = os.path.join(TOOLS_DIR, "mp4info", "mp4info_rv1126b")
            mp4info_remote = "/tmp/mp4info_rv1126b"
            check_cmd = "ls -la /tmp/mp4info_rv1126b"
        else:
            return False, f"不支持的设备类型: {device_type}"

        success, output = ADBService.exec_shell(device_serial, check_cmd)
        if not success or "No such file" in output:
            log.info(f"推送{os.path.basename(mp4info_local)}工具到设备")
            success, remote_path = ADBService.push_and_prepare_tool(device_serial, mp4info_local)
            if not success:
                log.error(f"推送mp4info失败: {remote_path}")
                tools_ready = False

        if not tools_ready:
            return False, "必要工具推送失败，无法继续测试"

        log.info("所有工具准备完成")

        # 第三步：执行录制流程
        log.info("开始执行录制打点流程")

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

        # 启动录制
        log.info("启动录制")
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test record 0 1 0 0")
        if not success:
            return False, f"启动录制失败: {output}"

        # sleep 5
        time.sleep(5)

        # 执行打点
        log.info("执行打点")
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test mark")
        if not success:
            return False, f"打点命令失败: {output}"

        # sleep 5
        time.sleep(5)

        # 结束录制
        log.info("结束录制")
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test record 3 1 0 0")
        if not success:
            return False, f"结束录制失败: {output}"

        time.sleep(5)  # 等待文件写入完成

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

        # 验证文件是否存在
        success, _ = ADBService.exec_shell(device_serial, f"ls {video_path}")
        if not success:
            log.error(f"录制文件不存在: {video_path}")
            return False, f"ACR订阅反馈：{acr_output.strip()}"

        log.info(f"录制文件路径: {video_path}")

        # 文件名格式校验（可选，用于日志记录）
        filename = os.path.basename(video_path)
        log.debug(f"录制文件名: {filename}")

        # 查找对应的打点文件
        # 需要查询文件路径下.data文件夹是否存在对应的mark文件
        video_dir = os.path.dirname(video_path)
        mark_file_path = f"{video_dir}/.data/{filename.replace('.mp4', '.mark')}"
        log.info(f"检查打点文件: {mark_file_path}")

        success, output = ADBService.exec_shell(device_serial, f"ls -la {mark_file_path}")
        if success and "No such file" not in output:
            # 如果存在mark文件则测试通过，返回/sdcard/falcon/20260427/.data/VID_20260427_104957_01_01.mark
            log.info("打点文件存在，测试通过")
            return True, f"打点文件成功生成: {mark_file_path}"
        else:
            # 如果不存在mark文件则测试不通过
            log.error(f"打点文件不存在: {mark_file_path}")
            return False, f"打点文件不存在: {mark_file_path}"

    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"