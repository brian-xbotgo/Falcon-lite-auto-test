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
from typing import List, Dict, Optional
from datetime import datetime
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side
from ..test_model import TestModel, Priority, Module
from .test_service import TestStatus
from ..device_model import DeviceModel
from ..config import REPORT_DIR, DEFAULT_REPORT_FORMAT, SUPPORTED_REPORT_FORMATS
from ..log_service import log
from ..common import get_current_time_str


class ReportService:
    """测试报告服务"""

    @staticmethod
    def generate_report(test_cases: List[TestModel], device: Optional[DeviceModel] = None, tester: str = "未知") -> Dict:
        """
        生成测试报告统计数据
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :param tester: 测试人姓名
        :return: 统计数据字典
        """
        total = len(test_cases)
        passed = sum(1 for tc in test_cases if tc.status == "通过")
        failed = sum(1 for tc in test_cases if tc.status == "失败")
        pending = sum(1 for tc in test_cases if tc.status == "等待中")
        running = sum(1 for tc in test_cases if tc.status == "执行中")
        waiting = sum(1 for tc in test_cases if tc.status == "待确认")
        not_supported = sum(1 for tc in test_cases if tc.status == "不支持")

        # 通过率计算排除不支持的测试项
        valid_total = total - not_supported
        pass_rate = round(passed / valid_total * 100, 2) if valid_total > 0 else 0.0

        # 调试：输出所有测试用例信息
        log.debug("========== 报告包含的测试用例 ==========")
        for i, tc in enumerate(test_cases):
            log.debug(f"[{i}] {tc.test_id} - {tc.name} - 状态: {tc.status}")
        log.debug("========================================")

        report_data = {
            "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tester": tester,
            "device_info": {
                "serial": device.serial if device else "未知",
                "device_name": device.device_name if device else "未知",
                "version": device.version if device else "未知",
                "device_type": device.get_device_type_name() if device else "未知"
            } if device else {},
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pending": pending,
                "running": running,
                "waiting_confirm": waiting,
                "not_supported": not_supported,
                "pass_rate": pass_rate
            },
            "test_cases": [
                {
                    "test_id": tc.test_id,
                    "module": tc.module,
                    "name": tc.name,
                    "test_type": tc.test_type,
                    "priority": str(tc.priority),
                    "status": tc.status,
                    "duration": tc.duration,
                    "remark": tc.remark
                } for tc in test_cases
            ]
        }

        log.info(f"生成测试报告: 总计 {total} 项, 通过 {passed} 项, 失败 {failed} 项, 通过率 {pass_rate}%")
        return report_data

    @staticmethod
    def save_csv_report(test_cases: List[TestModel], device: Optional[DeviceModel] = None, tester: str = "未知") -> str:
        """
        保存为CSV格式报告
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :param tester: 测试人姓名
        :return: 报告文件路径
        """
        report_data = ReportService.generate_report(test_cases, device, tester)

        filename = f"{get_current_time_str()}_test_report.csv"
        file_path = os.path.join(REPORT_DIR, filename)

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # 写入报告头
                writer.writerow(["冒烟测试报告"])
                writer.writerow(["生成时间", report_data["report_time"]])
                writer.writerow(["设备名称", report_data["device_info"].get("device_name", "未知")])
                writer.writerow(["设备序列号", report_data["device_info"].get("serial", "未知")])
                writer.writerow(["设备类型", report_data["device_info"].get("device_type", "未知")])
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
                writer.writerow(["测试ID", "模块", "测试名称", "类型", "优先级", "状态", "备注"])
                for tc in report_data["test_cases"]:
                    writer.writerow([
                        tc["test_id"],
                        tc["module"],
                        tc["name"],
                        tc["test_type"],
                        tc["priority"],
                        tc["status"],
                        tc["remark"]
                    ])
                writer.writerow([])
                
                # 写入测试人
                tester = report_data.get("tester", "未知")
                writer.writerow(["测试人", tester])

            log.info(f"测试报告已保存: {file_path}")
            return file_path

        except Exception as e:
            log.error(f"保存测试报告失败: {str(e)}")
            return ""

    @staticmethod
    def save_html_report(test_cases: List[TestModel], device: Optional[DeviceModel] = None, tester: str = "未知") -> str:
        """
        保存为HTML格式报告
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :param tester: 测试人姓名
        :return: 报告文件路径
        """
        report_data = ReportService.generate_report(test_cases, device, tester)

        filename = f"{get_current_time_str()}_test_report.html"
        file_path = os.path.join(REPORT_DIR, filename)

        try:
            # 生成HTML内容
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .report-header {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }}
        .summary-item {{ background: white; padding: 10px; border-radius: 4px; text-align: center; }}
        .summary-value {{ font-size: 24px; font-weight: bold; }}
        .passed {{ color: #2E7D32; }}
        .failed {{ color: #C62828; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f5f5f5; font-weight: bold; }}
        tr:hover {{ background-color: #f9f9f9; }}
        .status-passed {{ color: #2E7D32; font-weight: bold; }}
        .status-failed {{ color: #C62828; font-weight: bold; }}
        .report-footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>自动化冒烟测试报告</h1>
    
    <div class="report-header">
        <h3>设备信息</h3>
        <p><strong>生成时间:</strong> {report_data["report_time"]}</p>
        <p><strong>设备名称:</strong> {report_data["device_info"].get("device_name", "未知")}</p>
        <p><strong>设备序列号:</strong> {report_data["device_info"].get("serial", "未知")}</p>
        <p><strong>设备类型:</strong> {report_data["device_info"].get("device_type", "未知")}</p>
        <p><strong>固件版本:</strong> {report_data["device_info"].get("version", "未知")}</p>
        
        <div class="summary-grid">
            <div class="summary-item">
                <div>测试项总数</div>
                <div class="summary-value">{report_data["summary"]["total"]}</div>
            </div>
            <div class="summary-item">
                <div>通过</div>
                <div class="summary-value passed">{report_data["summary"]["passed"]}</div>
            </div>
            <div class="summary-item">
                <div>失败</div>
                <div class="summary-value failed">{report_data["summary"]["failed"]}</div>
            </div>
            <div class="summary-item">
                <div>通过率</div>
                <div class="summary-value">{report_data["summary"]["pass_rate"]}%</div>
            </div>
        </div>
    </div>

    <h3>测试详情</h3>
    <table>
        <thead>
            <tr>
                <th>测试ID</th>
                <th>模块</th>
                <th>测试名称</th>
                <th>类型</th>
                <th>优先级</th>
                <th>状态</th>
                <th>备注</th>
            </tr>
        </thead>
        <tbody>
"""

            # 生成测试用例表格
            for tc in report_data["test_cases"]:
                status_class = "status-passed" if tc["status"] == "通过" else "status-failed"
                html_content += f"""
            <tr>
                <td>{tc["test_id"]}</td>
                <td>{tc["module"]}</td>
                <td>{tc["name"]}</td>
                <td>{tc["test_type"]}</td>
                <td>{tc["priority"]}</td>
                <td class="{status_class}">{tc["status"]}</td>
                <td>{tc["remark"]}</td>
            </tr>"""

            # 添加尾部
            html_content += f"""
        </tbody>
    </table>

    <div class="report-footer">
        <p><strong>测试人:</strong> {report_data.get("tester", "未知")}</p>
        <p><strong>报告生成时间:</strong> {report_data["report_time"]}</p>
    </div>
</body>
</html>
"""

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            log.info(f"测试报告已保存: {file_path}")
            return file_path

        except Exception as e:
            log.error(f"保存测试报告失败: {str(e)}")
            return ""

    @staticmethod
    def save_report(test_cases: List[TestModel], device: Optional[DeviceModel] = None,
                    format_type: str = DEFAULT_REPORT_FORMAT, tester: str = "未知") -> str:
        """
        保存测试报告
        :param test_cases: 测试用例列表
        :param device: 测试设备信息
        :param format_type: 报告格式
        :param tester: 测试人姓名
        :return: 报告文件路径
        """
        # 默认使用HTML格式
        return ReportService.save_html_report(test_cases, device, tester)

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
