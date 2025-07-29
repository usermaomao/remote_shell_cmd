import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout,
    QFileDialog
)
from PyQt6.QtGui import QColor, QTextCursor

class LogPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(self.log_display)

        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Log")
        self.export_btn = QPushButton("Export Log...")
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_btn)
        self.layout.addLayout(button_layout)

        self.clear_btn.clicked.connect(self.log_display.clear)
        self.export_btn.clicked.connect(self.export_log)

    def add_log(self, message, msg_type='info'):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        color_map = {
            'stdout': 'black',
            'stderr': 'red',
            'info': 'blue',
            'success': 'green'
        }
        color = color_map.get(msg_type, 'black')

        formatted_message = f'<span style="color: {color};"><b>[{timestamp}] [{msg_type.upper()}]</b>: {message}</span>'

        self.log_display.append(formatted_message)
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "", "Log Files (*.log);;Text Files (*.txt)")
        if path:
            try:
                with open(path, 'w') as f:
                    f.write(self.log_display.toPlainText())
            except Exception as e:
                self.add_log(f"Failed to export log: {e}", "stderr")
