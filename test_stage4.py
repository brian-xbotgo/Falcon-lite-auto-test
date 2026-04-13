#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阶段4功能测试脚本
测试测试服务和报告服务功能
"""
from service import log, ADBService, TestService, ReportService
from model import DeviceModel


def test_test_service():
    """测试测试服务"""
    print("\n=== 测试 TestService ===")

    test_service = TestService()

    # 获取测试用例
    test_cases = test_service.get_all_test_cases()
    print(f"测试用例总数: {len(test_cases)}")
    print("\n测试用例列表:")
    for tc in test_cases:
        print(f"  [{tc.test_id}] {tc.name} - {tc.test_type} - {tc.priority}")

    # 创建模拟设备
    mock_device = DeviceModel(
        serial="TEST_DEVICE_001",
        status="在线",
        version="Test_V1.0.0",
        is_rooted=True
    )
    test_service.set_device(mock_device)

    # 设置回调
    def on_status_changed(test_case):
        print(f"\n状态变化: {test_case.name} -> {test_case.status}")

    def on_progress(completed, total):
        print(f"进度: {completed}/{total} ({completed/total*100:.1f}%)")

    def on_manual_confirm(test_case):
        print(f"\n需要人工确认: {test_case.name}")
        print(f"请确认测试结果 [Y/N]: ", end="")
        # 模拟人工确认
        import time
        time.sleep(1)
        print("Y (模拟)")
        test_service.confirm_manual_test(test_case.test_id, True, "人工确认通过", "TestUser")

    test_service.set_status_callback(on_status_changed)
    test_service.set_progress_callback(on_progress)
    test_service.set_manual_confirm_callback(on_manual_confirm)

    # 开始测试
    print("\n开始测试流程...")
    test_service.start_test()

    # 等待测试完成
    import time
    while test_service.is_running:
        time.sleep(0.5)

    print("\n测试完成！")

    # 生成报告
    print("\n=== 测试 ReportService ===")
    report_data = ReportService.generate_report(test_cases, mock_device)
    print(f"测试统计:")
    print(f"  总数: {report_data['summary']['total']}")
    print(f"  通过: {report_data['summary']['passed']}")
    print(f"  失败: {report_data['summary']['failed']}")
    print(f"  通过率: {report_data['summary']['pass_rate']}%")

    # 保存报告
    report_path = ReportService.save_report(test_cases, mock_device, "csv")
    if report_path:
        print(f"\n报告已保存: {report_path}")


if __name__ == "__main__":
    print("RV1126B 测试工具 - 阶段4测试")
    print("=" * 50)

    test_test_service()

    print("\n" + "=" * 50)
    print("阶段4测试完成！")
