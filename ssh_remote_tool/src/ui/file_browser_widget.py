import os
import datetime
import posixpath
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLineEdit, QLabel, QSplitter, QHeaderView,
    QMenu, QMessageBox, QInputDialog, QProgressBar
)
from PyQt6.QtCore import QDir, Qt, QModelIndex, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel, QStandardItem, QFileSystemModel
from core.file_manager import FileManager

class DirectoryLoadWorker(QThread):
    """Worker thread for loading directory contents asynchronously"""
    files_loaded = pyqtSignal(list)  # Signal emitted when files are loaded
    error_occurred = pyqtSignal(str)  # Signal emitted when error occurs

    def __init__(self, file_manager, connection_name, remote_path):
        super().__init__()
        self.file_manager = file_manager
        self.connection_name = connection_name
        self.remote_path = remote_path

    def run(self):
        """Load directory contents in background thread"""
        try:
            files = self.file_manager.list_directory(self.connection_name, self.remote_path)
            self.files_loaded.emit(files)
        except Exception as e:
            self.error_occurred.emit(str(e))

class RemoteFileModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'Modified'])

    def populate(self, files):
        """Populate model with files - optimized for large directories"""
        # Clear existing items efficiently
        self.clear()
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'Modified'])

        # Batch insert for better performance
        items = []
        for f in files:
            name_item = QStandardItem(f['name'])
            name_item.setData(f, Qt.ItemDataRole.UserRole)
            name_item.setEditable(False)

            # Format size more efficiently
            size_str = str(f['size']) if not f['is_dir'] else ""
            size_item = QStandardItem(size_str)
            size_item.setEditable(False)

            type_item = QStandardItem("Directory" if f['is_dir'] else "File")
            type_item.setEditable(False)

            # Format timestamp more efficiently
            try:
                mtime = datetime.datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OSError):
                mtime = "Unknown"
            modified_item = QStandardItem(mtime)
            modified_item.setEditable(False)

            items.append([name_item, size_item, type_item, modified_item])

        # Batch insert all items at once
        for item_row in items:
            self.appendRow(item_row)

class FileBrowserWidget(QWidget):
    def __init__(self, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.current_connection = None
        self.ssh_manager = None  # Store ssh_manager reference for accessing connection config
        self.remote_current_path = "/"  # Track current remote path
        self.load_worker = None  # Background loading worker
        self.is_loading = False  # Loading state flag

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
        self.back_btn = QPushButton("Back")
        self.home_btn = QPushButton("Home")

        self.refresh_btn.clicked.connect(self.refresh_views)
        self.upload_btn.clicked.connect(self.upload_selected_file)
        self.download_btn.clicked.connect(self.download_selected_file)
        self.new_folder_btn.clicked.connect(self.create_new_folder)
        self.back_btn.clicked.connect(self.go_back)
        self.home_btn.clicked.connect(self.go_home)

        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addWidget(self.home_btn)
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

        # Add progress bar for loading indication
        self.remote_progress = QProgressBar()
        self.remote_progress.setVisible(False)
        self.remote_progress.setRange(0, 0)  # Indeterminate progress

        self.remote_tree = QTreeView()
        self.remote_model = RemoteFileModel()
        self.remote_tree.setModel(self.remote_model)
        self.remote_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(QLabel("Remote System"))
        layout.addWidget(self.remote_path_edit)
        layout.addWidget(self.remote_progress)
        layout.addWidget(self.remote_tree)

        self.remote_path_edit.returnPressed.connect(self.navigate_to_path)
        self.remote_tree.doubleClicked.connect(self.remote_item_double_clicked)

        # Add context menu for remote files
        self.remote_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_tree.customContextMenuRequested.connect(self.show_remote_context_menu)

        return widget

    def normalize_remote_path(self, path):
        """Normalize remote path to use forward slashes and handle edge cases"""
        if not path:
            return "/"

        # Convert to forward slashes
        path = path.replace('\\', '/')

        # Ensure it starts with /
        if not path.startswith('/'):
            path = '/' + path

        # Remove double slashes
        while '//' in path:
            path = path.replace('//', '/')

        # Remove trailing slash unless it's root
        if len(path) > 1 and path.endswith('/'):
            path = path.rstrip('/')

        return path

    def join_remote_path(self, base_path, *parts):
        """Join remote path parts using posixpath for consistent forward slashes"""
        # Use posixpath.join for Unix-style paths
        result = posixpath.join(base_path, *parts)
        # Normalize and resolve any ".." components
        result = posixpath.normpath(result)
        return self.normalize_remote_path(result)

    def get_parent_path(self, path):
        """Get parent directory of given path"""
        path = self.normalize_remote_path(path)
        if path == "/":
            return "/"
        return posixpath.dirname(path)

    def go_back(self):
        """Navigate to parent directory"""
        if not self.current_connection:
            return

        parent_path = self.get_parent_path(self.remote_current_path)
        self.remote_current_path = parent_path
        self.remote_path_edit.setText(parent_path)
        self.load_remote_directory()

    def go_home(self):
        """Navigate to default directory configured for this connection"""
        if not self.current_connection:
            return

        # Get default directory from connection settings
        default_dir = "/"
        if self.ssh_manager and self.current_connection:
            conn_data = self.ssh_manager.get_connection(self.current_connection)
            if conn_data:
                default_dir = conn_data.get("default_dir", "/")

        # Navigate to the default directory
        self.remote_current_path = self.normalize_remote_path(default_dir)
        self.remote_path_edit.setText(self.remote_current_path)
        self.load_remote_directory()

    def navigate_to_path(self):
        """Navigate to the path entered in the path edit field"""
        if not self.current_connection:
            return

        requested_path = self.remote_path_edit.text()
        normalized_path = self.normalize_remote_path(requested_path)

        # Update current path and load directory
        self.remote_current_path = normalized_path
        self.load_remote_directory()

    def set_connection(self, connection_name, ssh_manager=None):
        self.current_connection = connection_name
        self.ssh_manager = ssh_manager  # Store ssh_manager reference

        # Get default directory from connection settings
        default_dir = "/"
        if ssh_manager and connection_name:
            conn_data = ssh_manager.get_connection(connection_name)
            if conn_data:
                default_dir = conn_data.get("default_dir", "/")

        self.remote_current_path = self.normalize_remote_path(default_dir)
        self.remote_path_edit.setText(self.remote_current_path)
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
            self.enter_directory(item_data['name'])

    def load_remote_directory(self):
        """Load remote directory asynchronously for better performance"""
        if not self.current_connection or self.is_loading:
            return

        # Get path from edit field and normalize it
        requested_path = self.remote_path_edit.text()
        normalized_path = self.normalize_remote_path(requested_path)

        # Start loading indication
        self.is_loading = True
        self.remote_progress.setVisible(True)
        self.refresh_btn.setEnabled(False)

        # Stop any existing worker
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.terminate()
            self.load_worker.wait()

        # Create and start background worker
        self.load_worker = DirectoryLoadWorker(
            self.file_manager,
            self.current_connection,
            normalized_path
        )
        self.load_worker.files_loaded.connect(self.on_files_loaded)
        self.load_worker.error_occurred.connect(self.on_load_error)
        self.load_worker.finished.connect(self.on_load_finished)
        self.load_worker.start()

    def on_files_loaded(self, files):
        """Handle successful file loading"""
        # Get current path from worker
        normalized_path = self.load_worker.remote_path

        # Add ".." entry for parent directory if not at root
        if normalized_path != "/":
            parent_entry = {
                "name": "..",
                "size": 0,
                "mtime": 0,
                "permissions": "drwxr-xr-x",
                "is_dir": True,
            }
            files.insert(0, parent_entry)

        self.remote_model.populate(files)
        self.remote_current_path = normalized_path
        self.remote_path_edit.setText(normalized_path)

    def on_load_error(self, error_msg):
        """Handle loading error"""
        normalized_path = self.load_worker.remote_path
        QMessageBox.critical(self, "Error", f"Failed to list remote directory '{normalized_path}':\n{error_msg}")

        # Try to navigate to parent directory on error
        if normalized_path != "/":
            parent_path = self.get_parent_path(normalized_path)
            self.remote_current_path = parent_path
            self.remote_path_edit.setText(parent_path)
            # Retry loading parent directory
            self.load_remote_directory()
        else:
            # If we can't even access root, there's a connection problem
            QMessageBox.warning(self, "Connection Error",
                              "Cannot access remote filesystem. Please check your connection.")
            self.remote_model.populate([])

    def on_load_finished(self):
        """Handle loading completion"""
        self.is_loading = False
        self.remote_progress.setVisible(False)
        self.refresh_btn.setEnabled(True)

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
        if dir_name == "..":
            # Navigate to parent directory
            self.go_back()
        else:
            # Navigate to subdirectory
            new_path = self.join_remote_path(self.remote_current_path, dir_name)
            self.remote_current_path = new_path
            self.remote_path_edit.setText(new_path)
            self.load_remote_directory()

    def download_file(self, filename):
        """Download a file from remote to local"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        remote_path = self.join_remote_path(self.remote_current_path, filename)

        # Get local save path
        local_path, ok = QInputDialog.getText(
            self, "Download File",
            f"Save '{filename}' to local path:",
            text=os.path.join(self.local_path_edit.text(), filename)
        )

        if ok and local_path:
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

        # Don't allow deleting parent directory entry
        if name == "..":
            return

        item_type = "directory" if is_dir else "file"
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the {item_type} '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                remote_path = self.join_remote_path(self.remote_current_path, name)
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

        # Don't allow renaming parent directory entry
        if old_name == "..":
            return

        new_name, ok = QInputDialog.getText(
            self, "Rename", f"Enter new name for '{old_name}':", text=old_name
        )

        if ok and new_name and new_name != old_name:
            try:
                old_path = self.join_remote_path(self.remote_current_path, old_name)
                new_path = self.join_remote_path(self.remote_current_path, new_name)
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
        default_remote_path = self.join_remote_path(self.remote_current_path, filename)
        remote_path, ok = QInputDialog.getText(
            self, "Upload File",
            f"Upload '{filename}' to remote path:",
            text=default_remote_path
        )

        if ok and remote_path:
            try:
                # Normalize the remote path
                remote_path = self.normalize_remote_path(remote_path)
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
                remote_path = self.join_remote_path(self.remote_current_path, folder_name)
                self.file_manager.create_directory(self.current_connection, remote_path)
                QMessageBox.information(self, "Success", f"Created folder '{folder_name}' successfully.")
                self.load_remote_directory()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")
