# -*- coding: utf-8 -*-
"""
报告服务模块
功能：测试报告生成、统计、保存到data/reports目录
作者：wuzhibin
创建时间：2026-04-13
"""
import os
import csv
from datetime import datetime
from typing import List, Dict
from model import TestModel, DeviceModel
from utils.config import REPORT_DIR, DEFAULT_REPORT_FORMAT
from utils.common import get_current_time_str
from service import log


class ReportService:
    """测试报告服务"""

    @staticmethod
    def generate_report(test_cases: List[TestModel], device: DeviceModel = None) -> Dict:
        """
        生成测试报告统计数据
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :return: 统计数据字典
        """
        total = len(test_cases)
        passed = sum(1 for tc in test_cases if tc.status == "通过")
        failed = sum(1 for tc in test_cases if tc.status == "失败")
        pending = sum(1 for tc in test_cases if tc.status == "等待中")
        running = sum(1 for tc in test_cases if tc.status == "执行中")
        waiting = sum(1 for tc in test_cases if tc.status == "待确认")

        pass_rate = round(passed / total * 100, 2) if total > 0 else 0.0

        report_data = {
            "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "device_info": {
                "serial": device.serial if device else "未知",
                "version": device.version if device else "未知",
                "is_rooted": device.is_rooted if device else False
            } if device else {},
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pending": pending,
                "running": running,
                "waiting_confirm": waiting,
                "pass_rate": pass_rate
            },
            "test_cases": [
                {
                    "test_id": tc.test_id,
                    "module": tc.module,
                    "name": tc.name,
                    "test_type": tc.test_type,
                    "priority": tc.priority,
                    "status": tc.status,
                    "duration": tc.duration,
                    "remark": tc.remark,
                    "executor": tc.executor
                } for tc in test_cases
            ]
        }

        log.info(f"生成测试报告: 总计 {total} 项, 通过 {passed} 项, 失败 {failed} 项, 通过率 {pass_rate}%")
        return report_data

    @staticmethod
    def save_csv_report(test_cases: List[TestModel], device: DeviceModel = None) -> str:
        """
        保存为CSV格式报告
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :return: 报告文件路径
        """
        report_data = ReportService.generate_report(test_cases, device)

        filename = f"{get_current_time_str()}_test_report.csv"
        file_path = os.path.join(REPORT_DIR, filename)

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # 写入报告头
                writer.writerow(["RV1126B 冒烟测试报告"])
                writer.writerow(["生成时间", report_data["report_time"]])
                writer.writerow(["设备序列号", report_data["device_info"].get("serial", "未知")])
                writer.writerow(["固件版本", report_data["device_info"].get("version", "未知")])
                writer.writerow([])

                # 写入统计摘要
                writer.writerow(["测试统计"])
                writer.writerow(["测试项总数", report_data["summary"]["total"]])
                writer.writerow(["通过", report_data["summary"]["passed"]])
                writer.writerow(["失败", report_data["summary"]["failed"]])
                writer.writerow(["通过率", f"{report_data['summary']['pass_rate']}%"])
                writer.writerow([])

                # 写入详细测试结果
                writer.writerow(["测试ID", "模块", "测试名称", "类型", "优先级", "状态", "耗时(s)", "备注", "确认人"])
                for tc in report_data["test_cases"]:
                    writer.writerow([
                        tc["test_id"],
                        tc["module"],
                        tc["name"],
                        tc["test_type"],
                        tc["priority"],
                        tc["status"],
                        tc["duration"],
                        tc["remark"],
                        tc["executor"]
                    ])

            log.info(f"CSV报告已保存: {file_path}")
            return file_path

        except Exception as e:
            log.error(f"保存CSV报告失败: {str(e)}")
            return ""

    @staticmethod
    def save_report(test_cases: List[TestModel], device: DeviceModel = None,
                    format_type: str = DEFAULT_REPORT_FORMAT) -> str:
        """
        保存测试报告
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :param format_type: 报告格式
        :return: 报告文件路径
        """
        # 目前先支持CSV格式，后续根据需求增加Excel/HTML格式
        return ReportService.save_csv_report(test_cases, device)

    @staticmethod
    def get_report_list() -> List[str]:
        """获取历史报告列表"""
        reports = []
        try:
            for filename in sorted(os.listdir(REPORT_DIR), reverse=True):
                if filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".html"):
                    file_path = os.path.join(REPORT_DIR, filename)
                    reports.append(file_path)
        except Exception as e:
            log.error(f"获取报告列表失败: {str(e)}")
        return reports
