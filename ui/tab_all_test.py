# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets

class TabAllTest(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_all_test")
        self._init_ui()

    def _init_ui(self):
        # 1. 设备连接区
        self.groupBox_device = QtWidgets.QGroupBox(self)
        self.groupBox_device.setGeometry(QtCore.QRect(15, 15, 720, 120))
        self.groupBox_device.setTitle("设备连接")
        self.table_devices = QtWidgets.QTableWidget(self.groupBox_device)
        self.table_devices.setGeometry(QtCore.QRect(10, 25, 520, 85))
        self.table_devices.setColumnCount(5)
        self.table_devices.setHorizontalHeaderLabels(["序列号", "连接方式", "状态", "固件版本", "Root状态"])
        self.btn_connect_adb = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_connect_adb.setGeometry(QtCore.QRect(540, 25, 90, 30))
        self.btn_connect_adb.setText("连接设备")
        self.btn_disconnect_adb = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_disconnect_adb.setGeometry(QtCore.QRect(540, 65, 90, 30))
        self.btn_disconnect_adb.setText("断开设备")

        # 2. 测试用例状态区（右侧新增）
        self.groupBox_test_status = QtWidgets.QGroupBox(self)
        self.groupBox_test_status.setGeometry(QtCore.QRect(750, 15, 215, 510))
        self.groupBox_test_status.setTitle("测试用例状态")
        
        # 成功用例列表
        self.label_passed = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_passed.setGeometry(QtCore.QRect(10, 25, 100, 20))
        self.label_passed.setText("✅ 已成功: 0")
        self.list_passed = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_passed.setGeometry(QtCore.QRect(10, 45, 195, 110))
        self.list_passed.setStyleSheet("QListWidget { color: #2E7D32; }")
        
        # 失败用例列表
        self.label_failed = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_failed.setGeometry(QtCore.QRect(10, 160, 100, 20))
        self.label_failed.setText("❌ 已失败: 0")
        self.list_failed = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_failed.setGeometry(QtCore.QRect(10, 180, 195, 110))
        self.list_failed.setStyleSheet("QListWidget { color: #C62828; }")
        
        # 当前测试用例
        self.label_current = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_current.setGeometry(QtCore.QRect(10, 295, 100, 20))
        self.label_current.setText("⏳ 当前测试:")
        self.text_current = QtWidgets.QLabel(self.groupBox_test_status)
        self.text_current.setGeometry(QtCore.QRect(10, 315, 195, 50))
        self.text_current.setStyleSheet("QLabel { background-color: #E3F2FD; padding: 5px; border-radius: 3px; }")
        self.text_current.setWordWrap(True)
        self.text_current.setText("等待开始测试")
        
        # 未完成用例列表
        self.label_pending = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_pending.setGeometry(QtCore.QRect(10, 370, 100, 20))
        self.label_pending.setText("📋 待执行: 0")
        self.list_pending = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_pending.setGeometry(QtCore.QRect(10, 390, 195, 110))
        self.list_pending.setStyleSheet("QListWidget { color: #757575; }")

        # 3. 测试项选择区
        self.groupBox_test_sel = QtWidgets.QGroupBox(self)
        self.groupBox_test_sel.setGeometry(QtCore.QRect(15, 145, 350, 120))
        self.groupBox_test_sel.setTitle("测试项选择")
        self.check_auto_all = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_auto_all.setGeometry(QtCore.QRect(10, 25, 120, 20))
        self.check_auto_all.setText("自动化测试(全选)")
        self.check_manual_all = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_manual_all.setGeometry(QtCore.QRect(10, 55, 120, 20))
        self.check_manual_all.setText("人工测试(全选)")

        # 4. 参数配置区
        self.groupBox_config = QtWidgets.QGroupBox(self)
        self.groupBox_config.setGeometry(QtCore.QRect(375, 145, 360, 120))
        self.groupBox_config.setTitle("参数配置")
        self.label_firm = QtWidgets.QLabel(self.groupBox_config)
        self.label_firm.setGeometry(QtCore.QRect(10, 25, 70, 20))
        self.label_firm.setText("固件路径：")
        self.edit_firm = QtWidgets.QLineEdit(self.groupBox_config)
        self.edit_firm.setGeometry(QtCore.QRect(80, 25, 200, 25))
        self.btn_firm = QtWidgets.QPushButton(self.groupBox_config)
        self.btn_firm.setGeometry(QtCore.QRect(290, 25, 60, 25))
        self.btn_firm.setText("选择")
        self.label_loop = QtWidgets.QLabel(self.groupBox_config)
        self.label_loop.setGeometry(QtCore.QRect(10, 60, 70, 20))
        self.label_loop.setText("循环次数：")
        self.spin_loop = QtWidgets.QSpinBox(self.groupBox_config)
        self.spin_loop.setGeometry(QtCore.QRect(80, 60, 80, 25))
        self.spin_loop.setValue(1)

        # 5. 测试控制区
        self.groupBox_test_ctrl = QtWidgets.QGroupBox(self)
        self.groupBox_test_ctrl.setGeometry(QtCore.QRect(15, 275, 720, 60))
        self.groupBox_test_ctrl.setTitle("测试控制")
        self.btn_start = QtWidgets.QPushButton(self.groupBox_test_ctrl)
        self.btn_start.setGeometry(QtCore.QRect(15, 20, 100, 30))
        self.btn_start.setText("开始测试")
        self.btn_pause = QtWidgets.QPushButton(self.groupBox_test_ctrl)
        self.btn_pause.setGeometry(QtCore.QRect(130, 20, 100, 30))
        self.btn_pause.setText("暂停测试")
        self.btn_stop = QtWidgets.QPushButton(self.groupBox_test_ctrl)
        self.btn_stop.setGeometry(QtCore.QRect(245, 20, 100, 30))
        self.btn_stop.setText("停止测试")

        # 6. 实时日志区
        self.groupBox_log = QtWidgets.QGroupBox(self)
        self.groupBox_log.setGeometry(QtCore.QRect(15, 345, 720, 180))
        self.groupBox_log.setTitle("实时日志")
        # 强制修复底部边线：统一设置样式
        self.groupBox_log.setStyleSheet("""
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.text_log = QtWidgets.QTextEdit(self.groupBox_log)
        self.text_log.setGeometry(QtCore.QRect(10, 25, 700, 145))
        self.text_log.setReadOnly(True)