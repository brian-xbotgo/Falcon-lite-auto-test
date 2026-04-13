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
        self.groupBox_device.setGeometry(QtCore.QRect(15, 15, 950, 120))
        self.groupBox_device.setTitle("设备连接")
        self.table_devices = QtWidgets.QTableWidget(self.groupBox_device)
        self.table_devices.setGeometry(QtCore.QRect(10, 25, 750, 85))
        self.table_devices.setColumnCount(5)
        self.table_devices.setHorizontalHeaderLabels(["序列号", "连接方式", "状态", "固件版本", "Root状态"])
        self.btn_refresh_dev = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_refresh_dev.setGeometry(QtCore.QRect(770, 25, 90, 30))
        self.btn_refresh_dev.setText("刷新设备")
        self.btn_net_adb = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_net_adb.setGeometry(QtCore.QRect(770, 65, 90, 30))
        self.btn_net_adb.setText("网络ADB")

        # 2. 测试项选择区
        self.groupBox_test_sel = QtWidgets.QGroupBox(self)
        self.groupBox_test_sel.setGeometry(QtCore.QRect(15, 145, 465, 120))
        self.groupBox_test_sel.setTitle("测试项选择")
        self.check_auto_all = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_auto_all.setGeometry(QtCore.QRect(10, 25, 120, 20))
        self.check_auto_all.setText("自动化测试(全选)")
        self.check_manual_all = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_manual_all.setGeometry(QtCore.QRect(10, 55, 120, 20))
        self.check_manual_all.setText("人工测试(全选)")

        # 3. 参数配置区
        self.groupBox_config = QtWidgets.QGroupBox(self)
        self.groupBox_config.setGeometry(QtCore.QRect(490, 145, 475, 120))
        self.groupBox_config.setTitle("参数配置")
        self.label_firm = QtWidgets.QLabel(self.groupBox_config)
        self.label_firm.setGeometry(QtCore.QRect(10, 25, 70, 20))
        self.label_firm.setText("固件路径：")
        self.edit_firm = QtWidgets.QLineEdit(self.groupBox_config)
        self.edit_firm.setGeometry(QtCore.QRect(80, 25, 300, 25))
        self.btn_firm = QtWidgets.QPushButton(self.groupBox_config)
        self.btn_firm.setGeometry(QtCore.QRect(390, 25, 60, 25))
        self.btn_firm.setText("选择")
        self.label_loop = QtWidgets.QLabel(self.groupBox_config)
        self.label_loop.setGeometry(QtCore.QRect(10, 60, 70, 20))
        self.label_loop.setText("循环次数：")
        self.spin_loop = QtWidgets.QSpinBox(self.groupBox_config)
        self.spin_loop.setGeometry(QtCore.QRect(80, 60, 80, 25))
        self.spin_loop.setValue(1)

        # 4. 测试控制区
        self.groupBox_test_ctrl = QtWidgets.QGroupBox(self)
        self.groupBox_test_ctrl.setGeometry(QtCore.QRect(15, 275, 950, 60))
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

        # 5. 实时日志区（修复：添加样式表确保边框完整）
        self.groupBox_log = QtWidgets.QGroupBox(self)
        self.groupBox_log.setGeometry(QtCore.QRect(15, 345, 950, 180))
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
        self.text_log.setGeometry(QtCore.QRect(10, 25, 930, 145))
        self.text_log.setReadOnly(True)