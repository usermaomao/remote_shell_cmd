import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QTextEdit, QTabWidget, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt

from core.ssh_manager import SSHManager
from core.file_manager import FileManager
from core.script_executor import ScriptExecutor
from ui.connection_manager_widget import ConnectionManagerWidget
from ui.file_browser_widget import FileBrowserWidget
from ui.script_panel_widget import ScriptPanelWidget
from ui.log_panel_widget import LogPanelWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSH Remote Operations Tool")
        self.setGeometry(100, 100, 1400, 900)

        self.ssh_manager = SSHManager()
        self.file_manager = FileManager(self.ssh_manager)
        self.script_executor = ScriptExecutor(self.ssh_manager)

        self.setup_ui()

    def setup_ui(self):
        # Main horizontal splitter (Left Sidebar | Main Content)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar
        self.connection_manager = ConnectionManagerWidget(self.ssh_manager)
        main_splitter.addWidget(self.connection_manager)

        # Main content area (vertically split)
        main_content_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top part of main content: File Browser
        self.file_browser = FileBrowserWidget(self.file_manager)
        main_content_splitter.addWidget(self.file_browser)

        # Bottom part of main content: Tabbed panel for Scripting and Logs
        self.bottom_panel = QTabWidget()
        self.script_panel = ScriptPanelWidget(self.script_executor)
        self.log_panel = LogPanelWidget()
        self.bottom_panel.addTab(self.script_panel, "Script")
        self.bottom_panel.addTab(self.log_panel, "Log")
        main_content_splitter.addWidget(self.bottom_panel)

        # Connect signals
        self.connection_manager.connection_selected.connect(self.file_browser.set_connection)
        self.connection_manager.connection_selected.connect(self.script_panel.set_connection)
        self.script_panel.log_message.connect(self.log_panel.add_log)

        # Connect file manager to log panel for file operation messages
        # Note: In a full implementation, file_manager would emit signals for logging

        # Set initial sizes for the vertical splitter
        main_content_splitter.setSizes([600, 300]) # 60% and 40% of 900px height

        # Add the main content splitter to the main horizontal splitter
        main_splitter.addWidget(main_content_splitter)

        # Set initial sizes for the horizontal splitter
        main_splitter.setSizes([280, 1120]) # 20% and 80% of 1400px width

        self.setCentralWidget(main_splitter)

        # Add status bar
        self.setup_status_bar()

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connection status label
        self.connection_status_label = QLabel("Not connected")
        self.status_bar.addWidget(self.connection_status_label)

        # Add permanent widget for app info
        self.app_info_label = QLabel("SSH Remote Operations Tool v1.0")
        self.status_bar.addPermanentWidget(self.app_info_label)

        # Connect to connection manager signals to update status
        self.connection_manager.connection_selected.connect(self.update_connection_status)

    def update_connection_status(self, connection_name):
        """Update the connection status in status bar"""
        if connection_name:
            self.connection_status_label.setText(f"Connected to: {connection_name}")
            self.log_panel.add_log(f"Connected to {connection_name}", "success")
        else:
            self.connection_status_label.setText("Not connected")

def main():
    # This is for testing this component independently.
    # The main entry point is still src/main.py
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # Update the main entry point to use the new MainWindow
    from ssh_remote_tool.src.main import main as run_main
    run_main()
