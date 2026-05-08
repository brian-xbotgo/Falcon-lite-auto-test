# -*- coding: utf-8 -*-
"""
测试用例：电子围栏测试
功能：电子围栏创建和查询功能测试
作者：wuzhibin
创建时间：2026-05-08
"""
import os
import time
from commons import ADBService, log, register_test_case, Module, Priority, TEST_MQTT_OUTPUT_FILE
from commons.config import MQTT_DEFAULT_HOST, MQTT_DEFAULT_PORT


@register_test_case("A", name="电子围栏测试", module=Module.MULTI_MEDIA, priority=Priority.P3, supported_devices=[2, 3], test_case_number='')
def test_fence_test(device_serial: str) -> tuple[bool, str]:
    """
    测试用例：电子围栏测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.info("开始执行电子围栏自动化测试")
    
    try:
        remarks = []
        
        # 第一步：清空电子围栏
        log.info("清空电子围栏")
        success, _ = ADBService.exec_shell(device_serial, r"mosquitto_pub -p 1883 -t 'CAR' -n")
        time.sleep(1)
        
        # 第二步：准备
        log.info("准备电子围栏")
        success, _ = ADBService.exec_shell(device_serial, r"mosquitto_pub -p 1883 -t 'CER' -n")
        time.sleep(1)
        
        # 第三步：开始
        log.info("开始电子围栏")
        success, _ = ADBService.exec_shell(device_serial, r"mosquitto_pub -p 1883 -t 'BYR' -n")
        time.sleep(1)
        
        # 第四步：点位0
        log.info("设置点位0")
        success, _ = ADBService.exec_shell(device_serial, r"printf '\x00\x00\x64\x00\x64' | mosquitto_pub -p 1883 -t 'CBR' -s")
        time.sleep(1)
        
        # 第五步：点位1
        log.info("设置点位1")
        success, _ = ADBService.exec_shell(device_serial, r"printf '\x01\x01\xF4\x00\x64' | mosquitto_pub -p 1883 -t 'CBR' -s")
        time.sleep(1)
        
        # 第六步：点位2
        log.info("设置点位2")
        success, _ = ADBService.exec_shell(device_serial, r"printf '\x02\x01\xF4\x01\x90' | mosquitto_pub -p 1883 -t 'CBR' -s")
        time.sleep(1)
        
        # 第七步：点位3
        log.info("设置点位3")
        success, _ = ADBService.exec_shell(device_serial, r"printf '\x03\x00\x64\x01\x90' | mosquitto_pub -p 1883 -t 'CBR' -s")
        time.sleep(1)
        
        # 第八步：完成
        log.info("完成电子围栏设置")
        success, _ = ADBService.exec_shell(device_serial, r"printf '\x00' | mosquitto_pub -p 1883 -t 'BZR' -s")
        time.sleep(1)
        
        # 第九步：查询结果
        # A. 监听输出到文件
        log.info("查询电子围栏结果")
        
        # 清理输出文件
        ADBService.exec_shell(device_serial, f"rm -f {TEST_MQTT_OUTPUT_FILE} && touch {TEST_MQTT_OUTPUT_FILE}")
        
        # B. 执行订阅和查询
        cca_sub_cmd = f'''mosquitto_sub -h {MQTT_DEFAULT_HOST} -p {MQTT_DEFAULT_PORT} -t 'CCA' -C 1 -W 60 > {TEST_MQTT_OUTPUT_FILE} 2>/dev/null & SUB_PID=$! ; sleep 1 ; mosquitto_pub -p 1883 -t "CCR" -n ; wait $SUB_PID'''
        
        success, _ = ADBService.exec_shell(device_serial, cca_sub_cmd, timeout=65)
        
        # C. 获取hexdump结果
        success, hex_output = ADBService.exec_shell(device_serial, f"hexdump {TEST_MQTT_OUTPUT_FILE}")
        hex_output = hex_output.strip()
        
        log.debug(f"CCR hexdump输出: {hex_output}")
        
        # 第十步：判断结果
        # 期望输出: 0a01 表示成功
        if "0a01" in hex_output:
            log.info("电子围栏测试通过")
            return True, f"CCR hexdump输出: {hex_output}"
        else:
            log.error(f"电子围栏测试失败: {hex_output}")
            return False, f"CCR hexdump输出: {hex_output}"
            
    except Exception as e:
        log.error(f"测试执行异常: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False, f"测试异常: {str(e)}"