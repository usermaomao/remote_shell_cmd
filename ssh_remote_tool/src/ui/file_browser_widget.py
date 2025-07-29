import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLineEdit, QLabel, QSplitter, QFileSystemModel, QHeaderView,
    QMenu, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QDir, Qt, QModelIndex
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel, QStandardItem
from ..core.file_manager import FileManager

class RemoteFileModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'Modified'])

    def populate(self, files):
        self.removeRows(0, self.rowCount())
        for f in files:
            name_item = QStandardItem(f['name'])
            name_item.setData(f, Qt.ItemDataRole.UserRole)
            name_item.setEditable(False)

            size_item = QStandardItem(str(f['size']))
            size_item.setEditable(False)

            type_item = QStandardItem("Directory" if f['is_dir'] else "File")
            type_item.setEditable(False)

            mtime = datetime.datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            modified_item = QStandardItem(mtime)
            modified_item.setEditable(False)

            self.appendRow([name_item, size_item, type_item, modified_item])

class FileBrowserWidget(QWidget):
    def __init__(self, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.current_connection = None

        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Local file browser
        self.local_widget = self._create_local_browser()

        # Remote file browser
        self.remote_widget = self._create_remote_browser()

        self.splitter.addWidget(self.local_widget)
        self.splitter.addWidget(self.remote_widget)
        self.layout.addWidget(self.splitter)

    def _create_local_browser(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.local_path_edit = QLineEdit()
        self.local_tree = QTreeView()
        self.local_model = QFileSystemModel()
        self.local_model.setRootPath(QDir.rootPath())
        self.local_tree.setModel(self.local_model)
        self.local_tree.setRootIndex(self.local_model.index(QDir.homePath()))
        self.local_path_edit.setText(QDir.homePath())
        self.local_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Local System"))
        layout.addWidget(self.local_path_edit)
        layout.addWidget(self.local_tree)

        self.local_path_edit.returnPressed.connect(self.navigate_local_path)
        self.local_tree.doubleClicked.connect(self.local_item_double_clicked)
        return widget

    def _create_remote_browser(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.remote_path_edit = QLineEdit("/")
        self.remote_tree = QTreeView()
        self.remote_model = RemoteFileModel()
        self.remote_tree.setModel(self.remote_model)
        self.remote_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Remote System"))
        layout.addWidget(self.remote_path_edit)
        layout.addWidget(self.remote_tree)

        self.remote_path_edit.returnPressed.connect(self.load_remote_directory)
        self.remote_tree.doubleClicked.connect(self.remote_item_double_clicked)
        return widget

    def set_connection(self, connection_name):
        self.current_connection = connection_name
        self.load_remote_directory()

    def navigate_local_path(self):
        path = self.local_path_edit.text()
        if os.path.isdir(path):
            self.local_tree.setRootIndex(self.local_model.index(path))

    def local_item_double_clicked(self, index):
        if self.local_model.isDir(index):
            self.navigate_local_path()

    def remote_item_double_clicked(self, index):
        item_data = self.remote_model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
        if item_data and item_data['is_dir']:
            new_path = os.path.join(self.remote_path_edit.text(), item_data['name'])
            self.remote_path_edit.setText(new_path)
            self.load_remote_directory()

    def load_remote_directory(self):
        if not self.current_connection:
            return

        remote_path = self.remote_path_edit.text()
        if not remote_path.startswith('/'):
            remote_path = '/' + remote_path

        try:
            files = self.file_manager.list_directory(self.current_connection, remote_path)
            self.remote_model.populate(files)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list remote directory: {e}")
            # Navigate back to root on error
            self.remote_path_edit.setText("/")
            if self.remote_path_edit.text() != remote_path:
                self.load_remote_directory()
