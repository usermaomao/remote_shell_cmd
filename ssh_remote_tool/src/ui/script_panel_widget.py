from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLineEdit, QLabel, QFrame, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from ..core.script_executor import ScriptExecutor

class ScriptPanelWidget(QWidget):
    log_message = pyqtSignal(str, str) # message, type ('stdout', 'stderr', 'info')

    def __init__(self, script_executor: ScriptExecutor, parent=None):
        super().__init__(parent)
        self.script_executor = script_executor
        self.current_connection = None

        self.layout = QVBoxLayout(self)

        # Script Input Area
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter your script here...")
        self.layout.addWidget(self.script_input)

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

    def set_connection(self, connection_name):
        self.current_connection = connection_name
        is_connected = bool(connection_name)
        self.execute_btn.setEnabled(is_connected)
        self.terminate_btn.setEnabled(is_connected)
        self.script_input.setEnabled(is_connected)

    def handle_output(self, message, msg_type):
        self.log_message.emit(message, msg_type)

    def execute_script(self):
        if not self.current_connection:
            self.log_message.emit("No active connection.", "stderr")
            return

        script_content = self.script_input.toPlainText()
        if not script_content.strip():
            self.log_message.emit("Script is empty.", "stderr")
            return

        exec_dir = self.exec_dir_input.text()
        params = self.params_input.text()

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

    def terminate_script(self):
        if self.current_connection:
            self.script_executor.terminate(self.current_connection)
            self.log_message.emit("Termination signal sent.", "info")

    def save_script(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Script", "", "Shell Scripts (*.sh);;All Files (*)")
        if path:
            try:
                with open(path, 'w') as f:
                    f.write(self.script_input.toPlainText())
                self.log_message.emit(f"Script saved to {path}", "info")
            except Exception as e:
                self.log_message.emit(f"Failed to save script: {e}", "stderr")
