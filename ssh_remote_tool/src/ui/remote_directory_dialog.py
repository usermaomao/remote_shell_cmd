import posixpath
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLineEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from core.file_manager import FileManager


class RemoteDirectoryDialog(QDialog):
    def __init__(self, file_manager: FileManager, connection_name: str, 
                 initial_path="/", parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.connection_name = connection_name
        self.current_path = self.normalize_remote_path(initial_path)
        self.selected_directory = None
        
        self.setWindowTitle("Select Remote Directory")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.load_directory()

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
        result = posixpath.join(base_path, *parts)
        result = posixpath.normpath(result)
        return self.normalize_remote_path(result)

    def get_parent_path(self, path):
        """Get parent directory of given path"""
        path = self.normalize_remote_path(path)
        if path == "/":
            return "/"
        return posixpath.dirname(path)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Path display and navigation
        path_layout = QHBoxLayout()
        self.path_label = QLabel("Current Path:")
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        
        self.back_btn = QPushButton("Back")
        self.home_btn = QPushButton("Home")
        self.refresh_btn = QPushButton("Refresh")
        
        self.back_btn.clicked.connect(self.go_back)
        self.home_btn.clicked.connect(self.go_home)
        self.refresh_btn.clicked.connect(self.load_directory)
        
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.back_btn)
        path_layout.addWidget(self.home_btn)
        path_layout.addWidget(self.refresh_btn)
        layout.addLayout(path_layout)
        
        # Directory tree view (only show directories)
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Directory Name'])
        self.tree_view.setModel(self.model)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree_view.doubleClicked.connect(self.item_double_clicked)
        self.tree_view.clicked.connect(self.item_clicked)
        layout.addWidget(self.tree_view)
        
        # Selected directory display
        selected_layout = QHBoxLayout()
        self.selected_label = QLabel("Selected Directory:")
        self.selected_edit = QLineEdit()
        self.selected_edit.setReadOnly(True)
        selected_layout.addWidget(self.selected_label)
        selected_layout.addWidget(self.selected_edit)
        layout.addLayout(selected_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        self.select_current_btn = QPushButton("Select Current")
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        
        self.select_current_btn.clicked.connect(self.select_current_directory)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.setEnabled(False)  # Initially disabled
        
        button_layout.addWidget(self.select_current_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Select current directory by default
        self.select_current_directory()

    def load_directory(self):
        """Load and display directory contents (directories only)"""
        try:
            files = self.file_manager.list_directory(self.connection_name, self.current_path)
            
            # Filter to show only directories
            directories = [f for f in files if f['is_dir']]
            
            # Add ".." entry for parent directory if not at root
            if self.current_path != "/":
                parent_entry = {
                    "name": "..",
                    "size": 0,
                    "mtime": 0,
                    "permissions": "drwxr-xr-x",
                    "is_dir": True,
                }
                directories.insert(0, parent_entry)
            
            self.populate_model(directories)
            self.path_edit.setText(self.current_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load directory '{self.current_path}':\n{str(e)}")
            
            # Try to navigate to parent directory on error
            if self.current_path != "/":
                parent_path = self.get_parent_path(self.current_path)
                self.current_path = parent_path
                self.load_directory()

    def populate_model(self, directories):
        """Populate the tree model with directory data"""
        self.model.removeRows(0, self.model.rowCount())
        
        for dir_data in directories:
            name_item = QStandardItem(dir_data['name'])
            name_item.setData(dir_data, Qt.ItemDataRole.UserRole)
            name_item.setEditable(False)
            
            self.model.appendRow([name_item])

    def item_clicked(self, index):
        """Handle single-click on items"""
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        dir_data = item.data(Qt.ItemDataRole.UserRole)
        if not dir_data:
            return
            
        if dir_data['name'] != "..":
            # Select this directory
            selected_path = self.join_remote_path(self.current_path, dir_data['name'])
            self.selected_directory = selected_path
            self.selected_edit.setText(selected_path)
            self.ok_btn.setEnabled(True)

    def item_double_clicked(self, index):
        """Handle double-click on items"""
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        dir_data = item.data(Qt.ItemDataRole.UserRole)
        if not dir_data:
            return
            
        # Navigate to directory
        if dir_data['name'] == "..":
            self.go_back()
        else:
            new_path = self.join_remote_path(self.current_path, dir_data['name'])
            self.current_path = new_path
            self.load_directory()

    def select_current_directory(self):
        """Select the current directory"""
        self.selected_directory = self.current_path
        self.selected_edit.setText(self.current_path)
        self.ok_btn.setEnabled(True)

    def go_back(self):
        """Navigate to parent directory"""
        parent_path = self.get_parent_path(self.current_path)
        self.current_path = parent_path
        self.load_directory()

    def go_home(self):
        """Navigate to root directory"""
        self.current_path = "/"
        self.load_directory()

    def navigate_to_path(self):
        """Navigate to the path entered in the path edit field"""
        requested_path = self.path_edit.text()
        normalized_path = self.normalize_remote_path(requested_path)
        self.current_path = normalized_path
        self.load_directory()

    def get_selected_directory(self):
        """Get the selected directory path"""
        return self.selected_directory

    @staticmethod
    def get_remote_directory(file_manager: FileManager, connection_name: str, 
                           initial_path="/", parent=None):
        """Static method to show dialog and get selected directory"""
        dialog = RemoteDirectoryDialog(file_manager, connection_name, initial_path, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_selected_directory()
        return None
