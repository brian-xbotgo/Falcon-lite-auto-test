# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets

class TabLogView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_log_view")
        self._init_ui()

    def _init_ui(self):
        self.list_log_file = QtWidgets.QListWidget(self)
        self.list_log_file.setGeometry(QtCore.QRect(15, 15, 300, 460))
        
        self.text_log_preview = QtWidgets.QTextEdit(self)
        self.text_log_preview.setGeometry(QtCore.QRect(330, 15, 635, 400))
        self.text_log_preview.setReadOnly(True)
        self.text_log_preview.setPlaceholderText("日志内容预览")
        
        self.btn_log_del = QtWidgets.QPushButton(self)
        self.btn_log_del.setGeometry(QtCore.QRect(330, 425, 100, 30))
        self.btn_log_del.setText("删除选中")
        self.btn_log_export = QtWidgets.QPushButton(self)
        self.btn_log_export.setGeometry(QtCore.QRect(440, 425, 100, 30))
        self.btn_log_export.setText("导出日志")
        self.btn_log_refresh = QtWidgets.QPushButton(self)
        self.btn_log_refresh.setGeometry(QtCore.QRect(550, 425, 100, 30))
        self.btn_log_refresh.setText("刷新列表")