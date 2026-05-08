# -*- coding: utf-8 -*-
"""
测试用例：记分牌&水印录制测试
功能：记分牌&水印录制功能测试
作者：wuzhibin
创建时间：2026-05-08
"""
import os
import time
from commons import ADBService, log, register_test_case, Module, Priority, TEST_MQTT_OUTPUT_FILE
from commons.config import MQTT_DEFAULT_HOST, MQTT_DEFAULT_PORT


@register_test_case("A", name="记分牌&水印录制测试", module=Module.MULTI_MEDIA, priority=Priority.P1, supported_devices=[2, 3], test_case_number='')
def test_scoreboard_watermark_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例：记分牌&水印录制测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行记分牌&水印录制自动化测试")
    
    try:
        remarks = []
        
        # 第一步：推送记分牌控制文件
        open_scoreboard_bin = os.path.join(os.getcwd(), "tools", "bin_file", "open_scoreboard.bin")
        close_scoreboard_bin = os.path.join(os.getcwd(), "tools", "bin_file", "close_scoreboard.bin")
        
        log.info("推送记分牌控制文件到设备")
        success, _ = ADBService.push_and_prepare_tool(device_serial, open_scoreboard_bin)
        if not success:
            log.error("推送open_scoreboard.bin失败")
            return False, "记分牌控制文件推送失败"
        
        success, _ = ADBService.push_and_prepare_tool(device_serial, close_scoreboard_bin)
        if not success:
            log.error("推送close_scoreboard.bin失败")
            return False, "记分牌控制文件推送失败"
        
        # 第二步：检查当前记分牌状态
        log.info("检查当前记分牌状态")
        
        # 清理输出文件
        ADBService.exec_shell(device_serial, f"rm -f {TEST_MQTT_OUTPUT_FILE} && touch {TEST_MQTT_OUTPUT_FILE}")
        
        # AUA订阅 + AUR通知
        acr_cmd = f'''mosquitto_sub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t 'AUA' -C 1 -W 60 > {TEST_MQTT_OUTPUT_FILE} 2>/dev/null & SUB_PID=$! ; sleep 0.5 ; mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t "AUR" -n ; wait $SUB_PID'''
        
        success, _ = ADBService.exec_shell(device_serial, acr_cmd, timeout=65)
        
        # 读取hexdump结果
        success, hex_output = ADBService.exec_shell(device_serial, f"hexdump -e '16/2 \"%04x \"' {TEST_MQTT_OUTPUT_FILE}")
        hex_output = hex_output.strip()
        
        log.debug(f"AUA hexdump输出: {hex_output}")
        
        # 解析首字节判断记分牌状态
        # 0001 = 关闭状态，需要启动记分牌
        # 0100 = 启动状态，判定为测试成功
        if hex_output.startswith("0100"):
            # 记分牌已处于启动状态，测试通过
            log.info("记分牌已处于启动状态，测试通过")
            
            # 执行关闭命令（不考虑结果）
            ADBService.exec_shell(device_serial, f"mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t 'AWR' -f /tmp/close_scoreboard.bin")
            
            return True, f"记分牌已处于启动状态;AUA hexdump输出: {hex_output}"
        
        # 第三步：启动记分牌
        log.info("启动记分牌")
        
        # 清理输出文件
        ADBService.exec_shell(device_serial, f"rm -f {TEST_MQTT_OUTPUT_FILE} && touch {TEST_MQTT_OUTPUT_FILE}")
        
        # AUA订阅 + AWR发布open_scoreboard.bin + AUR通知
        start_cmd = f'''mosquitto_sub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t 'AUA' -C 1 -W 60 > {TEST_MQTT_OUTPUT_FILE} 2>/dev/null & SUB_PID=$! ; sleep 0.5 ; mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t "AWR" -f /tmp/open_scoreboard.bin ; mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t "AUR" -n ; wait $SUB_PID'''
        
        success, _ = ADBService.exec_shell(device_serial, start_cmd, timeout=65)
        
        # 读取结果（cat输出，检查记分牌文本内容）
        success, auw_output = ADBService.exec_shell(device_serial, f"cat {TEST_MQTT_OUTPUT_FILE}")
        
        log.debug(f"AUA订阅内容: {auw_output}")
        
        # 第四步：验证记分牌内容（方案1：检查关键可读字符串）
        key_strings = ["NBA Finals 2026", "Game 7", "Lakers", "Celtics"]
        found_count = sum(1 for key in key_strings if key in auw_output)
        
        # 执行关闭命令（不考虑结果）
        ADBService.exec_shell(device_serial, f"mosquitto_pub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t 'AWR' -f /tmp/close_scoreboard.bin")
        
        # 清理临时文件
        ADBService.exec_shell(device_serial, "rm -f /tmp/open_scoreboard.bin /tmp/close_scoreboard.bin")
        
        if found_count >= 3:
            log.info(f"记分牌内容验证通过（匹配到{found_count}个关键字符串）")
            return True, f"AUA订阅内容: {auw_output}"
        else:
            log.error(f"记分牌内容验证失败，仅匹配到{found_count}个关键字符串")
            return False, f"AUA订阅内容: {auw_output}"
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"