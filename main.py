import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QFile, QIODeviceBase
from ui.main_window import Ui_MainWindow
from core.logger import logger

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.statusbar.showMessage("✅ 测试工具启动成功")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())