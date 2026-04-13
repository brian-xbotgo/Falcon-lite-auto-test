# core/test_case.py
from dataclasses import dataclass
from enum import Enum

class TestType(Enum):
    """测试类型：自动化/人工确认"""
    AUTO = "自动化"
    MANUAL = "人工确认"

class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "等待中"
    RUNNING = "执行中"
    PASSED = "通过"
    FAILED = "失败"
    SKIPPED = "跳过"

@dataclass
class TestCase:
    """测试项数据类"""
    id: int
    module: str  # 所属模块（如：系统升级、基础硬件）
    name: str  # 测试项名称
    test_type: TestType  # 自动化/人工
    priority: str  # P0/P1/P2
    status: TestStatus = TestStatus.PENDING
    duration: float = 0.0  # 执行耗时（秒）
    remark: str = ""  # 备注/失败原因
    executor: str = ""  # 人工确认人

# 预定义默认测试项（后续可从Excel读取，这里先写死）
DEFAULT_TEST_CASES = [
    TestCase(id=1, module="系统与升级", name="OTA升级测试", test_type=TestType.AUTO, priority="P0"),
    TestCase(id=2, module="基础硬件", name="开关机测试", test_type=TestType.AUTO, priority="P0"),
    TestCase(id=3, module="网络通信", name="WiFi连接测试", test_type=TestType.AUTO, priority="P0"),
    TestCase(id=4, module="基础硬件", name="LED灯语测试", test_type=TestType.MANUAL, priority="P0"),
    TestCase(id=5, module="基础硬件", name="蜂鸣器测试", test_type=TestType.MANUAL, priority="P0"),
    TestCase(id=6, module="显示交互", name="屏幕显示测试", test_type=TestType.MANUAL, priority="P0"),
]