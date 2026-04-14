# -*- coding: utf-8 -*-
import os
from PyQt6 import QtCore, QtWidgets, QtGui
from commons import LOG_DIR
from commons import get_file_modify_time, safe_delete_file
from commons import log


class TabLogView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_log_view")
        self._init_ui()
        self._connect_signals()
        self.refresh_log_list()

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

    def _connect_signals(self):
        """连接信号"""
        self.btn_log_refresh.clicked.connect(self.refresh_log_list)
        self.btn_log_del.clicked.connect(self.delete_selected_log)
        self.list_log_file.itemClicked.connect(self.preview_log)

    def refresh_log_list(self):
        """刷新日志文件列表"""
        self.list_log_file.clear()

        if not os.path.exists(LOG_DIR):
            return

        log_files = []
        for filename in os.listdir(LOG_DIR):
            if filename.endswith(".log"):
                file_path = os.path.join(LOG_DIR, filename)
                mtime = get_file_modify_time(file_path)
                log_files.append((filename, mtime, file_path))

        # 按时间倒序排列
        log_files.sort(key=lambda x: x[1], reverse=True)

        for filename, mtime, file_path in log_files:
            item = QtWidgets.QListWidgetItem(f"{filename}\n{mtime}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path)
            self.list_log_file.addItem(item)

        log.debug(f"日志列表已刷新，共 {len(log_files)} 个文件")

    def preview_log(self, item):
        """预览日志文件"""
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_log_preview.setPlainText(content)
                self.text_log_preview.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        except Exception as e:
            self.text_log_preview.setPlainText(f"读取日志失败: {str(e)}")
            log.error(f"读取日志文件失败: {file_path}, 错误: {str(e)}")

    def delete_selected_log(self):
        """删除选中的日志文件"""
        current_item = self.list_log_file.currentItem()
        if not current_item:
            return

        file_path = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        filename = os.path.basename(file_path)

        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除日志文件: {filename}？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if safe_delete_file(file_path):
                self.refresh_log_list()
                self.text_log_preview.clear()
                log.info(f"日志文件已删除: {filename}")
            else:
                log.error(f"删除日志文件失败: {filename}")