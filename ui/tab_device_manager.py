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

        self.btn_download_logs = QtWidgets.QPushButton(self)
        self.btn_download_logs.setGeometry(QtCore.QRect(195, 15, 110, 30))
        self.btn_download_logs.setText("下载设备日志")

        self.btn_upload = QtWidgets.QPushButton(self)
        self.btn_upload.setGeometry(QtCore.QRect(315, 15, 80, 30))
        self.btn_upload.setText("上传文件")

        self.tree_dir = QtWidgets.QTreeWidget(self)
        self.tree_dir.setGeometry(QtCore.QRect(15, 55, 300, 520))
        self.tree_dir.setHeaderLabel("设备目录")
        self.tree_dir.setItemsExpandable(True)
        self.tree_dir.setExpandsOnDoubleClick(True)

        self.table_file = QtWidgets.QTableWidget(self)
        self.table_file.setGeometry(QtCore.QRect(330, 55, 635, 520))
        self.table_file.setColumnCount(2)
        self.table_file.setHorizontalHeaderLabels(["文件名", "类型"])
        self.table_file.setColumnWidth(0, 480)
        self.table_file.setColumnWidth(1, 155)
        self.table_file.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_file.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_file.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table_file.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        # 修复DPI缩放时重绘残留问题
        self.table_file.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.table_file.viewport().setAttribute(QtCore.Qt.WidgetAttribute.WA_PaintOnScreen, True)

        self._update_ui_state(False)

    def _connect_signals(self):
        """连接信号"""
        self.btn_refresh.clicked.connect(self.refresh_file_list)
        self.btn_download.clicked.connect(self.download_file)
        self.btn_download_logs.clicked.connect(self.download_device_logs)
        self.btn_upload.clicked.connect(self.upload_file)
        self.tree_dir.itemClicked.connect(self.on_dir_selected)
        self.tree_dir.itemExpanded.connect(self.on_dir_expanded)
        self.table_file.itemDoubleClicked.connect(self.preview_file)

    def _update_ui_state(self, connected):
        """更新UI状态"""
        self.btn_refresh.setEnabled(connected)
        self.btn_download.setEnabled(connected)
        self.btn_download_logs.setEnabled(connected)
        self.btn_upload.setEnabled(connected)
        self.tree_dir.setEnabled(connected)
        self.table_file.setEnabled(connected)

        if not connected:
            self.tree_dir.clear()
            self.table_file.setRowCount(0)

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

        success, output = ADBService.exec_shell(self.current_serial, f"ls -F -1 {parent_path}")
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
        """解析ls -l输出 - 兼容BusyBox嵌入式系统"""
        files = []
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('total'):
                continue

            parts = line.split()
            if len(parts) < 6:
                continue

            # 适配两种ls输出格式:
            # GNU ls: perms links owner group size month day time name
            # BusyBox ls: perms size month day time name
            if parts[1].isdigit() and len(parts) >= 6:
                # BusyBox格式
                perms = parts[0]
                size = parts[1]
                month = parts[2]
                day = parts[3]
                time = parts[4]
                name = ' '.join(parts[5:])
            else:
                # 标准格式
                perms = parts[0]
                size = parts[4]
                month = parts[5]
                day = parts[6]
                time = parts[7]
                name = ' '.join(parts[8:])

            # 解析时间
            mtime = f"{month} {day} {time}"

            # 跳过目录，仅显示文件和链接
            if perms.startswith('d'):
                continue

            # 判断文件类型
            if perms.startswith('l'):
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
                "type": ftype,
                "is_dir": False
            })

        return files

    def _load_files(self, dir_path):
        """加载指定目录下的文件"""
        self.table_file.setRowCount(0)

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
            # 正确拼接路径，处理根目录特殊情况
            if dir_path == "/":
                full_path = "/" + file_info["name"]
            else:
                full_path = dir_path.rstrip('/') + "/" + file_info["name"]
            self.table_file.item(row, 0).setData(256, full_path)
            


    def preview_file(self, item):
        """预览文件内容 - 弹出独立窗口"""
        if not self.current_serial:
            return

        file_path = item.data(256)
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # 仅允许指定类型文件预览
        allowed_exts = ['.sh', '.txt', '.bin',".conf"]
        if ext not in allowed_exts:
            QtWidgets.QMessageBox.information(self, "提示", "该文件类型不支持预览")
            return
        
        success, content = ADBService.exec_shell(self.current_serial, f"cat {file_path}")

        # 创建预览对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"文件预览: {filename}")
        dialog.setFixedSize(800, 600)
        layout = QtWidgets.QVBoxLayout(dialog)

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)

        if success:
            text_edit.setPlainText(content)
        else:
            text_edit.setPlainText(f"无法读取文件: {content}")

        layout.addWidget(text_edit)

        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        dialog.exec()

    def download_file(self):
        """下载选中文件到本地"""
        current_row = self.table_file.currentRow()
        if current_row < 0 or not self.current_serial:
            return



        file_name = self.table_file.item(current_row, 0).text()
        remote_path = self.table_file.item(current_row, 0).data(256)

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

    def download_device_logs(self):
        """下载设备日志文件夹"""
        from commons import get_current_time_str
        import tempfile
        
        if not self.current_serial:
            QtWidgets.QMessageBox.warning(self, "提示", "请先连接设备")
            return
        
        log.info(f"开始下载设备[{self.current_serial}]日志")

        # 1. 创建本地临时目录用于存放日志文件
        temp_dir = tempfile.mkdtemp(prefix="device_logs_")
        log_dir = os.path.join(temp_dir, "")

        try:
            # 2. 使用adb pull直接拉取整个日志文件夹
            log.info(f"正在从设备拉取日志文件夹到: {log_dir}")
            
            # 创建目标目录
            os.makedirs(log_dir, exist_ok=True)
            
            # 使用adb pull命令拉取整个文件夹
            pull_success, pull_output = ADBService._run_adb_command(
                f"adb -s {self.current_serial} pull /userdata/logs/ {log_dir}"
            )
            
            if not pull_success:
                log.error(f"拉取日志文件夹失败: {pull_output}")
                QtWidgets.QMessageBox.critical(self, "下载失败", f"拉取日志文件夹失败: {pull_output}")
                return
            
            # 检查是否成功拉取到文件
            if not os.path.exists(log_dir) or len(os.listdir(log_dir)) == 0:
                log.error("未找到日志文件或文件夹为空")
                QtWidgets.QMessageBox.critical(self, "下载失败", "未找到日志文件或文件夹为空")
                return
            
            # 3. 在本地创建压缩文件
            zip_filename = f"device_logs_{self.current_serial}_{get_current_time_str()}.tar.gz"
            local_temp_zip = os.path.join(tempfile.gettempdir(), zip_filename)
            
            log.info(f"正在本地压缩日志文件: {local_temp_zip}")
            
            # 使用tar命令或Python的tarfile模块进行压缩
            try:
                import tarfile
                
                # 使用tarfile模块创建压缩包
                with tarfile.open(local_temp_zip, "w:gz") as tar:
                    tar.add(log_dir, arcname=os.path.basename(log_dir))
                
                log.info(f"日志压缩完成: {local_temp_zip}, 大小: {os.path.getsize(local_temp_zip)} 字节")
                
            except Exception as e:
                log.error(f"本地压缩失败: {str(e)}")
                # 备用方案：使用系统tar命令
                try:
                    import subprocess
                    subprocess.run(
                        ["tar", "-czf", local_temp_zip, "-C", temp_dir, "logs"],
                        check=True
                    )
                except Exception as e2:
                    log.error(f"备用压缩方案也失败: {str(e2)}")
                    QtWidgets.QMessageBox.critical(
                        self, "压缩失败", 
                        f"日志压缩失败:\n{str(e)}\n{str(e2)}"
                    )
                    return
            
            # 4. 让用户选择保存路径
            dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "保存设备日志",
                zip_filename,
                "压缩包 (*.tar.gz)"
            )
            
            if dest_path:
                try:
                    import shutil
                    shutil.copy2(local_temp_zip, dest_path)
                    log.info(f"设备日志下载成功: {dest_path}")
                    QtWidgets.QMessageBox.information(
                        self, "成功", 
                        f"设备日志下载完成\n保存位置: {dest_path}\n大小: {os.path.getsize(dest_path) / 1024 / 1024:.2f} MB"
                    )
                except Exception as e:
                    log.error(f"保存日志失败: {str(e)}")
                    QtWidgets.QMessageBox.critical(self, "下载失败", f"保存日志失败: {str(e)}")
                finally:
                    # 清理本地临时文件
                    if os.path.exists(local_temp_zip):
                        os.remove(local_temp_zip)
            
        finally:
            # 清理临时目录
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    log.info(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                log.warning(f"清理临时目录失败: {str(e)}")
