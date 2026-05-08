# -*- coding: utf-8 -*-
"""
测试用例：自动追踪测试
功能：通过record_test工具执行M键预设进行录制，验证自动追踪文件格式
作者：wuzhibin
创建时间：2026-05-08
"""
import os
import time
import re
from commons import ADBService, log, register_test_case, Module, Priority, extract_file_path_from_acr_output, TEST_MQTT_OUTPUT_TEXT_FILE


@register_test_case("A", name="自动追踪测试", module=Module.TRACKING, priority=Priority.P1, supported_devices=[2, 3], test_case_number='')
def test_auto_track(device_serial: str) -> tuple[bool, str]:
    """
    测试用例：自动追踪测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行自动追踪自动化测试")
    
    try:
        # 第一步：识别设备类型
        device_type = ADBService._identify_device_type(device_serial)
        if device_type == 0:
            log.error("无法识别设备类型")
            return False, "无法识别设备类型"
        
        log.debug(f"设备类型: {device_type}")
        
        # 第二步：推送record_test工具
        record_test_local = os.path.join(os.getcwd(), "tools", "record_tool", "record_test")
        log.info("推送record_test工具到设备")
        success, remote_path = ADBService.push_and_prepare_tool(device_serial, record_test_local)
        if not success:
            log.error(f"推送record_test失败: {remote_path}")
            return False, f"工具推送失败: {remote_path}"
        
        log.info("所有工具准备完成")

        # 第三步：执行录制流程
        log.info("开始执行录制追踪流程")

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
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test record 0 2 0 0")
        if not success:
            return False, f"启动录制失败: {output}"

        time.sleep(10)
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test record 0 1 0 0")

        time.sleep(2)

        # 结束录制
        log.info("结束录制")
        success, output = ADBService.exec_shell(device_serial, "/tmp/record_test record 3 2 0 0")
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

        # 查找对应的追踪文件
        # 需要查询文件路径下.data文件夹是否存在对应的track文件
        video_dir = os.path.dirname(video_path)
        track_file_path = f"{video_dir}/.data/{filename.replace('.mp4', '.track')}"
        log.info(f"检查追踪文件: {track_file_path}")

        success, output = ADBService.exec_shell(device_serial, f"ls -la {track_file_path}")
        if not success or "No such file"  in output:
            # 如果不存在track文件则测试不通过
            log.error(f"追踪文件不存在: {track_file_path}")
            return False, f"追踪文件不存在: {track_file_path}"
            
        # 第七步：验证track文件格式
        success, track_content = ADBService.exec_shell(device_serial, f"cat {track_file_path}")
        if not success:
            return False, f"ACR订阅反馈：{acr_output.strip()}"
        
        log.debug(f"track文件内容:\n{track_content}")
        
        # 第八步：格式校验
        # 允许的格式行：
        # - 空行
        # - UTC时间行: UTC2026-05-06 17:13:21.950
        # - Frame行: Frame188 SZ0 Yaw0.50 Pit0.00 fps20.0
        # - AFilterP行: AFilterP0 mot0 Deque0
        # - Fast行: Fast0 Crowdx1280
        # - backCenterX行: backCenterX1280
        # - FIN行: FIN:x1280.0 V80.0 Yaw input0.0 output0.0 dir0 gear32
        # - Zoom行: Zoom:CPSz0 Count0
        
        format_check_cmd = r'''! grep -v -E '^$|^UTC[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}$|^Frame[0-9]+ SZ[0-9]+ Yaw[0-9.\-]+ Pit[0-9.\-]+ fps[0-9.\]+$|^AFilterP[0-9]+ mot[0-9]+ Deque[0-9]+$|^Fast[0-9]+ Crowdx[0-9]+$|^backCenterX[0-9]+$|^FIN:x[0-9.\-]+ V[0-9.\-]+ Yaw input[0-9.\-]+ output[0-9.\-]+ dir[0-9]+ gear[0-9]+$|^Zoom:CPSz[0-9]+ Count[0-9]+$' ''' + track_file_path + ''' | grep -q . && echo "format error" || echo "format normal"'''
        
        success, format_result = ADBService.exec_shell(device_serial, format_check_cmd)
        format_result = format_result.strip()
        
        
        # 清理工具
        ADBService.exec_shell(device_serial, "rm -f /tmp/record_test")
        
        if "format normal" in format_result:
            log.info("自动追踪测试通过")
            return True, f"自动追踪文件格式正确，track文件内容:{track_content}"
        else:
            log.error(f"自动追踪测试失败: {format_result}")
            return False, f"ACR订阅反馈：{acr_output.strip()}"
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"