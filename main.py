import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QFile, QIODeviceBase
from ui.main_window import Ui_MainWindow
from utils.common import ensure_dirs
from utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_SIZE

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 设置窗口尺寸和最小尺寸
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # 或resize+setMinimumSize
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.statusbar.showMessage("✅ 测试工具启动成功")

if __name__ == "__main__":
    # 第一步：确保数据目录存在（必须优先执行）
    ensure_dirs()
    
    # 第二步：启动应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())