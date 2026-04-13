# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets

class TabFileManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_file_manager")
        self._init_ui()

    def _init_ui(self):
        self.btn_upload = QtWidgets.QPushButton(self)
        self.btn_upload.setGeometry(QtCore.QRect(15, 15, 80, 30))
        self.btn_upload.setText("上传")
        self.btn_download = QtWidgets.QPushButton(self)
        self.btn_download.setGeometry(QtCore.QRect(105, 15, 80, 30))
        self.btn_download.setText("下载")
        self.btn_del_file = QtWidgets.QPushButton(self)
        self.btn_del_file.setGeometry(QtCore.QRect(195, 15, 80, 30))
        self.btn_del_file.setText("删除")
        self.btn_refresh_file = QtWidgets.QPushButton(self)
        self.btn_refresh_file.setGeometry(QtCore.QRect(285, 15, 80, 30))
        self.btn_refresh_file.setText("刷新")

        self.tree_dir = QtWidgets.QTreeWidget(self)
        self.tree_dir.setGeometry(QtCore.QRect(15, 55, 300, 420))
        self.tree_dir.setHeaderLabel("目录结构")

        self.table_file = QtWidgets.QTableWidget(self)
        self.table_file.setGeometry(QtCore.QRect(330, 55, 635, 420))
        self.table_file.setColumnCount(3)
        self.table_file.setHorizontalHeaderLabels(["文件名", "大小", "修改时间"])