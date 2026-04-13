# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets
# 【顶部导入】无循环、无报错
from .tab_all_test import TabAllTest
from .tab_part_test import TabPartTest
from .tab_file_manager import TabFileManager
from .tab_log_view import TabLogView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 650)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 650))

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 980, 580))
        self.tabWidget.setObjectName("tabWidget")

        # 标签页
        self.tab_all = TabAllTest()
        self.tabWidget.addTab(self.tab_all, "全部测试")
        self.tab_part = TabPartTest()
        self.tabWidget.addTab(self.tab_part, "部分测试")
        self.tab_file = TabFileManager()
        self.tabWidget.addTab(self.tab_file, "文件管理")
        self.tab_log = TabLogView()
        self.tabWidget.addTab(self.tab_log, "日志查看")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RV1126B 测试工具"))