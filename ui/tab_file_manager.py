# -*- coding: utf-8 -*-
import os
from PyQt6 import QtCore, QtWidgets
from commons import DATA_DIR, REPORT_DIR, LOG_DIR, FIRMWARE_DIR
from commons import format_file_size, get_file_modify_time, safe_delete_file
from commons import log


class TabFileManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_file_manager")
        self._init_ui()
        self._connect_signals()
        self.refresh_file_list()

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
        self.table_file.setColumnWidth(0, 300)
        self.table_file.setColumnWidth(1, 120)
        self.table_file.setColumnWidth(2, 180)
        # 设置表格为只读，禁止编辑
        self.table_file.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_file.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table_file.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # 设置选中效果
        self.table_file.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        # 增强选中效果
        self.table_file.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QTableView::selection-background-color: #2196F3;
            QTableView::selection-color: white;
        """)
        # 禁止编辑表格内容
        self.table_file.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # 设置选择模式
        self.table_file.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_file.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

    def _connect_signals(self):
        """连接信号"""
        self.btn_refresh_file.clicked.connect(self.refresh_file_list)
        self.btn_del_file.clicked.connect(self.delete_selected_file)
        self.btn_upload.clicked.connect(self.upload_file)
        self.btn_download.clicked.connect(self.download_file)
        self.tree_dir.itemClicked.connect(self.on_dir_selected)
        self.table_file.itemDoubleClicked.connect(self.preview_file)

    def refresh_file_list(self):
        """刷新目录和文件列表"""
        self.tree_dir.clear()
        self.table_file.setRowCount(0)

        # 构建目录树
        root_item = QtWidgets.QTreeWidgetItem(["data"])
        root_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, DATA_DIR)
        self.tree_dir.addTopLevelItem(root_item)

        # 子目录
        subdirs = [
            ("logs", LOG_DIR),
            ("reports", REPORT_DIR),
            ("firmware", FIRMWARE_DIR)
        ]

        for dir_name, dir_path in subdirs:
            dir_item = QtWidgets.QTreeWidgetItem(root_item, [dir_name])
            dir_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, dir_path)

        root_item.setExpanded(True)

        # 默认显示reports目录
        self.current_dir = REPORT_DIR
        self._load_files(self.current_dir)
        log.debug("文件列表已刷新")

    def on_dir_selected(self, item):
        """目录选中事件"""
        self.current_dir = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        self._load_files(self.current_dir)

    def _load_files(self, dir_path):
        """加载指定目录下的文件"""
        self.table_file.setRowCount(0)

        if not os.path.exists(dir_path):
            return

        files = []
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                stat_info = os.stat(file_path)
                files.append({
                    "name": filename,
                    "path": file_path,
                    "size": stat_info.st_size,
                    "mtime": get_file_modify_time(file_path)
                })

        # 按修改时间倒序
        files.sort(key=lambda x: x["mtime"], reverse=True)

        for row, file_info in enumerate(files):
            self.table_file.insertRow(row)
            self.table_file.setItem(row, 0, QtWidgets.QTableWidgetItem(file_info["name"]))
            self.table_file.setItem(row, 1, QtWidgets.QTableWidgetItem(format_file_size(file_info["size"])))
            self.table_file.setItem(row, 2, QtWidgets.QTableWidgetItem(file_info["mtime"]))
            # 保存完整路径
            self.table_file.item(row, 0).setData(QtCore.Qt.ItemDataRole.UserRole, file_info["path"])

    def delete_selected_file(self):
        """删除选中的文件"""
        current_row = self.table_file.currentRow()
        if current_row < 0:
            return

        item = self.table_file.item(current_row, 0)
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        filename = os.path.basename(file_path)

        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除文件: {filename}？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if safe_delete_file(file_path):
                self._load_files(self.current_dir)
                log.info(f"文件已删除: {filename}")
            else:
                log.error(f"删除文件失败: {filename}")

    def preview_file(self, item):
        """预览文件内容"""
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        filename = os.path.basename(file_path)

        # 创建预览对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"文件预览: {filename}")
        dialog.setFixedSize(800, 600)
        layout = QtWidgets.QVBoxLayout(dialog)

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                text_edit.setPlainText(content)
        except Exception as e:
            text_edit.setPlainText(f"无法读取文件: {str(e)}")

        layout.addWidget(text_edit)

        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        dialog.exec()

    def preview_file_content(self, item):
        """双击预览文件内容"""
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        filename = os.path.basename(file_path)

        # 创建预览对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"查看文件 - {filename}")
        dialog.resize(800, 600)
        layout = QtWidgets.QVBoxLayout(dialog)

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                text_edit.setPlainText(content)
        except Exception as e:
            text_edit.setPlainText(f"无法读取文件内容: {str(e)}")

        layout.addWidget(text_edit)

        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        dialog.exec()

    def upload_file(self):
        """上传文件到当前目录"""
        if not hasattr(self, 'current_dir'):
            self.current_dir = FIRMWARE_DIR

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择要上传的文件",
            "",
            "所有文件 (*.*)"
        )

        if file_path:
            import shutil
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.current_dir, filename)

            try:
                shutil.copy2(file_path, dest_path)
                self._load_files(self.current_dir)
                log.info(f"文件上传成功: {filename}")
            except Exception as e:
                log.error(f"文件上传失败: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "上传失败", f"上传失败: {str(e)}")

    def download_file(self):
        """下载选中的文件"""
        current_row = self.table_file.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择要下载的文件")
            return

        item = self.table_file.item(current_row, 0)
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        filename = os.path.basename(file_path)

        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存文件",
            filename,
            "所有文件 (*.*)"
        )

        if dest_path:
            import shutil
            try:
                shutil.copy2(file_path, dest_path)
                log.info(f"文件下载成功: {filename} -> {dest_path}")
            except Exception as e:
                log.error(f"文件下载失败: {str(e)}")
                QtWidgets.QMessageBox.critical(self, "下载失败", f"下载失败: {str(e)}")