# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets
from .tab_all_test import TabAllTest
from .tab_part_test import TabPartTest
from .tab_file_manager import TabFileManager
from .tab_device_manager import TabDeviceManager
from commons import APP_NAME, APP_VERSION

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, test_service):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 670)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 670))

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 980, 640))
        self.tabWidget.setObjectName("tabWidget")

        # 标签页
        self.tab_all = TabAllTest()
        self.tabWidget.addTab(self.tab_all, "全部测试")
        self.tab_part = TabPartTest(test_service)
        self.tabWidget.addTab(self.tab_part, "部分测试")
        self.tab_file = TabFileManager()
        self.tabWidget.addTab(self.tab_file, "文件管理")
        self.tab_device = TabDeviceManager()
        self.tabWidget.addTab(self.tab_device, "设备系统")

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
        MainWindow.setWindowTitle(_translate("MainWindow", f"{APP_NAME} v{APP_VERSION}"))