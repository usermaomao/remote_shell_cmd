#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SSH Remote Operations Tool")
    app.setApplicationVersion("1.0")

    window = MainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
