# -*- coding: utf-8 -*-
"""
WiFi 扫描服务模块
功能：扫描过滤 Xb 开头的 WiFi 热点（与蓝牙设备命名规则一致）
作者：wuzhibin
创建时间：2026-04-30
"""
import time
from typing import List, Dict
from .log_service import log

try:
    import pywifi
    from pywifi import const
    PYWI_FI_AVAILABLE = True
except ImportError as e:
    PYWI_FI_AVAILABLE = False
    log.warning(f"pywifi 模块导入失败: {e}，WiFi 扫描功能不可用")


class WiFiService:
    """WiFi 扫描服务类 - 仅扫描 SSID 以 Xb 开头的热点"""
    
    @staticmethod
    def scan_networks(timeout: int = 5) -> List[Dict]:
        """
        扫描 WiFi 热点
        
        参数:
            timeout: 扫描超时（秒），WiFi扫描较慢，默认5秒
            
        返回:
            List[Dict]: 热点列表，格式:
                {
                    "ssid": str,        # 热点名称
                    "bssid": str,       # AP MAC 地址
                    "signal": int,      # 信号强度 (0-100 百分比，或 dBm 负数)
                    "security": str,    # 加密类型 ("WPA2"/"WPA"/"OPEN"/...)
                    "connected": bool   # 固定 False（不跟踪连接状态）
                }
        """
        if not PYWI_FI_AVAILABLE:
            log.error("pywifi 未安装或导入失败，无法扫描 WiFi")
            return []
        
        log.debug(f"开始扫描 WiFi 热点（超时 {timeout}秒）")
        
        try:
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]  # 第一个无线网卡
            
            # 开始扫描
            iface.scan()
            time.sleep(timeout)
            
            results = iface.scan_results()
            networks = []
            
            for net in results:
                ssid = net.ssid
                if ssid and ssid.startswith("Xb"):  # 过滤 Xb 开头
                    # 解析信号强度（兼容 dBm 和百分比）
                    signal = WiFiService._parse_signal(net)
                    
                    # 解析安全类型
                    security = WiFiService._parse_security(net)
                    
                    networks.append({
                        "ssid": ssid,
                        "bssid": net.bssid,
                        "signal": signal,
                        "security": security,
                        "connected": False
                    })
                    log.debug(f"发现 WiFi 热点: {ssid} [{net.bssid}] 信号:{signal}")
            
            log.debug(f"WiFi 扫描完成，共发现 {len(networks)} 个 Xb 热点")
            return networks
            
        except PermissionError:
            log.error("WiFi 扫描需要管理员权限，请以管理员身份运行")
            return []
        except Exception as e:
            log.error(f"WiFi 扫描失败: {str(e)}")
            return []
    
    @staticmethod
    def _parse_signal(network) -> int:
        """
        解析信号强度
        
        pywifi 在不同平台返回的 signal 单位不同：
        - Linux (wireless-tools): 0-100 百分比
        - Windows (wlanapi): 负 dBm 值（如 -50）
        
        返回: 统一转换为 0-100 百分比（ approximate）
        """
        try:
            raw_signal = network.signal
            
            # Windows: signal 通常是负数（dBm），范围 -100 到 -30
            # 转换为 0-100: max(0, min(100, raw_signal + 100))
            if raw_signal < 0:  # dBm
                percent = max(0, min(100, raw_signal + 100))
                return round(percent)
            else:  # 已是百分比
                return raw_signal
        except:
            return 0
    
    @staticmethod
    def _parse_security(network) -> str:
        """解析加密类型"""
        try:
            # pywifi 的 akm (Authentication Key Management) 列表
            if not network.akm:
                return "OPEN"
            
            # 取第一个 akm 类型
            akm = network.akm[0] if network.akm else 0
            
            # 映射表（pywifi.const 常量）
            security_map = {
                const.IFACE_SECURITY_OPEN: "OPEN",
                const.IFACE_SECURITY_WPA: "WPA",
                const.IFACE_SECURITY_WPA2: "WPA2",
                const.IFACE_SECURITY_WPA3: "WPA3",
            }
            return security_map.get(akm, "UNKNOWN")
        except AttributeError:
            # network 没有 akm 属性
            return "OPEN"
        except Exception:
            return "UNKNOWN"