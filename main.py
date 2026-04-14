import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
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

        label = QLabel(f"请确认测试结果：\n\n【{self.test_case.name}")
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
        # 测试状态变化回调
        def on_status_changed(test_case):
            self._update_test_status(test_case)

        # 测试进度回调
        def on_progress(completed, total):
            self.statusbar.showMessage(f"测试进度: {completed}/{total} ({completed/total*100:.1f}%)")
            if completed == total:
                # 测试完成，自动生成报告
                report_path = ReportService.save_report(self.test_service.get_all_test_cases(), self.test_service.device)
                log.info(f"测试报告已生成: {report_path}")
                self.statusbar.showMessage(f"测试完成，报告已保存")

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
        # 设备按钮
        self.tab_all.btn_connect_adb.clicked.connect(self._on_scan_devices)
        self.tab_all.btn_disconnect_adb.clicked.connect(self._on_disconnect_device)

        # 测试控制按钮
        self.tab_all.btn_start.clicked.connect(self._on_start_test)
        self.tab_all.btn_pause.clicked.connect(self._on_pause_test)
        self.tab_all.btn_stop.clicked.connect(self._on_stop_test)

    def _on_scan_devices(self):
        """扫描设备"""
        log.info("开始扫描USB设备")
        devices = ADBService.scan_devices()

        # 更新设备列表
        self.tab_all.table_devices.setRowCount(len(devices))
        for row, device in enumerate(devices):
            self.tab_all.table_devices.setItem(row, 0, QTableWidgetItem(device.serial))
            self.tab_all.table_devices.setItem(row, 1, QTableWidgetItem(device.conn_type))
            self.tab_all.table_devices.setItem(row, 2, QTableWidgetItem(device.status))
            self.tab_all.table_devices.setItem(row, 3, QTableWidgetItem(device.version))
            self.tab_all.table_devices.setItem(row, 4, QTableWidgetItem("是" if device.is_rooted else "否"))

        if devices:
            self.test_service.set_device(devices[0])
            log.info(f"发现 {len(devices)} 个设备，已选择: {devices[0].serial}")
            self.statusbar.showMessage(f"已连接设备: {devices[0].serial}")

    def _on_disconnect_device(self):
        """断开设备"""
        self.tab_all.table_devices.setRowCount(0)
        self.statusbar.showMessage("设备已断开")
        log.info("设备已断开")

    def _on_start_test(self):
        """开始测试"""
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