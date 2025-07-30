from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLineEdit, QLabel, QFrame, QFileDialog, QTabWidget, QComboBox,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import pyqtSignal
from core.script_executor import ScriptExecutor
from ui.remote_file_dialog import RemoteFileDialog

class ScriptPanelWidget(QWidget):
    log_message = pyqtSignal(str, str) # message, type ('stdout', 'stderr', 'info')

    def __init__(self, script_executor: ScriptExecutor, parent=None):
        super().__init__(parent)
        self.script_executor = script_executor
        self.current_connection = None
        self.file_manager = None  # Will be set by main window

        self.layout = QVBoxLayout(self)

        # Mode Selection
        self.mode_tabs = QTabWidget()
        self.input_mode_widget = self._create_input_mode()
        self.file_mode_widget = self._create_file_mode()

        self.mode_tabs.addTab(self.input_mode_widget, "Input Script")
        self.mode_tabs.addTab(self.file_mode_widget, "Select File")
        self.layout.addWidget(self.mode_tabs)

        # Options and Parameters
        options_layout = QHBoxLayout()
        self.exec_dir_label = QLabel("Working Directory:")
        self.exec_dir_input = QLineEdit(".")
        self.browse_dir_btn = QPushButton("Browse...")
        self.params_label = QLabel("Parameters:")
        self.params_input = QLineEdit()

        options_layout.addWidget(self.exec_dir_label)
        options_layout.addWidget(self.exec_dir_input)
        options_layout.addWidget(self.browse_dir_btn)
        options_layout.addWidget(self.params_label)
        options_layout.addWidget(self.params_input)
        self.layout.addLayout(options_layout)

        # Connect browse directory button
        self.browse_dir_btn.clicked.connect(self.browse_working_directory)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.execute_btn = QPushButton("Execute")
        self.terminate_btn = QPushButton("Terminate")
        self.save_btn = QPushButton("Save Script...")
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.terminate_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        self.layout.addLayout(button_layout)

        # Connect signals
        self.execute_btn.clicked.connect(self.execute_script)
        self.terminate_btn.clicked.connect(self.terminate_script)
        self.save_btn.clicked.connect(self.save_script)

        self.set_connection(None) # Initially disabled

    def _create_input_mode(self):
        """Create the input script mode widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter your script here...")
        layout.addWidget(self.script_input)

        return widget

    def _create_file_mode(self):
        """Create the file selection mode widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File selection
        file_layout = QHBoxLayout()
        self.script_file_input = QLineEdit()
        self.script_file_input.setPlaceholderText("Select a script file from remote server...")
        self.script_file_input.setReadOnly(True)
        self.browse_script_btn = QPushButton("Browse...")

        file_layout.addWidget(self.script_file_input)
        file_layout.addWidget(self.browse_script_btn)
        layout.addLayout(file_layout)

        # Script preview with better sizing
        preview_label = QLabel("Script Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        layout.addWidget(preview_label)

        self.script_preview = QTextEdit()
        self.script_preview.setPlaceholderText("Select a script file to preview its content...")
        self.script_preview.setReadOnly(True)
        # Remove height restriction to allow more content
        self.script_preview.setMinimumHeight(100)
        # Set font for better code readability
        self.script_preview.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.script_preview)

        # Connect signals
        self.browse_script_btn.clicked.connect(self.browse_remote_script)

        return widget

    def set_connection(self, connection_name):
        self.current_connection = connection_name
        is_connected = bool(connection_name)
        self.execute_btn.setEnabled(is_connected)
        self.terminate_btn.setEnabled(is_connected)
        if hasattr(self, 'script_input'):
            self.script_input.setEnabled(is_connected)
        if hasattr(self, 'browse_script_btn'):
            self.browse_script_btn.setEnabled(is_connected)
        if hasattr(self, 'browse_dir_btn'):
            self.browse_dir_btn.setEnabled(is_connected)

    def set_file_manager(self, file_manager):
        """Set the file manager for remote file browsing"""
        self.file_manager = file_manager

    def set_ssh_manager(self, ssh_manager):
        """Set the SSH manager for accessing connection settings"""
        self.ssh_manager = ssh_manager

    def handle_output(self, message, msg_type):
        self.log_message.emit(message, msg_type)

    def execute_script(self):
        if not self.current_connection:
            self.log_message.emit("No active connection.", "stderr")
            return

        current_tab = self.mode_tabs.currentIndex()
        exec_dir = self.exec_dir_input.text()
        params = self.params_input.text()

        if current_tab == 0:  # Input mode
            script_content = self.script_input.toPlainText()
            if not script_content.strip():
                self.log_message.emit("Script is empty.", "stderr")
                return

            self.log_message.emit(f"Executing script in '{exec_dir}'...", "info")
            try:
                self.script_executor.execute_script(
                    self.current_connection,
                    script_content,
                    exec_dir,
                    params,
                    self.handle_output
                )
            except Exception as e:
                self.log_message.emit(f"Failed to start script: {e}", "stderr")

        else:  # File mode
            script_file = self.script_file_input.text()
            if not script_file.strip():
                self.log_message.emit("No script file selected.", "stderr")
                return

            # Execute the script file directly
            command = f"bash {script_file}"
            self.log_message.emit(f"Executing script file '{script_file}' in '{exec_dir}'...", "info")
            try:
                self.script_executor.execute_script(
                    self.current_connection,
                    command,
                    exec_dir,
                    params,
                    self.handle_output
                )
            except Exception as e:
                self.log_message.emit(f"Failed to start script: {e}", "stderr")

    def terminate_script(self):
        if self.current_connection:
            self.script_executor.terminate(self.current_connection)
            self.log_message.emit("Termination signal sent.", "info")

    def save_script(self):
        current_tab = self.mode_tabs.currentIndex()
        if current_tab == 0:  # Input mode
            path, _ = QFileDialog.getSaveFileName(self, "Save Script", "", "Shell Scripts (*.sh);;All Files (*)")
            if path:
                try:
                    with open(path, 'w') as f:
                        f.write(self.script_input.toPlainText())
                    self.log_message.emit(f"Script saved to {path}", "info")
                except Exception as e:
                    self.log_message.emit(f"Failed to save script: {e}", "stderr")
        else:
            QMessageBox.information(self, "Info", "Use 'Save As...' to save the selected script file locally.")

    def browse_remote_script(self):
        """Browse and select a script file from remote server"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        if not self.file_manager:
            QMessageBox.warning(self, "Warning", "File manager not available.")
            return

        # Get default directory from connection settings
        initial_path = "/"
        if hasattr(self, 'ssh_manager') and self.ssh_manager and self.current_connection:
            conn_data = self.ssh_manager.get_connection(self.current_connection)
            if conn_data:
                initial_path = conn_data.get("default_dir", "/")

        # Open remote file dialog with script file filter
        script_extensions = ['.sh', '.py', '.pl', '.rb', '.js', '.bat', '.cmd']
        selected_file = RemoteFileDialog.get_remote_file(
            self.file_manager,
            self.current_connection,
            initial_path=initial_path,
            file_filter=script_extensions,
            parent=self
        )

        if selected_file:
            self.script_file_input.setText(selected_file)
            self.load_script_preview(selected_file)

    def browse_working_directory(self):
        """Browse and select working directory from remote server"""
        if not self.current_connection:
            QMessageBox.warning(self, "Warning", "No active connection.")
            return

        if not self.file_manager:
            QMessageBox.warning(self, "Warning", "File manager not available.")
            return

        # Get initial path from current input or connection default
        initial_path = self.exec_dir_input.text() or "/"
        if initial_path == "." and hasattr(self, 'ssh_manager') and self.ssh_manager and self.current_connection:
            conn_data = self.ssh_manager.get_connection(self.current_connection)
            if conn_data:
                initial_path = conn_data.get("default_dir", "/")

        # Create a modified dialog for directory selection
        from ui.remote_directory_dialog import RemoteDirectoryDialog
        selected_dir = RemoteDirectoryDialog.get_remote_directory(
            self.file_manager,
            self.current_connection,
            initial_path=initial_path,
            parent=self
        )

        if selected_dir:
            self.exec_dir_input.setText(selected_dir)

    def load_script_preview(self, script_path):
        """Load and preview the selected script file"""
        try:
            if self.file_manager and self.current_connection:
                try:
                    # Use SFTP to read file content (first 3000 characters for better preview)
                    ssh_client = self.file_manager.ssh_manager.get_client(self.current_connection)
                    if ssh_client:
                        sftp = ssh_client.open_sftp()
                        try:
                            with sftp.file(script_path, 'r') as f:
                                content = f.read(3000).decode('utf-8', errors='ignore')
                                if len(content) == 3000:
                                    # Find the last complete line to avoid cutting in the middle
                                    last_newline = content.rfind('\n')
                                    if last_newline > 2500:  # Keep most content
                                        content = content[:last_newline]
                                    content += "\n\n... (file truncated for preview)"
                                self.script_preview.setPlainText(content)
                        finally:
                            sftp.close()
                    else:
                        self.script_preview.setPlainText("[No connection available]")
                except Exception as e:
                    self.script_preview.setPlainText(f"[Error loading file: {str(e)}]")
            else:
                self.script_preview.setPlainText("[File manager not available]")

            self.log_message.emit(f"Selected script file: {script_path}", "info")
        except Exception as e:
            self.log_message.emit(f"Failed to load script preview: {e}", "stderr")
