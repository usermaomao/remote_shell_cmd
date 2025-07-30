from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QFileDialog,
    QListWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.ssh_manager import SSHManager

class ConnectionDialog(QDialog):
    def __init__(self, connection_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Settings")
        self.layout = QFormLayout(self)

        self.name = QLineEdit()
        self.host = QLineEdit()
        self.port = QLineEdit("22")
        self.user = QLineEdit()
        self.auth_method = QComboBox()
        self.auth_method.addItems(["password", "key"])
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_path = QLineEdit()
        self.key_browse_btn = QPushButton("Browse...")
        self.default_dir = QLineEdit("/")
        self.default_dir.setPlaceholderText("Default remote directory (e.g., /home/user)")

        self.layout.addRow("Connection Name:", self.name)
        self.layout.addRow("Host:", self.host)
        self.layout.addRow("Port:", self.port)
        self.layout.addRow("User:", self.user)
        self.layout.addRow("Default Directory:", self.default_dir)
        self.layout.addRow("Auth Method:", self.auth_method)
        self.layout.addRow("Password:", self.password)

        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_path)
        key_layout.addWidget(self.key_browse_btn)
        self.layout.addRow("SSH Key Path:", key_layout)

        self.buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.buttons.addWidget(self.ok_button)
        self.buttons.addWidget(self.cancel_button)
        self.layout.addRow(self.buttons)

        self.auth_method.currentTextChanged.connect(self.toggle_auth_fields)
        self.key_browse_btn.clicked.connect(self.browse_key)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if connection_data:
            self.name.setText(connection_data.get("name", ""))
            self.host.setText(connection_data.get("host", ""))
            self.port.setText(str(connection_data.get("port", "22")))
            self.user.setText(connection_data.get("user", ""))
            self.default_dir.setText(connection_data.get("default_dir", "/"))
            self.auth_method.setCurrentText(connection_data.get("auth_method", "password"))
            self.password.setText(connection_data.get("password", ""))
            self.key_path.setText(connection_data.get("key_path", ""))

        self.toggle_auth_fields(self.auth_method.currentText())

    def toggle_auth_fields(self, method):
        if method == "password":
            self.password.setVisible(True)
            self.key_path.setVisible(False)
            self.key_browse_btn.setVisible(False)
        else:
            self.password.setVisible(False)
            self.key_path.setVisible(True)
            self.key_browse_btn.setVisible(True)

    def browse_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select SSH Key")
        if path:
            self.key_path.setText(path)

    def get_data(self):
        return {
            "name": self.name.text(),
            "host": self.host.text(),
            "port": int(self.port.text()),
            "user": self.user.text(),
            "default_dir": self.default_dir.text() or "/",
            "auth_method": self.auth_method.currentText(),
            "password": self.password.text() if self.auth_method.currentText() == "password" else None,
            "key_path": self.key_path.text() if self.auth_method.currentText() == "key" else None,
        }

class ConnectionManagerWidget(QWidget):
    connection_selected = pyqtSignal(str)

    def __init__(self, ssh_manager: SSHManager, parent=None):
        super().__init__(parent)
        self.ssh_manager = ssh_manager
        self.layout = QVBoxLayout(self)

        self.connection_list = QListWidget()
        self.connection_list.itemDoubleClicked.connect(self.connect_to_selected)
        self.connection_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.connection_list.customContextMenuRequested.connect(self.show_context_menu)

        self.layout.addWidget(self.connection_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        self.layout.addLayout(button_layout)

        # Import/Export buttons
        import_export_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import...")
        self.export_btn = QPushButton("Export...")
        import_export_layout.addWidget(self.import_btn)
        import_export_layout.addWidget(self.export_btn)
        self.layout.addLayout(import_export_layout)

        self.add_btn.clicked.connect(self.add_connection)
        self.edit_btn.clicked.connect(self.edit_connection)
        self.delete_btn.clicked.connect(self.delete_connection)
        self.import_btn.clicked.connect(self.import_connections)
        self.export_btn.clicked.connect(self.export_connections)

        self.load_connections()

    def load_connections(self):
        self.connection_list.clear()
        connections = self.ssh_manager.get_all_connections()
        for name, data in connections.items():
            item = QListWidgetItem(f"{name} ({data['user']}@{data['host']})")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.connection_list.addItem(item)

    def add_connection(self):
        dialog = ConnectionDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.ssh_manager.add_connection(data)
                self.load_connections()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_connection(self):
        selected_item = self.connection_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a connection to edit.")
            return

        conn_name = selected_item.data(Qt.ItemDataRole.UserRole)
        conn_data = self.ssh_manager.get_connection(conn_name)

        dialog = ConnectionDialog(connection_data=conn_data, parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            # If name is changed, we need to remove old and add new
            if conn_name != new_data["name"]:
                self.ssh_manager.remove_connection(conn_name)
            self.ssh_manager.add_connection(new_data)
            self.load_connections()

    def delete_connection(self):
        selected_item = self.connection_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a connection to delete.")
            return

        conn_name = selected_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the connection '{conn_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.ssh_manager.remove_connection(conn_name)
            self.load_connections()

    def connect_to_selected(self, item):
        conn_name = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.ssh_manager.connect(conn_name)
            self.connection_selected.emit(conn_name)
            QMessageBox.information(self, "Success", f"Connected to {conn_name}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

    def show_context_menu(self, pos):
        item = self.connection_list.itemAt(pos)
        if not item:
            return

        context_menu = QMenu(self)
        connect_action = context_menu.addAction("Connect")
        edit_action = context_menu.addAction("Edit")
        delete_action = context_menu.addAction("Delete")

        action = context_menu.exec(self.connection_list.mapToGlobal(pos))

        if action == connect_action:
            self.connect_to_selected(item)
        elif action == edit_action:
            self.edit_connection()
        elif action == delete_action:
            self.delete_connection()

    def import_connections(self):
        """Import connections from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Connections", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_connections = json.load(f)

                # Validate and add connections
                imported_count = 0
                for name, data in imported_connections.items():
                    if self._validate_connection_data(data):
                        # Avoid name conflicts
                        original_name = name
                        counter = 1
                        while name in self.ssh_manager.get_all_connections():
                            name = f"{original_name}_{counter}"
                            counter += 1

                        data['name'] = name
                        self.ssh_manager.add_connection(data)
                        imported_count += 1

                self.load_connections()
                QMessageBox.information(
                    self, "Import Complete",
                    f"Successfully imported {imported_count} connections."
                )

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import connections: {e}")

    def export_connections(self):
        """Export connections to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Connections", "connections.json", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json
                connections = self.ssh_manager.get_all_connections()

                # Remove sensitive data for export
                export_data = {}
                for name, data in connections.items():
                    export_data[name] = {
                        'name': data.get('name', ''),
                        'host': data.get('host', ''),
                        'port': data.get('port', 22),
                        'user': data.get('user', ''),
                        'auth_method': data.get('auth_method', 'password'),
                        'key_path': data.get('key_path', '') if data.get('auth_method') == 'key' else ''
                        # Note: passwords are not exported for security
                    }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=4, ensure_ascii=False)

                QMessageBox.information(
                    self, "Export Complete",
                    f"Successfully exported {len(export_data)} connections to {file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export connections: {e}")

    def _validate_connection_data(self, data):
        """Validate connection data structure"""
        required_fields = ['host', 'user']
        return all(field in data and data[field] for field in required_fields)
