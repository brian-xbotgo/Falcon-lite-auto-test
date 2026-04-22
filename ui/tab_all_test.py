# -*- coding: utf-8 -*-
import asyncio
from PyQt6 import QtCore, QtWidgets, QtGui
from commons import BleService, ADBService, DeviceModel, log, TestService


class BleScanWorker(QtCore.QThread):
    """蓝牙扫描工作线程"""
    scan_finished = QtCore.pyqtSignal(list)
    
    def run(self):
        try:
            devices = asyncio.run(BleService.scan_devices())
            self.scan_finished.emit(devices)
        except Exception as e:
            log.error(f"蓝牙扫描线程异常: {str(e)}")
            self.scan_finished.emit([])


class TabAllTest(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_all_test")
        
        # 成员变量
        self.current_device: DeviceModel = None
        self.ble_devices = []
        self.scan_worker = None
        self.test_service = TestService()
        
        self._init_ui()
        self._init_events()
        self._init_timer()

    def _init_ui(self):
        # 1. 设备连接区
        self.groupBox_device = QtWidgets.QGroupBox(self)
        self.groupBox_device.setGeometry(QtCore.QRect(15, 15, 720, 200))
        self.groupBox_device.setTitle("设备连接")
        
        # 1.1 上半区：蓝牙设备列表区
        # 蓝牙设备列表 - 设备名称 + 设备类型
        self.table_ble_devices = QtWidgets.QTableWidget(self.groupBox_device)
        self.table_ble_devices.setGeometry(QtCore.QRect(10, 25, 520, 110))
        self.table_ble_devices.setColumnCount(2)
        self.table_ble_devices.setHorizontalHeaderLabels(["设备名称", "设备类型"])
        self.table_ble_devices.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table_ble_devices.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_ble_devices.setAlternatingRowColors(True)
        # 设置列宽比例 6:4, 总宽度520px
        self.table_ble_devices.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.table_ble_devices.setColumnWidth(0, 306)  # 60%
        self.table_ble_devices.setColumnWidth(1, 204)  # 40%
        self.table_ble_devices.verticalHeader().setVisible(False)
        self.table_ble_devices.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # 按钮区
        self.btn_ble_refresh = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_ble_refresh.setGeometry(QtCore.QRect(540, 25, 90, 30))
        self.btn_ble_refresh.setText("刷新扫描")
        
        self.btn_connect_adb = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_connect_adb.setGeometry(QtCore.QRect(540, 65, 90, 30))
        self.btn_connect_adb.setText("连接设备")
        
        self.btn_disconnect_adb = QtWidgets.QPushButton(self.groupBox_device)
        self.btn_disconnect_adb.setGeometry(QtCore.QRect(540, 105, 90, 30))
        self.btn_disconnect_adb.setText("断开设备")
        
        # 1.2 下半区：已连接设备信息
        self.table_connected_device = QtWidgets.QTableWidget(self.groupBox_device)
        self.table_connected_device.setGeometry(QtCore.QRect(10, 140, 630, 55))
        self.table_connected_device.setColumnCount(6)
        self.table_connected_device.setHorizontalHeaderLabels(["设备名称", "序列号", "设备类型", "连接方式", "状态", "固件版本"])
        self.table_connected_device.setRowCount(1)
        self.table_connected_device.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_connected_device.verticalHeader().setVisible(False)
        self.table_connected_device.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_connected_device.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        # 2. 测试用例状态区
        self.groupBox_test_status = QtWidgets.QGroupBox(self)
        self.groupBox_test_status.setGeometry(QtCore.QRect(750, 15, 215, 595))
        self.groupBox_test_status.setTitle("测试用例状态")
        
        # 成功用例列表
        self.label_passed = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_passed.setGeometry(QtCore.QRect(10, 25, 100, 20))
        self.label_passed.setText("✅ 已成功: 0")
        self.list_passed = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_passed.setGeometry(QtCore.QRect(10, 45, 195, 130))
        self.list_passed.setStyleSheet("QListWidget { color: #2E7D32; }")
        
        # 失败用例列表
        self.label_failed = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_failed.setGeometry(QtCore.QRect(10, 185, 100, 20))
        self.label_failed.setText("❌ 已失败: 0")
        self.list_failed = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_failed.setGeometry(QtCore.QRect(10, 205, 195, 130))
        self.list_failed.setStyleSheet("QListWidget { color: #C62828; }")
        
        # 当前测试用例
        self.label_current = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_current.setGeometry(QtCore.QRect(10, 345, 100, 20))
        self.label_current.setText("⏳ 当前测试:")
        self.text_current = QtWidgets.QLabel(self.groupBox_test_status)
        self.text_current.setGeometry(QtCore.QRect(10, 365, 195, 50))
        self.text_current.setStyleSheet("QLabel { background-color: #E3F2FD; padding: 5px; border-radius: 3px; }")
        self.text_current.setWordWrap(True)
        self.text_current.setText("等待开始测试")
        
        # 未完成用例列表
        self.label_pending = QtWidgets.QLabel(self.groupBox_test_status)
        self.label_pending.setGeometry(QtCore.QRect(10, 425, 100, 20))
        self.label_pending.setText("📋 待执行: 0")
        self.list_pending = QtWidgets.QListWidget(self.groupBox_test_status)
        self.list_pending.setGeometry(QtCore.QRect(10, 445, 195, 135))
        self.list_pending.setStyleSheet("QListWidget { color: #757575; }")

        # 3. 测试项选择区
        self.groupBox_test_sel = QtWidgets.QGroupBox(self)
        self.groupBox_test_sel.setGeometry(QtCore.QRect(15, 220, 720, 95))
        self.groupBox_test_sel.setTitle("测试项选择")
        
        # 自动测试项复选框
        self.check_auto = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_auto.setGeometry(QtCore.QRect(20, 25, 120, 20))
        self.check_auto.setText("自动测试项")
        self.check_auto.setChecked(True)
        
        # 人工测试项复选框
        self.check_manual = QtWidgets.QCheckBox(self.groupBox_test_sel)
        self.check_manual.setGeometry(QtCore.QRect(20, 55, 120, 20))
        self.check_manual.setText("人工测试项")
        self.check_manual.setChecked(True)

        # 5. 测试控制区
        self.groupBox_test_ctrl = QtWidgets.QGroupBox(self)
        self.groupBox_test_ctrl.setGeometry(QtCore.QRect(15, 325, 720, 60))
        self.groupBox_test_ctrl.setTitle("测试控制")
        
        # 测试控制按钮
        self.btn_start = QtWidgets.QPushButton(self.groupBox_test_ctrl)
        self.btn_start.setGeometry(QtCore.QRect(10, 25, 90, 30))
        self.btn_start.setText("开始测试")
        
        self.btn_stop = QtWidgets.QPushButton(self.groupBox_test_ctrl)
        self.btn_stop.setGeometry(QtCore.QRect(110, 25, 90, 30))
        self.btn_stop.setText("停止测试")

        # 6. 实时日志区
        self.groupBox_log = QtWidgets.QGroupBox(self)
        self.groupBox_log.setGeometry(QtCore.QRect(15, 395, 720, 215))
        self.groupBox_log.setTitle("实时日志")
        self.text_log = QtWidgets.QTextEdit(self.groupBox_log)
        self.text_log.setGeometry(QtCore.QRect(10, 25, 700, 180))
        self.text_log.setReadOnly(True)
    
    def _init_events(self):
        """初始化事件绑定"""
        self.btn_ble_refresh.clicked.connect(self._on_ble_refresh_clicked)
        self.btn_connect_adb.clicked.connect(self._on_connect_clicked)
        self.btn_disconnect_adb.clicked.connect(self._on_disconnect_clicked)
        self.table_ble_devices.itemSelectionChanged.connect(self._on_ble_device_selected)
    
    def _init_timer(self):
        """初始化定时器"""
        # 设备在线状态检测定时器 1秒
        self.device_check_timer = QtCore.QTimer(self)
        self.device_check_timer.timeout.connect(self._check_device_online)
        self.device_check_timer.start(1000)
    
    def _on_ble_refresh_clicked(self):
        """刷新蓝牙扫描按钮点击"""
        # 防止重复点击
        try:
            if self.scan_worker and self.scan_worker.isRunning():
                log.debug("扫描进行中，忽略重复点击")
                return
        except RuntimeError:
            # C++对象已被删除，重置引用
            self.scan_worker = None
            
        # 扫描期间禁用整个设备区域，防止用户操作
        self.groupBox_device.setEnabled(False)
        self.btn_ble_refresh.setText("扫描中...")
        
        self.scan_worker = BleScanWorker()
        self.scan_worker.scan_finished.connect(self._on_ble_scan_finished)
        self.scan_worker.finished.connect(self._on_scan_worker_finished)
        self.scan_worker.start()
        
    def _on_scan_worker_finished(self):
        """扫描工作线程完成回调"""
        # 强制处理所有待处理绘制事件，确保UI完全更新
        QtWidgets.QApplication.processEvents()
        
        if self.scan_worker:
            self.scan_worker.deleteLater()
            self.scan_worker = None
        
        # 所有操作完成后重新启用控件
        self.groupBox_device.setEnabled(True)
        self.btn_ble_refresh.setEnabled(True)
        self.btn_ble_refresh.setText("刷新扫描")
    
    def _on_ble_scan_finished(self, devices):
        """蓝牙扫描完成"""
        self.ble_devices = devices
        self.table_ble_devices.setRowCount(0)
        
        # 已连接设备置顶
        connected_device = None
        other_devices = []
        
        for device in devices:
            if self.current_device and device["name"] == self.current_device.device_name:
                connected_device = device
            else:
                other_devices.append(device)
        
        row = 0
        # 先添加已连接设备
        if connected_device:
            self.table_ble_devices.insertRow(row)
            # 设备名称
            name_item = QtWidgets.QTableWidgetItem(f"✅ {connected_device['name']} (已连接)")
            name_item.setData(QtCore.Qt.ItemDataRole.UserRole, connected_device)
            name_item.setBackground(QtGui.QColor('lightgreen'))
            self.table_ble_devices.setItem(row, 0, name_item)
            # 设备类型
            device_type = "Chameleon" if connected_device["name"].startswith("XbotGo-") else "Falcon"
            type_item = QtWidgets.QTableWidgetItem(device_type)
            type_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table_ble_devices.setItem(row, 1, type_item)
            row += 1
        
        # 添加其他设备
        for device in other_devices:
            self.table_ble_devices.insertRow(row)
            # 设备名称
            name_item = QtWidgets.QTableWidgetItem(device["name"])
            name_item.setData(QtCore.Qt.ItemDataRole.UserRole, device)
            self.table_ble_devices.setItem(row, 0, name_item)
            # 设备类型
            device_type = "Chameleon" if device["name"].startswith("XbotGo-") else "Falcon"
            type_item = QtWidgets.QTableWidgetItem(device_type)
            type_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table_ble_devices.setItem(row, 1, type_item)
            row += 1
        
        log.info(f"蓝牙扫描完成，发现 {len(devices)} 个设备")
    
    def _on_ble_device_selected(self):
        """蓝牙设备选中"""
        selected_rows = self.table_ble_devices.selectedItems()
        if selected_rows:
            device = selected_rows[0].data(QtCore.Qt.ItemDataRole.UserRole)
            log.debug(f"选中蓝牙设备: {device['name']}")
    
    def _on_connect_clicked(self):
        """连接按钮点击"""
        selected_rows = self.table_ble_devices.selectedItems()
        if not selected_rows:
            log.warning("请先选择蓝牙设备")
            return
        
        ble_device = selected_rows[0].data(QtCore.Qt.ItemDataRole.UserRole)
        ble_name = ble_device["name"]
        
        log.info(f"尝试连接设备: {ble_name}")
        self.btn_connect_adb.setEnabled(False)
        self.btn_connect_adb.setText("连接中...")
        
        # 扫描USB设备
        usb_devices = ADBService.scan_devices()
        
        # 匹配设备
        matched_device = None
        for device in usb_devices:
            if ADBService.verify_device_name(device.serial, ble_name):
                matched_device = device
                matched_device.device_name = ble_name
                break
        
        if matched_device:
            self.current_device = matched_device
            self._update_connected_device_table()
            log.info(f"设备连接成功: {ble_name} [{matched_device.serial}]")
        else:
            log.error(f"未找到匹配的USB设备: {ble_name}")
        
        self.btn_connect_adb.setEnabled(True)
        self.btn_connect_adb.setText("连接设备")
    
    def _on_disconnect_clicked(self):
        """断开按钮点击"""
        if self.current_device:
            log.info(f"断开设备: {self.current_device.device_name}")
            self.current_device = None
            self._update_connected_device_table()
            # 刷新蓝牙列表
            self._on_ble_refresh_clicked()
    
    def _check_device_online(self):
        """定时器检测设备在线状态"""
        if not self.current_device:
            return
        
        # 检查设备是否仍在线
        devices = ADBService.timer_scan_devices()
        device_online = False
        
        for device in devices:
            if device.serial == self.current_device.serial:
                device_online = True
                # 更新设备信息
                self.current_device.status = "在线"
                self.current_device.version = device.version
                break
        
        if not device_online:
            if self.current_device.status == "在线":
                log.warning(f"设备离线: {self.current_device.device_name}")
            self.current_device.status = "离线"
        
        self._update_connected_device_table()
    
    def _update_connected_device_table(self):
        """更新已连接设备表格"""
        # 清空表格
        for col in range(self.table_connected_device.columnCount()):
            self.table_connected_device.setItem(0, col, QtWidgets.QTableWidgetItem(""))
        
        if not self.current_device:
            return
        
        # 填充数据
        items = [
            QtWidgets.QTableWidgetItem(self.current_device.device_name),
            QtWidgets.QTableWidgetItem(self.current_device.serial),
            QtWidgets.QTableWidgetItem(self.current_device.get_device_type_name()),
            QtWidgets.QTableWidgetItem(self.current_device.conn_type),
            QtWidgets.QTableWidgetItem(self.current_device.status),
            QtWidgets.QTableWidgetItem(self.current_device.version)
        ]
        
        # 状态颜色
        if self.current_device.status == "在线":
            items[3].setBackground(QtCore.Qt.GlobalColor.green)
        else:
            items[3].setBackground(QtCore.Qt.GlobalColor.red)
        
        for col, item in enumerate(items):
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table_connected_device.setItem(0, col, item)