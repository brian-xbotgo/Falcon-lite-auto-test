# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets, QtGui
from commons import TestService, log


class TabPartTest(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_part_test")
        self.test_service = TestService()
        self.current_test_index = -1
        self._init_ui()
        self._connect_signals()
        self._load_test_cases()

    def _init_ui(self):
        self.tree_test = QtWidgets.QTreeWidget(self)
        self.tree_test.setGeometry(QtCore.QRect(15, 15, 465, 400))
        self.tree_test.setHeaderLabel("测试项列表")
        self.tree_test.setColumnCount(2)
        self.tree_test.setHeaderLabels(["测试项", "状态"])
        self.tree_test.setColumnWidth(0, 300)
        self.tree_test.setColumnWidth(1, 100)
        
        self.btn_step = QtWidgets.QPushButton(self)
        self.btn_step.setGeometry(QtCore.QRect(500, 15, 100, 30))
        self.btn_step.setText("单步执行")
        self.btn_skip = QtWidgets.QPushButton(self)
        self.btn_skip.setGeometry(QtCore.QRect(500, 55, 100, 30))
        self.btn_skip.setText("跳过当前项")
        self.btn_reset = QtWidgets.QPushButton(self)
        self.btn_reset.setGeometry(QtCore.QRect(500, 95, 100, 30))
        self.btn_reset.setText("重置测试")
        
        self.text_part_log = QtWidgets.QTextEdit(self)
        self.text_part_log.setGeometry(QtCore.QRect(500, 140, 465, 275))
        self.text_part_log.setReadOnly(True)
        self.text_part_log.setPlaceholderText("部分测试日志")

    def _connect_signals(self):
        """连接信号"""
        self.btn_step.clicked.connect(self._on_step_execute)
        self.btn_skip.clicked.connect(self._on_skip_current)
        self.btn_reset.clicked.connect(self._on_reset_test)

    def _load_test_cases(self):
        """加载测试用例到树状列表"""
        self.tree_test.clear()

        # 分组显示测试用例
        auto_group = QtWidgets.QTreeWidgetItem(["自动化测试"])
        manual_group = QtWidgets.QTreeWidgetItem(["人工测试"])
        self.tree_test.addTopLevelItem(auto_group)
        self.tree_test.addTopLevelItem(manual_group)

        for tc in self.test_service.get_all_test_cases():
            if tc.test_type == "自动化":
                item = QtWidgets.QTreeWidgetItem(auto_group, [tc.name, tc.status])
            else:
                item = QtWidgets.QTreeWidgetItem(manual_group, [tc.name, tc.status])
            item.setData(0, QtCore.Qt.ItemDataRole.UserRole, tc.test_id)

        auto_group.setExpanded(True)
        manual_group.setExpanded(True)

        # 绑定日志输出
        def on_log_output(log_entry):
            self.text_part_log.append(log_entry)

        log.add_qt_handler(on_log_output)

    def _on_step_execute(self):
        """单步执行选中的测试用例"""
        # 获取当前选中的项
        selected_items = self.tree_test.selectedItems()
        if not selected_items:
            log.info("请先选择要测试的用例")
            self.text_part_log.append("请先选择要测试的用例")
            return
            
        item = selected_items[0]
        test_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        
        if not test_id:
            log.info("请选择具体的测试用例，而不是分组")
            self.text_part_log.append("请选择具体的测试用例，而不是分组")
            return
            
        test_cases = self.test_service.get_all_test_cases()
        
        # 找到对应的测试用例
        for i, tc in enumerate(test_cases):
            if tc.test_id == test_id:
                self.current_test_index = i
                current_test = tc
                break
        else:
            log.error("未找到对应的测试用例")
            self.text_part_log.append("未找到对应的测试用例")
            return
        log.info(f"=== 单步测试: 开始执行 {current_test.name} ===")
        self.text_part_log.append(f"\n=== 开始执行: {current_test.name} ===")

        # 更新UI状态
        self._update_test_item_status(current_test.test_id, "执行中")

        if current_test.test_type == "自动化":
            # 执行自动化测试
            log.info(f"[单步测试] 开始执行: {current_test.name}")
            success, remark = self.test_service.execute_auto_test(current_test)
            if success:
                current_test.status = "通过"
                current_test.remark = remark
                log.info(f"[单步测试] ✅ 通过: {current_test.name}")
                if remark:
                    log.info(f"[单步测试] 结果: {remark}")
                self.text_part_log.append(f"✅ 测试通过: {current_test.name}")
                if remark:
                    self.text_part_log.append(f"  结果: {remark}")
            else:
                current_test.status = "失败"
                current_test.remark = remark
                log.error(f"[单步测试] ❌ 失败: {current_test.name}, 原因: {remark}")
                self.text_part_log.append(f"❌ 测试失败: {current_test.name}")
                self.text_part_log.append(f"  原因: {remark}")
        else:
            # 人工测试，弹出确认对话框
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("人工测试确认")
            dialog.setFixedSize(400, 180)
            layout = QtWidgets.QVBoxLayout(dialog)

            label = QtWidgets.QLabel(f"请确认测试结果：\n\n【{current_test.name}】")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

            btn_layout = QtWidgets.QHBoxLayout()
            btn_pass = QtWidgets.QPushButton("✅ 通过")
            btn_fail = QtWidgets.QPushButton("❌ 失败")
            btn_pass.clicked.connect(lambda: (self._update_test_item_status(current_test.test_id, "通过"), dialog.accept()))
            btn_fail.clicked.connect(lambda: (self._update_test_item_status(current_test.test_id, "失败"), dialog.reject()))
            btn_layout.addWidget(btn_pass)
            btn_layout.addWidget(btn_fail)
            layout.addLayout(btn_layout)

            result = dialog.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                current_test.status = "通过"
                log.info(f"[单步测试] ✅ 人工测试通过: {current_test.name}")
                self.text_part_log.append(f"✅ 人工测试通过: {current_test.name}")
            else:
                current_test.status = "失败"
                log.error(f"[单步测试] ❌ 人工测试失败: {current_test.name}")
                self.text_part_log.append(f"❌ 人工测试失败: {current_test.name}")

        self._update_test_item_status(current_test.test_id, current_test.status)

    def _on_skip_current(self):
        """跳过当前测试用例"""
        test_cases = self.test_service.get_all_test_cases()
        if self.current_test_index >= 0 and self.current_test_index < len(test_cases):
            tc = test_cases[self.current_test_index]
            tc.status = "跳过"
            self._update_test_item_status(tc.test_id, "跳过")
            log.info(f"[单步测试] ⏭  跳过测试: {tc.name}")
            self.text_part_log.append(f"⏭  跳过测试: {tc.name}")
            self.current_test_index += 1

    def _on_reset_test(self):
        """重置所有测试用例状态"""
        for tc in self.test_service.get_all_test_cases():
            tc.status = "等待中"
            tc.duration = 0.0
            tc.remark = ""
            self._update_test_item_status(tc.test_id, "等待中")

        self.current_test_index = -1
        self.text_part_log.clear()
        self.text_part_log.append("🔄 测试已重置")
        log.info("部分测试已重置")

    def _update_test_item_status(self, test_id: str, status: str):
        """更新测试项状态显示"""
        # 递归查找测试项
        def find_item(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                item_id = child.data(0, QtCore.Qt.ItemDataRole.UserRole)
                if item_id == test_id:
                    child.setText(1, status)
                    # 设置状态颜色
                    if status == "通过":
                        child.setBackground(1, QtGui.QBrush(QtGui.QColor("#E8F5E9")))
                        child.setForeground(1, QtGui.QBrush(QtGui.QColor("#2E7D32")))
                    elif status == "失败":
                        child.setBackground(1, QtGui.QBrush(QtGui.QColor("#FFEBEE")))
                        child.setForeground(1, QtGui.QBrush(QtGui.QColor("#C62828")))
                    elif status == "执行中":
                        child.setBackground(1, QtGui.QBrush(QtGui.QColor("#E3F2FD")))
                        child.setForeground(1, QtGui.QBrush(QtGui.QColor("#1565C0")))
                    elif status == "跳过":
                        child.setBackground(1, QtGui.QBrush(QtGui.QColor("#FFF3E0")))
                        child.setForeground(1, QtGui.QBrush(QtGui.QColor("#EF6C00")))
                    return True

                if find_item(child):
                    return True
            return False

        for i in range(self.tree_test.topLevelItemCount()):
            if find_item(self.tree_test.topLevelItem(i)):
                break