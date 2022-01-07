"""
:module:    saskan_services_ui.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (Qt prototype)
"""

import sys
from pprint import pprint as pp  # type: ignore

from PySide2.QtCore import QRect
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QAction  # Generic action widget
from PySide2.QtWidgets import QApplication  # Root widget
from PySide2.QtWidgets import QCheckBox  # Checkbox widget
from PySide2.QtWidgets import QFileDialog  # File dialog window/function
from PySide2.QtWidgets import QGroupBox  # Group box for grouping widgets
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel  # Generic widget for text or img
from PySide2.QtWidgets import QLineEdit  # Single line text input widget
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QMenuBar
from PySide2.QtWidgets import QMessageBox  # Modal dialog window
from PySide2.QtWidgets import QPushButton  # Button widget
from PySide2.QtWidgets import QTextEdit  # Multi-line text input widget
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QToolButton
from PySide2.QtWidgets import QVBoxLayout  # Vertical layout manager
from PySide2.QtWidgets import QWidget  # Base class for all objects

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore

# QButtonGroup,  # Radio-ish buttons container
# QFormLayout,   # Layout for interactive forms
# QHBoxLayout,   # Horizontal layout manager

TX = SaskanTexts()


class SaskanStyles(QMainWindow):
    """Define style sheets for QT app"""

    def __init__(self):
        """Define basic template for the app."""
        self.base = "background-color: black; " + \
                    "border: 1px solid; " + \
                    "border-color: black; " + \
                    "color: white;"
        self.ss = self.base

    def set_style(self,
                  widget: str = None,
                  style: str = None,):
        """Set the style of a widget.

        :Args:
            widget: str in ('label', 'button', None)
            style: str in ('black', 'gray', 'white', None)
        """
        self.ss = self.base


class SaskanServices(QWidget):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs."""

    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.SS = SaskanStyles()
        self.initialize_UI()

    def initialize_UI(self):
        """Set window size and name. Show the window."""
        self.setObjectName(u"saskan_services")  # Is this necessary?
        self.setGeometry(100, 100, 900, 600)
        self.setWindowTitle(TX.tl.app)
        self.setStyleSheet(self.SS.base)
        self.setFont(QFont('Arial', 16))
        # self.root_w = QWidget(self)
        # self.setCentralWidget(self.root_w)
        # ==============================================================
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        pp((dir(self)))
        self.show()

    def save_state(self):
        """Slot for Save action"""
        print("Save state")

    def exit_app(self):
        """Slot for Exit action"""
        print("Exit application")
        self.close()

    def add_item(self):
        """Slot for Add action"""
        print("Add an item")

    def remove_item(self):
        """Slot for Remove action"""
        print("Remove an item")

    def undo_item(self):
        """Slot for Undo action"""
        print("Undo last action")

    def edit_schema(self):
        """Slot for Schema action"""
        print("Edit schema")

    def monitor_services(self):
        """Slot for Monitor action"""
        print("Monitor services")

    def control_services(self):
        """Slot for Control action"""
        print("Control services")

    def test_request(self):
        """Slot for Test action"""
        print("Test services")

    def help_me(self):
        """Slot for Help action"""
        print("Display help")

    def create_actions(self):
        """Define actions. Triggred by menu items and toolbar buttons."""
        # Add these texts to saskan_texts.
        # Include icons for these actions.
        self.actions = {
            "save": {
                "t": "Save",
                "p": "Save current state",
                "c": "Ctrl+S",
                "s": self.save_state,
                "w": None},
            "exit": {
                "t": "Exit",
                "p": "Quit the application",
                "c": "Ctrl+Q",
                "s": self.exit_app,
                "w": None},
            "add": {
                "t": "Add",
                "p": "Start a new item",
                "c": "Ctrl+N",
                "s": self.add_item,
                "w": None},
            "remove": {
                "t": "Remove",
                "p": "Delete the current item",
                "c": "Ctrl+X",
                "s": self.remove_item,
                "w": None},
            "undo": {
                "t": "Undo",
                "p": "Reverse previous action",
                "c": "Ctrl+Z",
                "s": self.undo_item,
                "w": None},
            "schema": {
                "t": "Schema",
                "p": "Edit the Saskan Schema",
                "c": "Ctrl+Alt+S",
                "s": self.edit_schema,
                "w": None},
            "monitor": {
                "t": "Monitor",
                "p": "Monitor running services",
                "c": "Ctrl+Alt+M",
                "s": self.monitor_services,
                "w": None},
            "control": {
                "t": "Control",
                "p": "Start, stop, manage services",
                "c": "Ctrl+Alt+C",
                "s": self.control_services,
                "w": None},
            "test": {
                "t": "Test",
                "p": "Test service requests",
                "c": "Ctrl+Alt+T",
                "s": self.test_request,
                "w": None},
            "help": {
                "t": "User Guide",
                "p": "Get help",
                "c": "Ctrl+H",
                "s": self.help_me,
                "w": None}}
        for key, obj in self.actions.items():
            # Can also provide an icon as the first parameter:
            # Also see .icon() and .iconText() get methods
            self.actions[key]["w"] = \
                QAction(QIcon('favicon.jpg'), obj["t"], self)
            self.actions[key]["w"].setToolTip(obj["p"])     # Does nothing
            self.actions[key]["w"].setShortcut(obj["c"])    # Works fine
            self.actions[key]["w"].triggered.connect(obj["s"])  # Works fine

    def create_menus(self):
        """Define menus and menu items."""
        self.menu_bar = QMenuBar(self)
        # self.menu_bar.isNativeMenuBar()       # Does not do anything

        self.menu_file = self.menu_bar.addMenu("File")
        self.menu_file.addAction(self.actions["save"]["w"])
        self.menu_file.addAction(self.actions["exit"]["w"])
        self.menu_bar.addMenu(self.menu_file)

        self.menu_edit = self.menu_bar.addMenu("Edit")
        self.menu_edit.addAction(self.actions["add"]["w"])
        self.menu_edit.addAction(self.actions["remove"]["w"])
        self.menu_edit.addAction(self.actions["undo"]["w"])
        self.menu_bar.addMenu(self.menu_edit)

        self.menu_window = self.menu_bar.addMenu("Window")
        self.menu_window.addAction(self.actions["schema"]["w"])
        self.menu_window.addAction(self.actions["monitor"]["w"])
        self.menu_window.addAction(self.actions["control"]["w"])
        self.menu_window.addAction(self.actions["test"]["w"])
        self.menu_bar.addMenu(self.menu_window)

        self.menu_help = self.menu_bar.addMenu("Help")
        self.menu_bar.addMenu(self.menu_help)
        self.menu_help.addAction(self.actions["help"]["w"])
        self.menu_help = QMenu(self.menu_bar)

    def create_toolbar(self):
        """Define toolbar container and tool buttons.
        Check out hover and pressed styles.
        """
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(64, 100))
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setGeometry(QRect(0, 40, 900, 60))
        self.toolbar.addAction(self.actions["save"]["w"])
        for key, obj in self.actions.items():
            self.toolbar.addAction(obj["w"])

# Run program
if __name__ == '__main__':
    """Instantiate the app and start the event loop.
    """
    app = QApplication(sys.argv)
    ex = SaskanServices()
    sys.exit(app.exec_())
