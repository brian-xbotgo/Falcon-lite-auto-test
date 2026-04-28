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
from commons import ADBService, log, register_test_case, Module, Priority, validate_recorded_file


@register_test_case("A", name="录制打点测试", module=Module.MULTI_MEDIA, priority=Priority.P2, supported_devices=[2, 3])
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
            record_test_local = os.path.join(os.getcwd(), "tools", "record_tool", "record_test")
            log.info("推送record_test工具到设备")
            success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
            if not success:
                log.error(f"推送record_test失败: {remote_path}")
                tools_ready = False

        # 检查/tmp/中是否有mp4info工具，没有则推送对应版本
        if device_type == 2:  # Falcon
            mp4info_local = os.path.join(os.getcwd(), "tools", "mp4info", "mp4info_rk3576")
            mp4info_remote = "/tmp/mp4info_rk3576"
            check_cmd = "ls -la /tmp/mp4info_rk3576"
        elif device_type == 3:  # Falcon-Air
            mp4info_local = os.path.join(os.getcwd(), "tools", "mp4info", "mp4info_rv1126b")
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

        # 记录操作开始时间
        operation_start = time.time()

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

        # 获取刚录制的文件的路径
        log.info("获取刚录制的文件路径")
        success, output = ADBService.exec_shell(device_serial, "ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 | head -1")
        if not success or not output.strip():
            return False, "未找到录制的视频文件"

        video_path = output.strip()
        log.info(f"录制文件路径: {video_path}")

        # 第四步：执行文件检查流程并进行判断
        # 检查文件生成时间（不超过1分半钟）
        log.debug(f"开始验证录制文件: {video_path}")
        is_valid, validation_message = validate_recorded_file(device_serial, video_path, operation_start, max_age_seconds=90)
        if not is_valid:
            log.error(f"文件验证失败: {validation_message}")
            return False, f"录制文件验证失败: {validation_message}"

        log.debug(f"文件验证通过: {validation_message}")

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