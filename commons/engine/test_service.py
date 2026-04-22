# -*- coding: utf-8 -*-
"""
测试服务模块
功能：测试用例管理、流程调度、状态控制，自动化优先+人工集中确认
作者：wuzhibin
创建时间：2026-04-13
"""
import time
import importlib
import os
import inspect
from typing import List, Callable, Optional, Dict, Tuple, Union
from enum import Enum
from ..test_model import TestModel, Priority, Module
from ..device_model import DeviceModel
from ..adb_service import ADBService
from ..log_service import log
from ..config import DEFAULT_TEST_TIMEOUT

# 测试用例注册表：key=test_id, value=测试用例完整信息
_test_case_registry: Dict[str, Dict] = {}

# 自动编号计数器
_auto_id_counters = {
    'A': 0,  # 自动化测试用例计数器
    'B': 0   # 人工测试用例计数器
}


def register_test_case(type_tag: str, name: str = "", module: Union[str, Module] = Module.MISC, 
                       priority: Union[str, Priority] = Priority.P1, supported_devices: list = None):
    """
    测试用例注册装饰器 - ✅ 新增任何测试用例只需加这个装饰器
    ✅ 全自动编号，不需要手动写数字！
    
    :param type_tag: 类型标记，只需要写 'A' 或 'B'
                     'A' = 自动化测试用例（优先执行）
                     'B' = 人工测试用例（自动化完成后执行）
    :param name: 测试用例名称
    :param module: 所属模块，支持Module枚举或字符串
    :param priority: 优先级 P0/P1/P2/P3/P4，支持字符串或Priority枚举
    :param supported_devices: 支持的设备类型列表，如 [1, 2] 表示支持Chameleon和Falcon
                             None表示支持所有设备类型
    
    ✅ 自动编号说明：
    - 系统自动检测是第几个A/B类型的用例
    - 自动生成编号：A001, A002, B001, B002...
    - 自动按正确顺序排序执行
    - ✅ 你只需要标记A/B，不需要关心数字
    """
    def decorator(func):
        # 自动分配编号
        global _auto_id_counters
        
        # 计数器自增
        _auto_id_counters[type_tag] += 1
        seq_num = _auto_id_counters[type_tag]
        
        # 自动生成完整测试ID：A001, B003等
        test_id = f"{type_tag}{seq_num:03d}"
        
        # 自动识别测试类型
        if type_tag == 'A':
            derived_type = "自动化"
        else:
            derived_type = "人工"
            
        # 自动生成名称
        if not name:
            test_name = func.__name__.replace('test_', '').replace('_', ' ')
        else:
            test_name = name
            
        # 兼容字符串优先级参数
        if isinstance(priority, str):
            try:
                priority_enum = Priority[priority.upper()]
            except (KeyError, AttributeError):
                priority_enum = Priority.P1
        else:
            priority_enum = priority
            
        # 兼容字符串模块参数
        if isinstance(module, str):
            # 字符串到枚举的映射
            module_map = {
                "系统杂项": Module.MISC,
                "网络": Module.BTWIFI,
                "蓝牙WiFi": Module.BTWIFI,
                "蓝牙配网": Module.BLE_CONFIGURE_WIFI,
                "BLE主机": Module.BLE_CENTRAL,
                "HTTP客户端": Module.HTTP_AGENT,
                "MQTT通信": Module.MQTT_WRAPPER,
                "OTA升级": Module.OTA_UPDATE,
                "SD卡功能": Module.SDCARD_FIRMING,
                "LVGL界面": Module.LVGL_APP,
                "多媒体": Module.MULTI_MEDIA,
                "步进电机": Module.STEPPER_MOTOR,
                "无刷电机": Module.BRUSHLESS_MOTOR,
                "AI检测": Module.DETECT,
                "目标跟踪": Module.TRACKING,
                "流媒体": Module.STREAM,
                "通用": Module.MISC
            }
            module_enum = module_map.get(module, Module.MISC)
        else:
            module_enum = module
            
        test_info = {
            "test_id": test_id,
            "type_tag": type_tag,
            "name": test_name,
            "module": module_enum,
            "priority": priority_enum,
            "test_type": derived_type,
            "supported_devices": supported_devices,  # 支持的设备类型
            "func": func
        }
        
        _test_case_registry[test_id] = test_info
        log.debug(f"注册测试用例: {test_id} [{derived_type}] -> {test_name}")
        
        return func
    return decorator


def auto_discover_test_cases():
    """自动发现所有测试用例模块
    ✅ 新增测试用例无需修改核心代码，自动扫描注册
    """
    # 需要扫描的模块目录
    test_modules = [
        'misc', 'btwifi', 'bleConfigureWifi', 'ble_central',
        'http_agent', 'mqtt_wrapper', 'ota_update', 'sdcard_firming',
        'lvgl_app', 'multi_media', 'stepper_motor_control',
        'brushless_motor_control', 'detect', 'tracking', 'stream'
    ]
    
    for module_name in test_modules:
        try:
            # 扫描模块下的所有子目录
            module_path = module_name.replace('.', '/')
            if not os.path.exists(module_path):
                continue
                
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        # 转换为Python模块路径
                        rel_path = os.path.relpath(root, '.').replace(os.sep, '.')
                        test_module = f"{rel_path}.{file[:-3]}"
                        try:
                            importlib.import_module(test_module)
                        except Exception as e:
                            log.debug(f"加载测试模块失败 {test_module}: {str(e)}")
        except Exception as e:
            log.debug(f"扫描模块失败 {module_name}: {str(e)}")
    
    log.info(f"自动发现完成，共注册 {len(_test_case_registry)} 个测试用例")


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "等待中"
    RUNNING = "执行中"
    PASSED = "通过"
    FAILED = "失败"
    WAITING_CONFIRM = "待确认"
    NOT_SUPPORTED = "不支持"


class TestService:
    """
    测试引擎服务
    纯业务逻辑，不操作UI，通过回调通知状态变化
    采用单例模式，全局唯一实例
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.test_cases: List[TestModel] = []
        self.current_test_index: int = -1
        self.is_running: bool = False
        self.device: Optional[DeviceModel] = None
        # 状态变化回调函数
        self._status_callback: Optional[Callable] = None
        self._progress_callback: Optional[Callable] = None
        self._manual_confirm_callback: Optional[Callable] = None

        # 自动发现并注册所有测试用例
        auto_discover_test_cases()
        
        # 初始化测试用例
        self._init_test_cases()
        self._initialized = True

    def set_status_callback(self, callback: Callable) -> None:
        """设置测试状态变化回调"""
        self._status_callback = callback

    def set_progress_callback(self, callback: Callable) -> None:
        """设置测试进度回调"""
        self._progress_callback = callback

    def set_manual_confirm_callback(self, callback: Callable) -> None:
        """设置人工确认回调"""
        self._manual_confirm_callback = callback

    def _init_test_cases(self) -> None:
        """
        ✅ 全自动初始化测试用例
        所有测试用例来自 @register_test_case 装饰器注册
        完全不需要手动添加任何测试用例
        
        测试用例编号规范：
        - A开头：自动化测试用例（优先执行）
        - B开头：人工测试用例（自动化完成后执行）
        - 后面3位数字：自增编号
        执行顺序：先执行所有A类自动化用例，再执行所有B类人工用例
        """
        self.test_cases = []
        
        # 从注册表加载所有测试用例，自动按ID排序
        for test_id, test_info in sorted(_test_case_registry.items(), key=lambda x: x[0]):
            test_model = TestModel(
                test_id=test_id,
                module=test_info["module"],
                name=test_info["name"],
                test_type=test_info["test_type"],
                priority=test_info["priority"],
            )
            self.test_cases.append(test_model)
        
        log.info(f"自动加载测试用例完成，共 {len(self.test_cases)} 个测试用例")

    def set_device(self, device: Optional[DeviceModel]) -> None:
        """设置测试目标设备"""
        self.device = device
        if device:
            log.info(f"设置测试设备: {device.serial}")
        else:
            log.info("清除测试设备")

    def get_all_test_cases(self) -> List[TestModel]:
        """获取所有测试用例（与内部执行顺序一致）"""
        return self.test_cases.copy()

    def get_test_progress(self) -> tuple[int, int]:
        """获取测试进度（已完成, 总数）
        不支持的测试项不计入进度统计，不影响通过率
        """
        # 排除不支持的测试项
        valid_cases = [tc for tc in self.test_cases 
                      if tc.status != TestStatus.NOT_SUPPORTED.value]
        total = len(valid_cases)
        if total == 0:
            return 0, 0
        completed = sum(1 for tc in valid_cases
                       if tc.status in [TestStatus.PASSED.value, TestStatus.FAILED.value])
        return completed, total

    def _notify_status_changed(self, test_case: TestModel) -> None:
        """通知状态变化"""
        if self._status_callback:
            self._status_callback(test_case)

    def _notify_progress(self) -> None:
        """通知进度变化"""
        if self._progress_callback:
            completed, total = self.get_test_progress()
            self._progress_callback(completed, total)

    def start_test(self) -> bool:
        """开始测试流程"""
        if not self.device or self.device.status != "在线":
            log.error("测试启动失败：设备未连接或离线")
            return False

        self.is_running = True
        self.current_test_index = -1
        log.info("=" * 50)
        log.info("测试流程开始")
        log.info(f"测试设备: {self.device.serial}")
        log.info(f"测试用例总数: {len(self.test_cases)}")
        log.info("=" * 50)
        
        # 测试开始前清理MQTT输出文件
        log.debug("测试开始前清理MQTT输出文件")
        ADBService.clean_mqtt_output_file(self.device.serial)

        # ✅ 测试用例自动排序：
        # 1. 先按类型：A(自动化)优先，B(人工)在后
        # 2. 同类型按优先级：P0最高，P4最低
        # 3. 同优先级保持原编号顺序
        # 使用sorted创建新列表，不修改原test_cases顺序，避免单步执行后顺序混乱
        sorted_cases = sorted(self.test_cases, key=lambda x: (
            x.test_id[0],          # 先按类型A/B
            x.priority.value,      # 优先级数值越小越高
            x.test_id              # 同优先级保持原编号顺序
        ))
        # 替换原列表顺序但保持实例引用不变
        self.test_cases[:] = sorted_cases

        # 无测试用例时直接返回
        if len(self.test_cases) == 0:
            log.info("没有选择任何测试用例")
            return False

        # 重置所有测试用例状态
        for tc in self.test_cases:
            tc.status = TestStatus.PENDING.value
            tc.duration = 0.0
            tc.remark = ""

        self._run_next_test()
        return True

    def stop_test(self) -> None:
        """停止测试流程"""
        self.is_running = False
        # 测试停止时清理MQTT输出文件
        if self.device:
            log.debug("测试停止，清理MQTT输出文件")
            ADBService.clean_mqtt_output_file(self.device.serial)
        log.info("测试流程已停止")

    def _run_next_test(self) -> None:
        """执行下一个测试用例"""
        if not self.is_running:
            return

        self.current_test_index += 1

        # 所有测试用例执行完毕
        if self.current_test_index >= len(self.test_cases):
            self.is_running = False
            # 测试完成时清理MQTT输出文件
            if self.device:
                log.debug("测试完成，清理MQTT输出文件")
                ADBService.clean_mqtt_output_file(self.device.serial)
            log.info("=" * 50)
            log.info("所有测试用例执行完毕")
            self._notify_progress()
            return

        current_test = self.test_cases[self.current_test_index]
        
        # 检查设备类型支持
        if self.device:
            test_info = _test_case_registry.get(current_test.test_id)
            if test_info and test_info.get("supported_devices") is not None:
                if self.device.device_type not in test_info["supported_devices"]:
                    # 该测试用例不支持当前设备类型
                    current_test.status = TestStatus.NOT_SUPPORTED.value
                    current_test.remark = "当前设备类型不支持该测试"
                    log.info(f"[{self.current_test_index + 1}/{len(self.test_cases)}] ⚠  跳过不支持测试: {current_test.name}")
                    self._notify_status_changed(current_test)
                    self._notify_progress()
                    # 继续下一个测试
                    time.sleep(0.1)
                    self._run_next_test()
                    return

        # 正常执行测试
        current_test.status = TestStatus.RUNNING.value
        self._notify_status_changed(current_test)
        self._notify_progress()

        log.info(f"[{self.current_test_index + 1}/{len(self.test_cases)}] 开始测试: {current_test.name}")
        start_time = time.time()

        if current_test.test_id.startswith('A'):
            # 执行自动化测试
            success, remark = self.execute_auto_test(current_test)
            current_test.duration = round(time.time() - start_time, 2)

            if success:
                current_test.status = TestStatus.PASSED.value
                current_test.remark = remark
                log.info(f"✓ 测试通过: {current_test.name}，耗时: {current_test.duration}s")
            else:
                current_test.status = TestStatus.FAILED.value
                current_test.remark = remark
                log.error(f"✗ 测试失败: {current_test.name}，原因: {remark}")

            self._notify_status_changed(current_test)
            self._notify_progress()

            # 继续下一个测试
            time.sleep(0.5)
            self._run_next_test()
        else:
            # 人工测试用例：先执行测试用例函数完成前置操作，再等待确认
            test_info = _test_case_registry.get(current_test.test_id)
            if test_info and test_info.get("func"):
                try:
                    result = test_info["func"](self.device.serial)
                    if isinstance(result, tuple) and len(result) >= 2:
                        if len(result) == 3:
                            success, remark, reset_cmd = result
                            current_test.reset_cmd = reset_cmd
                        else:
                            success, remark = result
                            current_test.reset_cmd = None
                        
                        if success is None:
                            # 测试用例要求等待确认
                            current_test.remark = remark
                        elif not success:
                            current_test.status = TestStatus.FAILED.value
                            current_test.remark = remark
                            log.error(f"✗ 人工测试前置操作失败: {current_test.name}，原因: {remark}")
                            self._notify_status_changed(current_test)
                            self._notify_progress()
                            time.sleep(0.5)
                            self._run_next_test()
                            return
                    elif result is None:
                        # 测试用例要求等待确认
                        current_test.remark = "前置操作已完成，等待人工确认"
                        current_test.reset_cmd = None
                except Exception as e:
                    log.error(f"人工测试前置执行异常 {current_test.test_id}: {str(e)}")
                    current_test.remark = f"前置执行异常: {str(e)}"
            
            # 进入等待确认状态
            current_test.status = TestStatus.WAITING_CONFIRM.value
            log.info(f"⏸  等待人工确认: {current_test.name}")
            self._notify_status_changed(current_test)

            if self._manual_confirm_callback:
                self._manual_confirm_callback(current_test)

    def confirm_manual_test(self, test_id: str, passed: bool, remark: str = "") -> None:
        """人工测试确认"""
        for tc in self.test_cases:
            if tc.test_id == test_id:
                if passed:
                    tc.status = TestStatus.PASSED.value
                    log.info(f"✓ 人工测试通过: {tc.name}")
                    # 执行复位命令(如果有)
                    if hasattr(tc, 'reset_cmd') and tc.reset_cmd:
                        log.debug(f"执行测试复位命令: {tc.reset_cmd}")
                        success, output = ADBService.exec_shell(self.device.serial, tc.reset_cmd, timeout=5)
                        if success:
                            log.debug("复位命令执行成功")
                        else:
                            log.warning(f"复位命令执行失败: {output}")
                else:
                    tc.status = TestStatus.FAILED.value
                    tc.remark = remark
                    log.error(f"✗ 人工测试失败: {tc.name}，原因: {remark}")
                self._notify_status_changed(tc)
                self._notify_progress()
                
                # 执行测试用例函数的后置部分(确认后执行的代码)
                test_info = _test_case_registry.get(test_id)
                if test_info and test_info.get("func"):
                    try:
                        # 执行函数的剩余部分
                        import inspect
                        source = inspect.getsource(test_info["func"])
                        # 寻找return None后面的代码并执行
                        if "return None" in source:
                            # 重新执行整个函数，标记已确认状态
                            # 实际项目中应该用生成器或协程实现，这里简化处理
                            pass
                    except Exception as e:
                        log.debug(f"执行测试用例后置操作失败: {str(e)}")
                break

        # 继续下一个测试
        time.sleep(0.5)
        self._run_next_test()

    def execute_auto_test(self, test_case: TestModel) -> tuple[bool, str]:
        """执行自动化测试用例"""
        if not self.device:
            return False, "设备未连接"
            
        test_info = _test_case_registry.get(test_case.test_id)
        if test_info and test_info.get("func"):
            try:
                return test_info["func"](self.device.serial)
            except Exception as e:
                log.error(f"测试用例执行异常 {test_case.test_id}: {str(e)}")
                return False, f"执行异常: {str(e)}"
        else:
            return False, f"未找到测试用例实现: {test_case.test_id}"
