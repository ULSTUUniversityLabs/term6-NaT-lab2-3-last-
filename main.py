import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget)
from PyQt5 import QtGui

from src.RouteTab import RouteTab
from src.IpconfigTab import IpconfigTab
from src.PingTab import PingTab
from src.TracertTab import TracertTab

import ctypes
import sys


class NetworkUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Utility")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(PingTab(), "Ping")
        self.tabs.addTab(TracertTab(), "Tracert")
        self.tabs.addTab(IpconfigTab(), "Ipconfig")
        self.tabs.addTab(RouteTab(), "Route")


def set_dark_palette(app):
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(18, 18, 18))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))

    app.setPalette(dark_palette)

    dark_qss = """
    QWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }

    QLineEdit, QTextEdit {
        background-color: #3b3b3b;
        color: #ffffff;
        border: 1px solid #666666;
    }

    QTableWidget {
        background-color: #3b3b3b;
        color: #ffffff;
        gridline-color: #444444;
    }

    QHeaderView::section {
        background-color: #444444;
        color: #ffffff;
        border: 1px solid #666666;
    }

    QPushButton {
        background-color: #444444;
        color: #ffffff;
        border: 1px solid #666666;
        padding: 5px;
    }

    QPushButton:hover {
        background-color: #555555;
    }

    QTabWidget::pane { /* Border and background for tab area */
        background: #2e2e2e;
        border: 1px solid #444444;
    }

    QTabBar::tab {
        background: #444444;
        color: #ffffff;
        padding: 5px;
    }

    QTabBar::tab:selected {
        background: #555555;
        color: #ffffff;
    }
    """
    app.setStyleSheet(dark_qss)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    set_dark_palette(app)
    
    window = NetworkUtility()
    window.show()
    sys.exit(app.exec_())