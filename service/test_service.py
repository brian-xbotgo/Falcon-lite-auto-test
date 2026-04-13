# -*- coding: utf-8 -*-
"""
测试服务模块
功能：测试用例管理、流程调度、状态控制，自动化优先+人工集中确认
作者：wuzhibin
创建时间：2026-04-13
"""
import time
from typing import List, Callable, Optional
from enum import Enum
from model import TestModel, DeviceModel
from service import ADBService, log
from utils.config import DEFAULT_TEST_TIMEOUT


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "等待中"
    RUNNING = "执行中"
    PASSED = "通过"
    FAILED = "失败"
    WAITING_CONFIRM = "待确认"


class TestService:
    """
    测试引擎服务
    纯业务逻辑，不操作UI，通过回调通知状态变化
    """

    def __init__(self):
        self.test_cases: List[TestModel] = []
        self.current_test_index: int = -1
        self.is_running: bool = False
        self.device: Optional[DeviceModel] = None
        # 状态变化回调函数
        self._status_callback: Optional[Callable] = None
        self._progress_callback: Optional[Callable] = None
        self._manual_confirm_callback: Optional[Callable] = None

        # 初始化测试用例
        self._init_test_cases()

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
        """初始化测试用例列表 - 2自动化+2人工测试用例"""
        self.test_cases = [
            # 自动化测试用例
            TestModel(
                test_id="A001",
                module="系统",
                name="设备版本号读取",
                test_type="自动化",
                priority="P0",
            ),
            TestModel(
                test_id="A002",
                module="网络",
                name="网络连通性测试",
                test_type="自动化",
                priority="P0",
            ),
            # 人工测试用例
            TestModel(
                test_id="M001",
                module="硬件",
                name="LED指示灯检查",
                test_type="人工",
                priority="P1",
            ),
            TestModel(
                test_id="M002",
                module="显示",
                name="屏幕显示观察",
                test_type="人工",
                priority="P1",
            ),
        ]

    def set_device(self, device: DeviceModel) -> None:
        """设置测试目标设备"""
        self.device = device
        log.info(f"设置测试设备: {device.serial}")

    def get_all_test_cases(self) -> List[TestModel]:
        """获取所有测试用例"""
        return self.test_cases.copy()

    def get_test_progress(self) -> tuple[int, int]:
        """获取测试进度（已完成, 总数）"""
        completed = sum(1 for tc in self.test_cases
                       if tc.status in [TestStatus.PASSED.value, TestStatus.FAILED.value])
        return completed, len(self.test_cases)

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

        # 重置所有测试用例状态
        for tc in self.test_cases:
            tc.status = TestStatus.PENDING.value
            tc.duration = 0.0
            tc.remark = ""
            tc.executor = ""

        self._run_next_test()
        return True

    def stop_test(self) -> None:
        """停止测试流程"""
        self.is_running = False
        log.info("测试流程已停止")

    def _run_next_test(self) -> None:
        """执行下一个测试用例"""
        if not self.is_running:
            return

        self.current_test_index += 1

        # 所有测试用例执行完毕
        if self.current_test_index >= len(self.test_cases):
            self.is_running = False
            log.info("=" * 50)
            log.info("所有测试用例执行完毕")
            self._notify_progress()
            return

        current_test = self.test_cases[self.current_test_index]
        current_test.status = TestStatus.RUNNING.value
        self._notify_status_changed(current_test)
        self._notify_progress()

        log.info(f"[{self.current_test_index + 1}/{len(self.test_cases)}] 开始测试: {current_test.name}")
        start_time = time.time()

        if current_test.test_type == "自动化":
            # 执行自动化测试
            success, remark = self._execute_auto_test(current_test)
            current_test.duration = round(time.time() - start_time, 2)

            if success:
                current_test.status = TestStatus.PASSED.value
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
            # 人工测试用例，等待确认
            current_test.status = TestStatus.WAITING_CONFIRM.value
            log.info(f"⏸  等待人工确认: {current_test.name}")
            self._notify_status_changed(current_test)

            if self._manual_confirm_callback:
                self._manual_confirm_callback(current_test)

    def confirm_manual_test(self, test_id: str, passed: bool, remark: str = "", executor: str = "") -> None:
        """人工测试确认"""
        for tc in self.test_cases:
            if tc.test_id == test_id:
                if passed:
                    tc.status = TestStatus.PASSED.value
                    log.info(f"✓ 人工测试通过: {tc.name}")
                else:
                    tc.status = TestStatus.FAILED.value
                    tc.remark = remark
                    log.error(f"✗ 人工测试失败: {tc.name}，原因: {remark}")

                tc.executor = executor
                self._notify_status_changed(tc)
                self._notify_progress()
                break

        # 继续下一个测试
        time.sleep(0.5)
        self._run_next_test()

    def _execute_auto_test(self, test_case: TestModel) -> tuple[bool, str]:
        """执行自动化测试用例"""
        if test_case.test_id == "A001":
            return self._test_version_read()
        elif test_case.test_id == "A002":
            return self._test_network_connectivity()
        else:
            return False, "未知测试用例"

    def _test_version_read(self) -> tuple[bool, str]:
        """测试用例A001：读取设备版本号 /oem/usr/bin/version.txt"""
        log.debug("读取设备版本文件: /oem/usr/bin/version.txt")
        success, output = ADBService.exec_shell(
            self.device.serial,
            "cat /oem/usr/bin/version.txt",
            timeout=DEFAULT_TEST_TIMEOUT
        )

        if success and output.strip():
            return True, f"版本号: {output.strip()}"
        elif success:
            return False, "版本文件为空"
        else:
            # 兼容性处理：如果文件不存在，尝试通用版本获取
            log.debug("尝试通用版本获取方式")
            success2, output2 = ADBService.exec_shell(self.device.serial, "cat /proc/version")
            if success2 and output2.strip():
                return True, f"内核版本: {output2.strip()[:100]}..."
            return False, output

    def _test_network_connectivity(self) -> tuple[bool, str]:
        """测试用例A002：网络连通性测试"""
        log.debug("执行网络连通性测试: ping -c 3 192.168.1.1")
        success, output = ADBService.exec_shell(
            self.device.serial,
            "ping -c 3 192.168.1.1",
            timeout=30
        )

        if success and "0% packet loss" in output:
            return True, "网络连通正常"
        elif success:
            return False, f"网络丢包: {output.splitlines()[-1]}"
        else:
            return False, output
