# -*- coding: utf-8 -*-
"""
BLE蓝牙服务模块
功能：扫描过滤Xb开头的蓝牙设备
作者：wuzhibin
创建时间：2026-04-14
"""
import asyncio
from bleak import BleakScanner
from typing import List, Dict
from .log_service import log


class BleService:
    """
    BLE蓝牙扫描服务类
    仅扫描名称以Xb开头的设备
    """

    @staticmethod
    async def scan_devices(timeout: int = 3) -> List[Dict]:
        """
        扫描BLE蓝牙设备
        :param timeout: 扫描超时时间（秒）
        :return: 设备列表 [{name, address, rssi}]
        """
        log.debug("开始扫描BLE蓝牙设备")
        
        devices = []
        
        try:
            devices_raw = await BleakScanner.discover(timeout=timeout, return_adv=True)
            
            for device, adv_data in devices_raw.values():
                try:
                    name = adv_data.local_name
                    if name and name.startswith("Xb"):
                        devices.append({
                            "name": name,
                            "address": device.address,
                            "rssi": adv_data.rssi,
                            "connected": False
                        })
                        log.debug(f"发现蓝牙设备: {name} [{device.address}]")
                except Exception:
                    # 忽略单个设备解析错误，继续扫描其他设备
                    continue

        except Exception as e:
            log.error(f"蓝牙扫描失败: {str(e)}")
            return []

        log.debug(f"蓝牙扫描完成，共发现 {len(devices)} 个Xb开头设备")
        return devices