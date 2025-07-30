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
from utils.performance_monitor import get_performance_monitor, monitor_ui_operation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSH Remote Operations Tool")
        self.setGeometry(100, 100, 1400, 900)

        self.ssh_manager = SSHManager()
        self.file_manager = FileManager(self.ssh_manager)
        self.script_executor = ScriptExecutor(self.ssh_manager)

        # Initialize performance monitoring
        self.performance_monitor = get_performance_monitor()
        self.performance_monitor.set_components(self.ssh_manager, self.file_manager)
        self.performance_monitor.performance_warning.connect(self.on_performance_warning)

        self.setup_ui()

        # Start performance monitoring
        self.performance_monitor.start_monitoring()

    def setup_ui(self):
        # Main horizontal splitter (Left Sidebar | Main Content)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar
        self.connection_manager = ConnectionManagerWidget(self.ssh_manager)
        main_splitter.addWidget(self.connection_manager)

        # Main content area (vertically split)
        main_content_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top part of main content: File Browser (reduced size)
        self.file_browser = FileBrowserWidget(self.file_manager)
        main_content_splitter.addWidget(self.file_browser)

        # Bottom part of main content: Script and Log panels side by side
        script_log_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Script panel
        self.script_panel = ScriptPanelWidget(self.script_executor)
        self.script_panel.set_file_manager(self.file_manager)  # Pass file manager for remote browsing
        self.script_panel.set_ssh_manager(self.ssh_manager)    # Pass SSH manager for connection settings
        script_log_splitter.addWidget(self.script_panel)

        # Log panel
        self.log_panel = LogPanelWidget()
        script_log_splitter.addWidget(self.log_panel)

        # Set equal sizes for script and log panels
        script_log_splitter.setSizes([700, 700])  # Equal split

        main_content_splitter.addWidget(script_log_splitter)

        # Connect signals
        self.connection_manager.connection_selected.connect(self.on_connection_selected)
        self.script_panel.log_message.connect(self.log_panel.add_log)

        # Connect file manager to log panel for file operation messages
        # Note: In a full implementation, file_manager would emit signals for logging

        # Set initial sizes for the vertical splitter (1/3 for file browser, 2/3 for script/log)
        main_content_splitter.setSizes([300, 600]) # 1/3 and 2/3 of 900px height

        # Add the main content splitter to the main horizontal splitter
        main_splitter.addWidget(main_content_splitter)

        # Set initial sizes for the horizontal splitter (smaller sidebar)
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

    def on_connection_selected(self, connection_name):
        """Handle connection selection"""
        # Pass ssh_manager to file browser for default directory support
        self.file_browser.set_connection(connection_name, self.ssh_manager)
        self.script_panel.set_connection(connection_name)
        self.update_connection_status(connection_name)

    def update_connection_status(self, connection_name):
        """Update the connection status in status bar"""
        if connection_name:
            self.connection_status_label.setText(f"Connected to: {connection_name}")
            self.log_panel.add_log(f"Connected to {connection_name}", "success")
        else:
            self.connection_status_label.setText("Not connected")

    def on_performance_warning(self, warning_type: str, message: str):
        """处理性能警告"""
        print(f"⚠️  性能警告 [{warning_type}]: {message}")
        # 可以在这里添加UI通知，比如状态栏消息或弹窗
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(f"性能警告: {message}", 5000)

    def closeEvent(self, event):
        """窗口关闭时的清理工作"""
        # 停止性能监控
        self.performance_monitor.stop_monitoring()

        # 清理连接
        self.ssh_manager.disconnect_all()
        self.file_manager.cleanup_connections()

        # 导出性能报告
        try:
            import os
            report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'performance_report.json')
            self.performance_monitor.export_metrics(report_path)
        except Exception as e:
            print(f"导出性能报告失败: {e}")

        event.accept()

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
