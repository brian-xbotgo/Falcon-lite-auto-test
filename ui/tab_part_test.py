# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets

class TabPartTest(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_part_test")
        self._init_ui()

    def _init_ui(self):
        self.tree_test = QtWidgets.QTreeWidget(self)
        self.tree_test.setGeometry(QtCore.QRect(15, 15, 465, 400))
        self.tree_test.setHeaderLabel("测试项列表")
        
        self.btn_step = QtWidgets.QPushButton(self)
        self.btn_step.setGeometry(QtCore.QRect(500, 15, 100, 30))
        self.btn_step.setText("单步执行")
        self.btn_skip = QtWidgets.QPushButton(self)
        self.btn_skip.setGeometry(QtCore.QRect(500, 55, 100, 30))
        self.btn_skip.setText("跳过当前项")
        
        self.text_part_log = QtWidgets.QTextEdit(self)
        self.text_part_log.setGeometry(QtCore.QRect(500, 100, 465, 315))
        self.text_part_log.setReadOnly(True)
        self.text_part_log.setPlaceholderText("部分测试日志")