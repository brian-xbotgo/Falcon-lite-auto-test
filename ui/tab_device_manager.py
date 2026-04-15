# -*- coding: utf-8 -*-
import os
from PyQt6 import QtCore, QtWidgets
from commons import ADBService, format_file_size, log


class TabDeviceManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_device_manager")
        self.current_serial = None
        self.current_path = "/"
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.btn_refresh = QtWidgets.QPushButton(self)
        self.btn_refresh.setGeometry(QtCore.QRect(15, 15, 80, 30))
        self.btn_refresh.setText("刷新")

        self.btn_download = QtWidgets.QPushButton(self)
        self.btn_download.setGeometry(QtCore.QRect(105, 15, 80, 30))
        self.btn_download.setText("下载文件")

        self.btn_upload = QtWidgets.QPushButton(self)
        self.btn_upload.setGeometry(QtCore.QRect(195, 15, 80, 30))
        self.btn_upload.setText("上传文件")

        self.tree_dir = QtWidgets.QTreeWidget(self)
        self.tree_dir.setGeometry(QtCore.QRect(15, 55, 300, 520))
        self.tree_dir.setHeaderLabel("设备目录")
        self.tree_dir.setItemsExpandable(True)
        self.tree_dir.setExpandsOnDoubleClick(True)

        self.table_file = QtWidgets.QTableWidget(self)
        self.table_file.setGeometry(QtCore.QRect(330, 55, 635, 350))
        self.table_file.setColumnCount(4)
        self.table_file.setHorizontalHeaderLabels(["文件名", "类型", "大小", "修改时间"])
        self.table_file.setColumnWidth(0, 260)
        self.table_file.setColumnWidth(1, 80)
        self.table_file.setColumnWidth(2, 120)
        self.table_file.setColumnWidth(3, 175)
        self.table_file.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_file.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_file.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table_file.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)

        self.text_preview = QtWidgets.QTextEdit(self)
        self.text_preview.setGeometry(QtCore.QRect(330, 415, 635, 160))
        self.text_preview.setReadOnly(True)
        self.text_preview.setPlaceholderText("双击文件预览内容")

        self._update_ui_state(False)

    def _connect_signals(self):
        """连接信号"""
        self.btn_refresh.clicked.connect(self.refresh_file_list)
        self.btn_download.clicked.connect(self.download_file)
        self.btn_upload.clicked.connect(self.upload_file)
        self.tree_dir.itemClicked.connect(self.on_dir_selected)
        self.tree_dir.itemExpanded.connect(self.on_dir_expanded)
        self.table_file.itemDoubleClicked.connect(self.preview_file)

    def _update_ui_state(self, connected):
        """更新UI状态"""
        self.btn_refresh.setEnabled(connected)
        self.btn_download.setEnabled(connected)
        self.btn_upload.setEnabled(connected)
        self.tree_dir.setEnabled(connected)
        self.table_file.setEnabled(connected)

        if not connected:
            self.tree_dir.clear()
            self.table_file.setRowCount(0)
            self.text_preview.clear()
            self.text_preview.setPlaceholderText("请先连接设备")

    def on_device_connected(self, serial):
        """设备连接事件"""
        self.current_serial = serial
        self._update_ui_state(True)
        self.refresh_file_list()
        log.info(f"设备已连接，设备文件浏览器就绪: {serial}")

    def on_device_disconnected(self):
        """设备断开事件"""
        self.current_serial = None
        self._update_ui_state(False)
        log.info("设备已断开，设备文件浏览器已禁用")

    def refresh_file_list(self):
        """刷新目录和文件列表"""
        if not self.current_serial:
            return

        self.tree_dir.clear()
        self.table_file.setRowCount(0)

        # 构建根目录
        root_item = QtWidgets.QTreeWidgetItem(["/"])
        root_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, "/")
        root_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        self.tree_dir.addTopLevelItem(root_item)

        self.current_path = "/"
        self._load_files("/")
        log.debug("设备目录已刷新")

    def on_dir_expanded(self, item):
        """目录展开事件 - 懒加载子目录"""
        path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if item.childCount() == 0:
            self._load_subdirs(item, path)

    def on_dir_selected(self, item):
        """目录选中事件"""
        self.current_path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        self._load_files(self.current_path)

    def _load_subdirs(self, parent_item, parent_path):
        """懒加载子目录"""
        if not self.current_serial:
            return

        success, output = ADBService.exec_shell(self.current_serial, f"ls -F {parent_path}")
        if not success:
            return

        for line in output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            # 目录以/结尾
            if line.endswith('/'):
                dir_name = line[:-1]
                dir_path = os.path.join(parent_path, dir_name).replace('\\', '/')
                dir_item = QtWidgets.QTreeWidgetItem(parent_item, [dir_name])
                dir_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, dir_path)
                dir_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)

    def _parse_ls_output(self, output):
        """解析ls -l输出"""
        files = []
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('total'):
                continue

            parts = line.split(None, 8)
            if len(parts) < 9:
                continue

            perms, _, _, _, size, month, day, time, name = parts

            # 跳过目录链接
            if name.endswith('/'):
                continue

            # 解析时间
            mtime = f"{month} {day} {time}"

            # 判断类型
            if perms.startswith('d'):
                ftype = "文件夹"
            elif perms.startswith('l'):
                ftype = "链接"
            else:
                ext = os.path.splitext(name)[1].lower()
                type_map = {
                    '.log': '日志',
                    '.txt': '文本',
                    '.sh': '脚本',
                    '.bin': '固件',
                    '.img': '镜像',
                    '.tar': '压缩包',
                    '.gz': '压缩包',
                    '.xml': 'XML',
                    '.json': 'JSON',
                }
                ftype = type_map.get(ext, "文件")

            files.append({
                "name": name,
                "size": int(size) if size.isdigit() else 0,
                "mtime": mtime,
                "type": ftype
            })

        return files

    def _load_files(self, dir_path):
        """加载指定目录下的文件"""
        self.table_file.setRowCount(0)
        self.text_preview.clear()

        if not self.current_serial:
            return

        success, output = ADBService.exec_shell(self.current_serial, f"ls -l {dir_path}")
        if not success:
            return

        files = self._parse_ls_output(output)

        for row, file_info in enumerate(files):
            self.table_file.insertRow(row)
            self.table_file.setItem(row, 0, QtWidgets.QTableWidgetItem(file_info["name"]))
            self.table_file.setItem(row, 1, QtWidgets.QTableWidgetItem(file_info["type"]))
            self.table_file.setItem(row, 2, QtWidgets.QTableWidgetItem(format_file_size(file_info["size"])))
            self.table_file.setItem(row, 3, QtWidgets.QTableWidgetItem(file_info["mtime"]))
            self.table_file.item(row, 0).setData(QtCore.Qt.ItemDataRole.UserRole,
                                               os.path.join(dir_path, file_info["name"]).replace('\\', '/'))

    def preview_file(self, item):
        """预览文件内容"""
        if not self.current_serial:
            return

        file_path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        success, content = ADBService.exec_shell(self.current_serial, f"cat {file_path}")

        if success:
            self.text_preview.setPlainText(content)
        else:
            self.text_preview.setPlainText(f"无法读取文件: {content}")

    def download_file(self):
        """下载选中文件到本地"""
        current_row = self.table_file.currentRow()
        if current_row < 0 or not self.current_serial:
            return

        file_name = self.table_file.item(current_row, 0).text()
        remote_path = self.table_file.item(current_row, 0).data(QtCore.Qt.ItemDataRole.UserRole)

        local_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存文件", file_name, "所有文件 (*.*)"
        )

        if local_path:
            success, output = ADBService.adb_pull_file(self.current_serial, remote_path, local_path)
            if success:
                log.info(f"文件下载成功: {remote_path} -> {local_path}")
                QtWidgets.QMessageBox.information(self, "成功", "文件下载完成")
            else:
                log.error(f"文件下载失败: {output}")
                QtWidgets.QMessageBox.critical(self, "失败", f"下载失败: {output}")

    def upload_file(self):
        """上传文件到设备当前目录"""
        if not self.current_serial:
            return

        local_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择要上传的文件", "", "所有文件 (*.*)"
        )

        if local_path:
            file_name = os.path.basename(local_path)
            remote_path = os.path.join(self.current_path, file_name).replace('\\', '/')

            success, output = ADBService._run_adb_command(
                f"adb -s {self.current_serial} push \"{local_path}\" \"{remote_path}\""
            )

            if success:
                log.info(f"文件上传成功: {local_path} -> {remote_path}")
                self._load_files(self.current_path)
                QtWidgets.QMessageBox.information(self, "成功", "文件上传完成")
            else:
                log.error(f"文件上传失败: {output}")
                QtWidgets.QMessageBox.critical(self, "失败", f"上传失败: {output}")
