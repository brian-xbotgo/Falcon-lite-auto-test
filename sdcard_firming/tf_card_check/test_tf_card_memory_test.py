# -*- coding: utf-8 -*-
"""
测试用例：SD卡内存检查
功能：自动检查SD卡是否连接且输出内存使用情况
作者：系统自动生成
创建时间：2026-04-20
"""
from commons import ADBService, log, register_test_case, Priority, Module


@register_test_case("A", name="SD卡内存检查", module=Module.SDCARD_FIRMING, priority=Priority.P0, supported_devices=[2, 3])
def test_tf_card_memory_check(device_serial: str) -> tuple[bool, str]:
    """
    测试用例：SD卡内存检查
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行SD卡内存检查测试")
    
    # 1. 执行MQTT订阅-发送-等待流程
    success, result = ADBService.mqtt_subscribe_and_send(
        device_serial,
        subscribe_topic="CSA",
        publish_topic="CSR",
        publish_payload="",
        timeout=30,
        mode="HEX"
    )
    
    if not success:
        return False, f"测试失败: {result}"
    
    log.debug(f"收到SD卡返回数据: {result}")
    
    # 2. 解析返回的十六进制内容
    hex_parts = result.strip().split()
    log.debug(f"拆分后数据: {hex_parts}, 长度: {len(hex_parts)}")
    
    # 检查数据长度是否足够
    if len(hex_parts) < 5:
        return False, f"返回数据格式错误: {result}, 部分数: {len(hex_parts)}"
    
    try:
        log.debug("开始解析字节序...")
        # hexdump输出是16位小端格式，每个4字符是2字节，高字节在后
        # 输入：a701 0004 a600 0004 0a00
        # 解析后对应9字节：01 00 00 04 a7 00 00 04 a6
        raw_bytes = [0x00] * 9
        
        if len(hex_parts) >= 1:
            # 第一个双字节 a701 → 01(字节0), a7(字节4)
            part1 = hex_parts[0]
            raw_bytes[0] = int(part1[2:4], 16)  # 01
            raw_bytes[4] = int(part1[0:2], 16)  # a7
            
        if len(hex_parts) >= 2:
            # 第二个双字节 0004 → 00(字节1), 04(字节3)
            part2 = hex_parts[1]
            raw_bytes[1] = int(part2[0:2], 16)  # 00
            raw_bytes[2] = 0x00                  # 固定00
            raw_bytes[3] = int(part2[2:4], 16)  # 04
            
        if len(hex_parts) >= 3:
            # 第三个双字节 a300 → 00(字节5), a3(字节8)
            part3 = hex_parts[2]
            raw_bytes[5] = int(part3[2:4], 16)  # 00
            raw_bytes[8] = int(part3[0:2], 16)  # a3
            
        if len(hex_parts) >= 4:
            # 第四个双字节 0004 → 00(字节6), 04(字节7)
            part4 = hex_parts[3]
            raw_bytes[6] = int(part4[0:2], 16)  # 00
            raw_bytes[7] = int(part4[2:4], 16)  # 04
        
        log.debug(f"解析后原始字节: {[f'0x{b:02x}' for b in raw_bytes]}")
        
        # 3. 逐字段解析
        # 字节0: 挂载状态
        mount_status = raw_bytes[0]
        log.debug(f"挂载状态: 0x{mount_status:02x}")
        
         # 字节1-4: 总容量（大端序）字节1最高位，字节4最低位
        total_capacity = (
             (raw_bytes[1] << 24) |
             (raw_bytes[2] << 16) |
             (raw_bytes[3] << 8) |
             raw_bytes[4]
         )
        log.debug(f"总容量原始值: 0x{total_capacity:08x} = {total_capacity}")
        
        # 字节5-8: 可用容量（大端序）字节5最高位，字节8最低位
        available_capacity = (
            (raw_bytes[5] << 24) |
            (raw_bytes[6] << 16) |
            (raw_bytes[7] << 8) |
            raw_bytes[8]
        )
        log.debug(f"可用容量原始值: 0x{available_capacity:08x} = {available_capacity}")
        
        # 转换为GB
        total_gb = total_capacity / 10.0
        available_gb = available_capacity / 10.0
        
        # 4. 判断结果
        if mount_status == 0x00:
            log.error("SD卡未挂载")
            return False, "SD卡未挂载"
        elif mount_status == 0x01:
            log.info(f"SD卡已挂载，总容量：{total_gb:.1f} GB，可用容量：{available_gb:.1f} GB")
            return True, f"SD卡已挂载，总容量：{total_gb:.1f} GB，可用容量：{available_gb:.1f} GB"
        else:
            log.error(f"未知挂载状态: 0x{mount_status:02X}")
            return False, f"未知挂载状态: 0x{mount_status:02X}"
            
    except Exception as e:
        log.error(f"解析数据失败: {str(e)}")
        return False, f"解析数据失败: {str(e)}"
