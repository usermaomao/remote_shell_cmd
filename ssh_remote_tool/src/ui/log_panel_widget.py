import datetime
import re
import html
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout,
    QFileDialog, QComboBox, QLabel, QCheckBox
)
from PyQt6.QtGui import QColor, QTextCursor
from PyQt6.QtCore import Qt

class LogPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.all_logs = []  # Store all log entries for filtering

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Info", "Success", "Error", "Output"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)

        self.auto_scroll_checkbox = QCheckBox("Auto Scroll")
        self.auto_scroll_checkbox.setChecked(True)
        filter_layout.addWidget(self.auto_scroll_checkbox)

        filter_layout.addStretch()
        self.layout.addLayout(filter_layout)

        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)

        # Set font and styling for better readability
        self.log_display.setStyleSheet("""
            QTextBrowser {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)

        self.layout.addWidget(self.log_display)

        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Log")
        self.export_btn = QPushButton("Export Log...")
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_btn)
        self.layout.addLayout(button_layout)

        self.clear_btn.clicked.connect(self.clear_logs)
        self.export_btn.clicked.connect(self.export_log)

    def clean_ansi_codes(self, text):
        """Remove ANSI color codes and control sequences from text"""
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)

        # Remove other control characters but keep newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        return text

    def format_message_for_html(self, message):
        """Format message for HTML display with proper line breaks"""
        # Clean ANSI codes first
        message = self.clean_ansi_codes(message)

        # Escape HTML characters
        message = html.escape(message)

        # Convert newlines to HTML line breaks
        message = message.replace('\n', '<br>')

        # Convert multiple spaces to non-breaking spaces to preserve formatting
        message = re.sub(r'  +', lambda m: '&nbsp;' * len(m.group()), message)

        return message

    def add_log(self, message, msg_type='info'):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the log entry
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'type': msg_type
        }
        self.all_logs.append(log_entry)

        # Apply current filter
        self.apply_filter()

    def apply_filter(self):
        """Apply the current filter to the log display"""
        filter_type = self.filter_combo.currentText().lower()

        self.log_display.clear()

        for log_entry in self.all_logs:
            msg_type = log_entry['type']

            # Check if this log entry should be displayed
            if filter_type == 'all' or \
               (filter_type == 'info' and msg_type == 'info') or \
               (filter_type == 'success' and msg_type == 'success') or \
               (filter_type == 'error' and msg_type in ['stderr', 'error']) or \
               (filter_type == 'output' and msg_type in ['stdout', 'stderr']):

                color_map = {
                    'stdout': '#2E8B57',      # Sea Green
                    'stderr': '#DC143C',      # Crimson
                    'info': '#4169E1',        # Royal Blue
                    'success': '#228B22',     # Forest Green
                    'error': '#DC143C'        # Crimson
                }
                color = color_map.get(msg_type, '#000000')  # Default black

                # Format the message with proper HTML formatting
                clean_message = self.format_message_for_html(log_entry["message"])

                formatted_message = f'<span style="color: {color};"><b>[{log_entry["timestamp"]}] [{msg_type.upper()}]</b>: {clean_message}</span>'
                self.log_display.append(formatted_message)

        # Auto scroll to end if enabled
        if self.auto_scroll_checkbox.isChecked():
            self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def clear_logs(self):
        """Clear all logs"""
        self.all_logs.clear()
        self.log_display.clear()

    def export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "", "Log Files (*.log);;Text Files (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for log_entry in self.all_logs:
                        f.write(f"[{log_entry['timestamp']}] [{log_entry['type'].upper()}]: {log_entry['message']}\n")
                self.add_log(f"Log exported to {path}", "success")
            except Exception as e:
                self.add_log(f"Failed to export log: {e}", "stderr")
