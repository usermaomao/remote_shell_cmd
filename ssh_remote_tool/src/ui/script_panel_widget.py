from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLineEdit, QLabel, QFrame, QFileDialog, QTabWidget, QComboBox,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import pyqtSignal
from core.script_executor import ScriptExecutor

class ScriptPanelWidget(QWidget):
    log_message = pyqtSignal(str, str) # message, type ('stdout', 'stderr', 'info')

    def __init__(self, script_executor: ScriptExecutor, parent=None):
        super().__init__(parent)
        self.script_executor = script_executor
        self.current_connection = None

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
        self.params_label = QLabel("Parameters:")
        self.params_input = QLineEdit()
        options_layout.addWidget(self.exec_dir_label)
        options_layout.addWidget(self.exec_dir_input)
        options_layout.addWidget(self.params_label)
        options_layout.addWidget(self.params_input)
        self.layout.addLayout(options_layout)

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

        # Script preview
        self.script_preview = QTextEdit()
        self.script_preview.setPlaceholderText("Script content will be shown here...")
        self.script_preview.setReadOnly(True)
        self.script_preview.setMaximumHeight(150)
        layout.addWidget(QLabel("Script Preview:"))
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

        # For now, let user input the path manually
        # In a full implementation, this would open a file browser dialog
        script_path, ok = QInputDialog.getText(
            self, "Select Script File",
            "Enter the full path to the script file on remote server:"
        )

        if ok and script_path:
            self.script_file_input.setText(script_path)
            self.load_script_preview(script_path)

    def load_script_preview(self, script_path):
        """Load and preview the selected script file"""
        try:
            # This is a simplified implementation
            # In a real app, you'd use SFTP to read the file content
            self.script_preview.setPlainText(f"Preview for: {script_path}\n\n[Script content would be loaded here]")
            self.log_message.emit(f"Selected script file: {script_path}", "info")
        except Exception as e:
            self.log_message.emit(f"Failed to load script preview: {e}", "stderr")
