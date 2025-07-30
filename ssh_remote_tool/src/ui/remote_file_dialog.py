import posixpath
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
    QLineEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from core.file_manager import FileManager


class RemoteFileDialog(QDialog):
    def __init__(self, file_manager: FileManager, connection_name: str, 
                 initial_path="/", file_filter=None, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.connection_name = connection_name
        self.current_path = self.normalize_remote_path(initial_path)
        self.file_filter = file_filter or []  # List of extensions like ['.sh', '.py']
        self.selected_file = None
        
        self.setWindowTitle("Select Remote File")
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
        
        # File tree view
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Type', 'Size'])
        self.tree_view.setModel(self.model)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree_view.doubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.tree_view)
        
        # Selected file display
        selected_layout = QHBoxLayout()
        self.selected_label = QLabel("Selected File:")
        self.selected_edit = QLineEdit()
        self.selected_edit.setReadOnly(True)
        selected_layout.addWidget(self.selected_label)
        selected_layout.addWidget(self.selected_edit)
        layout.addLayout(selected_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.setEnabled(False)  # Initially disabled
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def load_directory(self):
        """Load and display directory contents"""
        try:
            files = self.file_manager.list_directory(self.connection_name, self.current_path)
            
            # Add ".." entry for parent directory if not at root
            if self.current_path != "/":
                parent_entry = {
                    "name": "..",
                    "size": 0,
                    "mtime": 0,
                    "permissions": "drwxr-xr-x",
                    "is_dir": True,
                }
                files.insert(0, parent_entry)
            
            self.populate_model(files)
            self.path_edit.setText(self.current_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load directory '{self.current_path}':\n{str(e)}")
            
            # Try to navigate to parent directory on error
            if self.current_path != "/":
                parent_path = self.get_parent_path(self.current_path)
                self.current_path = parent_path
                self.load_directory()

    def populate_model(self, files):
        """Populate the tree model with file data"""
        self.model.removeRows(0, self.model.rowCount())
        
        for file_data in files:
            name_item = QStandardItem(file_data['name'])
            name_item.setData(file_data, Qt.ItemDataRole.UserRole)
            name_item.setEditable(False)
            
            type_item = QStandardItem("Directory" if file_data['is_dir'] else "File")
            type_item.setEditable(False)
            
            size_item = QStandardItem(str(file_data['size']) if not file_data['is_dir'] else "")
            size_item.setEditable(False)
            
            # Apply file filter
            if not file_data['is_dir'] and self.file_filter:
                file_ext = posixpath.splitext(file_data['name'])[1].lower()
                if file_ext not in self.file_filter:
                    name_item.setEnabled(False)
                    type_item.setEnabled(False)
                    size_item.setEnabled(False)
            
            self.model.appendRow([name_item, type_item, size_item])

    def item_double_clicked(self, index):
        """Handle double-click on items"""
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        file_data = item.data(Qt.ItemDataRole.UserRole)
        if not file_data:
            return
            
        if file_data['is_dir']:
            # Navigate to directory
            if file_data['name'] == "..":
                self.go_back()
            else:
                new_path = self.join_remote_path(self.current_path, file_data['name'])
                self.current_path = new_path
                self.load_directory()
        else:
            # Select file
            if self.is_file_selectable(file_data['name']):
                self.select_file(file_data['name'])

    def is_file_selectable(self, filename):
        """Check if file can be selected based on filter"""
        if not self.file_filter:
            return True
        file_ext = posixpath.splitext(filename)[1].lower()
        return file_ext in self.file_filter

    def select_file(self, filename):
        """Select a file"""
        if self.is_file_selectable(filename):
            self.selected_file = self.join_remote_path(self.current_path, filename)
            self.selected_edit.setText(self.selected_file)
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

    def get_selected_file(self):
        """Get the selected file path"""
        return self.selected_file

    @staticmethod
    def get_remote_file(file_manager: FileManager, connection_name: str, 
                       initial_path="/", file_filter=None, parent=None):
        """Static method to show dialog and get selected file"""
        dialog = RemoteFileDialog(file_manager, connection_name, initial_path, file_filter, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_selected_file()
        return None
