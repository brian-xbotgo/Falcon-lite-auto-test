# -*- coding: utf-8 -*-
"""
测试引擎核心模块
包含测试调度引擎和报告生成引擎
所有测试用例模块通过本引擎调度，无需修改核心代码
"""

from .test_service import TestService, TestStatus, register_test_case, auto_discover_test_cases
from .report_service import ReportService

__all__ = [
    'TestService', 'TestStatus', 
    'ReportService',
    'register_test_case', 'auto_discover_test_cases'
]
