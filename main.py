import sys
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from ui.main_window import Ui_MainWindow
from commons import ensure_dirs, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_SIZE, log, ADBService, TestService, ReportService


class ManualConfirmDialog(QDialog):
    """人工测试确认对话框"""
    def __init__(self, test_case, parent=None):
        super().__init__(parent)
        self.test_case = test_case
        self.result = False
        self.remark = ""
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("人工测试确认")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout(self)

        label = QLabel(f"请确认测试结果：\n\n【{self.test_case.name}】")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self.btn_pass = QPushButton("✅ 通过")
        self.btn_fail = QPushButton("❌ 失败")
        self.btn_pass.clicked.connect(self._on_pass)
        self.btn_fail.clicked.connect(self._on_fail)
        btn_layout.addWidget(self.btn_pass)
        btn_layout.addWidget(self.btn_fail)
        layout.addLayout(btn_layout)

    def _on_pass(self):
        self.result = True
        self.accept()

    def _on_fail(self):
        self.result = False
        self.accept()


class ReportConfirmDialog(QDialog):
    """测试报告确认对话框"""
    def __init__(self, test_cases, device, parent=None):
        super().__init__(parent)
        self.test_cases = test_cases
        self.device = device
        self.tester = ""
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("测试报告确认")
        self.setFixedSize(800, 500)
        layout = QVBoxLayout(self)

        # 统计信息
        total = len(self.test_cases)
        passed = sum(1 for tc in self.test_cases if tc.status == "通过")
        failed = sum(1 for tc in self.test_cases if tc.status == "失败")
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0.0
        
        stat_label = QLabel(f"测试统计：总计 {total} 项, 通过 {passed} 项, 失败 {failed} 项, 通过率 {pass_rate}%")
        stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stat_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(stat_label)

        # 测试结果表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["测试ID", "模块", "测试名称", "类型", "优先级", "状态"])
        self.table.setRowCount(total)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        for i, tc in enumerate(self.test_cases):
            self.table.setItem(i, 0, QTableWidgetItem(tc.test_id))
            self.table.setItem(i, 1, QTableWidgetItem(tc.module))
            self.table.setItem(i, 2, QTableWidgetItem(tc.name))
            self.table.setItem(i, 3, QTableWidgetItem(tc.test_type))
            self.table.setItem(i, 4, QTableWidgetItem(tc.priority))
            
            status_item = QTableWidgetItem(tc.status)
            if tc.status == "通过":
                status_item.setForeground(Qt.GlobalColor.green)
            elif tc.status == "失败":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(i, 5, status_item)
            
        layout.addWidget(self.table)

        # 测试人输入
        tester_layout = QHBoxLayout()
        tester_label = QLabel("测试人：")
        self.tester_input = QLineEdit(self)
        self.tester_input.setPlaceholderText("请输入测试人姓名")
        self.tester_input.setMaximumWidth(200)
        tester_layout.addWidget(tester_label)
        tester_layout.addWidget(self.tester_input)
        tester_layout.addStretch()
        layout.addLayout(tester_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("✅ 确定生成报告")
        self.btn_cancel = QPushButton("❌ 取消")
        self.btn_confirm.clicked.connect(self._on_confirm)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_confirm)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _on_confirm(self):
        self.tester = self.tester_input.text().strip() or "未知"
        self.accept()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 设置窗口尺寸和最小尺寸
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(*WINDOW_MIN_SIZE)

        # 初始化服务（唯一入口）
        self.test_service = TestService()
        self._setup_callbacks()
        self._connect_signals()

        # 绑定日志到UI
        def on_log_output(log_entry):
            self.tab_all.text_log.append(log_entry)

        log.add_qt_handler(on_log_output)

        self.statusbar.showMessage("✅ 测试工具启动成功")
        log.info("RV1126B测试工具启动成功")

    def _setup_callbacks(self):
        """设置服务回调"""
        # 防止重复弹出对话框标志
        self._report_shown = False
        
        # 测试状态变化回调
        def on_status_changed(test_case):
            self._update_test_status(test_case)

        # 测试进度回调
        def on_progress(completed, total):
            self.statusbar.showMessage(f"测试进度: {completed}/{total} ({completed/total*100:.1f}%)")
            if completed == total and not self._report_shown:
                self._report_shown = True
                # 测试完成，弹出报告确认对话框
                dialog = ReportConfirmDialog(self.test_service.get_all_test_cases(), self.test_service.device, self)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    report_path = ReportService.save_report(
                        self.test_service.get_all_test_cases(), 
                        self.test_service.device,
                        tester=dialog.tester
                    )
                    log.info(f"测试报告已生成: {report_path}")
                    self.statusbar.showMessage(f"测试完成，报告已保存")
                else:
                    log.info("用户取消生成测试报告")
                    self.statusbar.showMessage("测试完成，报告生成已取消")

        # 人工确认回调
        def on_manual_confirm(test_case):
            dialog = ManualConfirmDialog(test_case, self)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                self.test_service.confirm_manual_test(
                    test_case.test_id,
                    dialog.result,
                    dialog.remark,
                    "操作员"
                )

        self.test_service.set_status_callback(on_status_changed)
        self.test_service.set_progress_callback(on_progress)
        self.test_service.set_manual_confirm_callback(on_manual_confirm)

    def _connect_signals(self):
        """连接UI信号"""
        # 测试控制按钮
        self.tab_all.btn_start.clicked.connect(self._on_start_test)
        self.tab_all.btn_pause.clicked.connect(self._on_pause_test)
        self.tab_all.btn_stop.clicked.connect(self._on_stop_test)
        
        # 监听设备连接状态变化
        self._last_device = None
        def on_device_changed():
            current_device = self.tab_all.current_device
            if current_device != self._last_device:
                self._last_device = current_device
                if current_device:
                    self.test_service.set_device(current_device)
                    self.statusbar.showMessage(f"已连接设备: {current_device.serial}")
                    self.tab_device.on_device_connected(current_device.serial)
                else:
                    self.test_service.set_device(None)
                    self.statusbar.showMessage("设备已断开")
                    self.tab_device.on_device_disconnected()
        
        # 定时器检测设备变化
        self.device_monitor_timer = QTimer(self)
        self.device_monitor_timer.timeout.connect(on_device_changed)
        self.device_monitor_timer.start(500)



    def _on_start_test(self):
        """开始测试"""
        # 重置报告对话框标志
        self._report_shown = False
        
        # 清空测试状态列表
        self.tab_all.list_passed.clear()
        self.tab_all.list_failed.clear()
        self.tab_all.list_pending.clear()

        # 加载所有测试用例到待执行列表
        for tc in self.test_service.get_all_test_cases():
            self.tab_all.list_pending.addItem(f"{tc.test_id} - {tc.name}")
        self.tab_all.label_pending.setText(f"📋 待执行: {self.tab_all.list_pending.count()}")

        if self.test_service.start_test():
            log.info("测试流程已启动")
        else:
            self.statusbar.showMessage("请先连接设备")

    def _on_pause_test(self):
        """暂停测试"""
        log.info("测试已暂停")
        self.statusbar.showMessage("测试已暂停")

    def _on_stop_test(self):
        """停止测试"""
        self.test_service.stop_test()
        self.statusbar.showMessage("测试已停止")

    def _update_test_status(self, test_case):
        """更新测试用例状态"""
        # 从待执行列表移除
        for i in range(self.tab_all.list_pending.count()):
            item = self.tab_all.list_pending.item(i)
            if item and test_case.test_id in item.text():
                self.tab_all.list_pending.takeItem(i)
                break

        if test_case.status == "通过":
            self.tab_all.list_passed.addItem(f"{test_case.test_id} - {test_case.name}")
            self.tab_all.label_passed.setText(f"✅ 已成功: {self.tab_all.list_passed.count()}")
        elif test_case.status == "失败":
            self.tab_all.list_failed.addItem(f"{test_case.test_id} - {test_case.name}")
            self.tab_all.label_failed.setText(f"❌ 已失败: {self.tab_all.list_failed.count()}")
        elif test_case.status == "执行中":
            self.tab_all.text_current.setText(f"{test_case.test_id} - {test_case.name}")
        elif test_case.status == "待确认":
            self.tab_all.text_current.setText(f"⏳ 等待人工确认:\n{test_case.name}")

        self.tab_all.label_pending.setText(f"📋 待执行: {self.tab_all.list_pending.count()}")


if __name__ == "__main__":
    # 第一步：确保数据目录存在（必须优先执行）
    ensure_dirs()

    # 第二步：启动应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())