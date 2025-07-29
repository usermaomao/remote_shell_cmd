import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLineEdit, QLabel, QSplitter, QHeaderView,
    QMenu, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QDir, Qt, QModelIndex
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel, QStandardItem, QFileSystemModel
from core.file_manager import FileManager

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

        # Add toolbar
        self.create_toolbar()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Local file browser
        self.local_widget = self._create_local_browser()

        # Remote file browser
        self.remote_widget = self._create_remote_browser()

        self.splitter.addWidget(self.local_widget)
        self.splitter.addWidget(self.remote_widget)
        self.layout.addWidget(self.splitter)

    def create_toolbar(self):
        """Create toolbar with file operation buttons"""
        toolbar_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.upload_btn = QPushButton("Upload")
        self.download_btn = QPushButton("Download")
        self.new_folder_btn = QPushButton("New Folder")

        self.refresh_btn.clicked.connect(self.refresh_views)
        self.upload_btn.clicked.connect(self.upload_selected_file)
        self.download_btn.clicked.connect(self.download_selected_file)
        self.new_folder_btn.clicked.connect(self.create_new_folder)

        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.download_btn)
        toolbar_layout.addWidget(self.new_folder_btn)
        toolbar_layout.addStretch()

        self.layout.addLayout(toolbar_layout)

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

        # Add context menu for local files
        self.local_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_tree.customContextMenuRequested.connect(self.show_local_context_menu)

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

        # Add context menu for remote files
        self.remote_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_tree.customContextMenuRequested.connect(self.show_remote_context_menu)

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

    def show_remote_context_menu(self, pos):
        """Show context menu for remote files"""
        index = self.remote_tree.indexAt(pos)
        if not index.isValid():
            return

        item = self.remote_model.itemFromIndex(index)
        if not item:
            return

        file_data = item.data(Qt.ItemDataRole.UserRole)
        if not file_data:
            return

        context_menu = QMenu(self)

        if file_data['is_dir']:
            # Directory actions
            enter_action = context_menu.addAction("Enter Directory")
            enter_action.triggered.connect(lambda: self.enter_directory(file_data['name']))
        else:
            # File actions
            download_action = context_menu.addAction("Download")
            download_action.triggered.connect(lambda: self.download_file(file_data['name']))

            edit_action = context_menu.addAction("Edit")
            edit_action.triggered.connect(lambda: self.edit_file(file_data['name']))

        context_menu.addSeparator()
        delete_action = context_menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_item(file_data['name'], file_data['is_dir']))

        rename_action = context_menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self.rename_item(file_data['name']))

        context_menu.exec(self.remote_tree.mapToGlobal(pos))

    def enter_directory(self, dir_name):
        """Enter a directory"""
        current_path = self.remote_path_edit.text()
        new_path = os.path.join(current_path, dir_name).replace('\\', '/')
        self.remote_path_edit.setText(new_path)
        self.load_remote_directory()

    def download_file(self, filename):
        """Download a file from remote to local"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        remote_path = os.path.join(self.remote_path_edit.text(), filename).replace('\\', '/')

        # Get local save path
        local_path, _ = QInputDialog.getText(
            self, "Download File",
            f"Save '{filename}' to local path:",
            text=os.path.join(self.local_path_edit.text(), filename)
        )

        if local_path:
            try:
                self.file_manager.download_file(self.current_connection, remote_path, local_path)
                QMessageBox.information(self, "Success", f"Downloaded '{filename}' successfully.")
                # Refresh local view
                self.navigate_local_path()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download file: {e}")

    def edit_file(self, filename):
        """Edit a remote file"""
        QMessageBox.information(self, "Info", f"Edit functionality for '{filename}' will be implemented.")

    def delete_item(self, name, is_dir):
        """Delete a file or directory"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        item_type = "directory" if is_dir else "file"
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the {item_type} '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                remote_path = os.path.join(self.remote_path_edit.text(), name).replace('\\', '/')
                if is_dir:
                    self.file_manager.delete_directory(self.current_connection, remote_path)
                else:
                    self.file_manager.delete_file(self.current_connection, remote_path)
                QMessageBox.information(self, "Success", f"Deleted '{name}' successfully.")
                self.load_remote_directory()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete {item_type}: {e}")

    def rename_item(self, old_name):
        """Rename a file or directory"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        new_name, ok = QInputDialog.getText(
            self, "Rename", f"Enter new name for '{old_name}':", text=old_name
        )

        if ok and new_name and new_name != old_name:
            try:
                old_path = os.path.join(self.remote_path_edit.text(), old_name).replace('\\', '/')
                new_path = os.path.join(self.remote_path_edit.text(), new_name).replace('\\', '/')
                self.file_manager.rename_file(self.current_connection, old_path, new_path)
                QMessageBox.information(self, "Success", f"Renamed '{old_name}' to '{new_name}' successfully.")
                self.load_remote_directory()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename: {e}")

    def show_local_context_menu(self, pos):
        """Show context menu for local files"""
        index = self.local_tree.indexAt(pos)
        if not index.isValid():
            return

        file_path = self.local_model.filePath(index)
        file_name = self.local_model.fileName(index)
        is_dir = self.local_model.isDir(index)

        context_menu = QMenu(self)

        if not is_dir and self.current_connection:
            upload_action = context_menu.addAction("Upload to Remote")
            upload_action.triggered.connect(lambda: self.upload_file(file_path, file_name))

        context_menu.exec(self.local_tree.mapToGlobal(pos))

    def upload_file(self, local_path, filename):
        """Upload a file from local to remote"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        # Get remote save path
        remote_path, ok = QInputDialog.getText(
            self, "Upload File",
            f"Upload '{filename}' to remote path:",
            text=os.path.join(self.remote_path_edit.text(), filename).replace('\\', '/')
        )

        if ok and remote_path:
            try:
                self.file_manager.upload_file(self.current_connection, local_path, remote_path)
                QMessageBox.information(self, "Success", f"Uploaded '{filename}' successfully.")
                # Refresh remote view
                self.load_remote_directory()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload file: {e}")

    def refresh_views(self):
        """Refresh both local and remote views"""
        self.navigate_local_path()
        self.load_remote_directory()

    def upload_selected_file(self):
        """Upload currently selected local file"""
        selected_indexes = self.local_tree.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "Please select a file to upload.")
            return

        index = selected_indexes[0]
        if self.local_model.isDir(index):
            QMessageBox.warning(self, "Warning", "Directory upload not yet supported.")
            return

        file_path = self.local_model.filePath(index)
        file_name = self.local_model.fileName(index)
        self.upload_file(file_path, file_name)

    def download_selected_file(self):
        """Download currently selected remote file"""
        selected_indexes = self.remote_tree.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "Please select a file to download.")
            return

        index = selected_indexes[0]
        item = self.remote_model.itemFromIndex(index)
        if not item:
            return

        file_data = item.data(Qt.ItemDataRole.UserRole)
        if not file_data:
            return

        if file_data['is_dir']:
            QMessageBox.warning(self, "Warning", "Directory download not yet supported.")
            return

        self.download_file(file_data['name'])

    def create_new_folder(self):
        """Create a new folder in remote directory"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Enter folder name:"
        )

        if ok and folder_name:
            try:
                remote_path = os.path.join(self.remote_path_edit.text(), folder_name).replace('\\', '/')
                self.file_manager.create_directory(self.current_connection, remote_path)
                QMessageBox.information(self, "Success", f"Created folder '{folder_name}' successfully.")
                self.load_remote_directory()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")
