"""
:module:    saskan_services_ui.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (Qt prototype)
"""

import sys
# from pprint import pprint as pp  # type: ignore

from PySide2.QtCore import QRect
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtGui import QIcon
# from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
# from PySide2.QtWidgets import QButtonGroup
# from PySide2.QtWidgets import QCheckBox
# from PySide2.QtWidgets import QFileDialog
# from PySide2.QtWidgets import QFormLayout
# from PySide2.QtWidgets import QGroupBox
# from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QMenuBar
# from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QOpenGLWidget
# from PySide2.QtWidgets import QPlainTextEdit
from PySide2.QtWidgets import QPushButton
# from PySide2.QtWidgets import QStatusBar
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QToolButton
# from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore

TX = SaskanTexts()


class SaskanStyles(object):
    """Define style sheets for QT app"""

    def __init__(self):
        """Define stylesheets for the app."""
        pass

    @classmethod
    def _base_style(cls):
        """Set default style."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: white;"
        return ss

    @classmethod
    def _button_style(cls):
        """Set style for buttons"""
        ss = "background-color: white; " + \
             "border-width: 1px 3px 3px 1px; " + \
             "border-style: solid; " + \
             "border-color: gray;" + \
             "color: black;" + \
             "border-radius: 5px;" + \
             "margin: 5px;" + \
             "padding: 5px;"
        return ss

    @classmethod
    def _canvas_style(cls):
        """Set OpenGL canvas style."""
        ss = "border: 1px solid; " + \
             "border-color: whhite; "
        return ss

    @classmethod
    def _editor_style(cls):
        """Set style for editors."""
        ss = "background-color: white; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: black;"
        return ss

    @classmethod
    def _menu_style(cls):
        """Set style for menus."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: white; " + \
             "color: white;"
        return ss

    @classmethod
    def _status_style(cls):
        """Set default style."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;"
        return ss

    @classmethod
    def get_style(self,
                  p_widget: str = 'base'):
        """Set the style of a widget.

        :Args:
            p_widget: str
        """
        if p_widget in ('base'):
            ss = self._base_style()
        elif p_widget in ('editor', 'help'):
            ss = self._editor_style()
        elif p_widget in ('button'):
            ss = self._button_style()
        elif p_widget in ('canvas'):
            ss = self._canvas_style()
        elif p_widget in ('menu'):
            ss = self._menu_style()
        elif p_widget in ('status'):
            ss = self._status_style()
        else:
            ss = self._base_style()
        return ss


class SaskanServices(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs."""

    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.SS = SaskanStyles()
        self.initialize_UI()

    def initialize_UI(self):
        """Set window size and name. Show the window."""
        self.setObjectName(u"saskan_services")  # Is this necessary?
        self.setGeometry(100, 100, 875, 650)
        self.setWindowTitle(TX.tl.app)
        self.setStyleSheet(self.SS.get_style())
        self.setFont(QFont('Arial', 16))
        # ==============================================================
        self.create_tool_actions()
        self.create_editor_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_editor_title()
        self.create_editor()
        self.create_editor_buttons()
        self.create_opengl_display()
        self.create_help_display()
        self.create_statusbar()
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

    def show_services(self):
        """Slot for Services action"""
        print("Show services status")

    def scroll_to_top(self):
        """Slot for Top action"""
        print("Scroll to top")

    def scroll_to_bottom(self):
        """Slot for Tail action"""
        print("Scroll to bottom")

    def show_full_log(self):
        """Slot for Log action"""
        print("Refresh log display")

    def show_failures(self):
        """Slot for Failures action"""
        print("Show failed requests")

    def show_requests(self):
        """Slot for Requests action"""
        print("Show pending requests")

    def show_pressure(self):
        """Slot for Pressure action"""
        print("Show average load on services")

    def create_tool_actions(self):
        """Define actions. Triggered by menu items and toolbar buttons."""
        # Add these texts to saskan_texts.
        # Include icons for these actions.
        self.tool_actions = {
            "save": {
                "t": "Save",
                "p": "Save current state",
                "c": "Ctrl+S",
                "s": self.save_state,
                "w": None},
            "add": {
                "t": "Add",
                "p": "Start a new item",
                "c": "Ctrl+N",
                "s": self.add_item,
                "w": None},
            "remove": {
                "t": "Del",
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
                "t": "Edit",
                "p": "Edit the Saskan Schema",
                "c": "Ctrl+Alt+S",
                "s": self.edit_schema,
                "w": None},
            "monitor": {
                "t": "Mon",
                "p": "Monitor running services",
                "c": "Ctrl+Alt+M",
                "s": self.monitor_services,
                "w": None},
            "control": {
                "t": "Ctl",
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
                "t": "Help",
                "p": "Get help",
                "c": "Ctrl+H",
                "s": self.help_me,
                "w": None},
            "exit": {
                "t": "Exit",
                "p": "Quit the application",
                "c": "Ctrl+Q",
                "s": self.exit_app,
                "w": None}}
        for key, obj in self.tool_actions.items():
            # Can also provide an icon as the first parameter:
            # Also see .icon() and .iconText() get methods
            self.tool_actions[key]["w"] = \
                QAction(QIcon('images/favicon.jpg'), obj["t"], self)
            self.tool_actions[key]["w"].setToolTip(obj["p"])
            self.tool_actions[key]["w"].setShortcut(obj["c"])
            self.tool_actions[key]["w"].triggered.connect(obj["s"])

    def create_editor_actions(self):
        """Define actions. Triggered by editor buttons."""
        # Add these texts to saskan_texts.
        # Include icons for these actions.
        self.editor_actions = {
            "services": {
                "t": "Services",
                "p": "Show services status",
                "c": "Ctrl+Alt+S",
                "s": self.show_services,
                "w": None},
            "top": {
                "t": "Go to Top",
                "p": "Scroll to top",
                "c": "Ctrl+Alt+T",
                "s": self.scroll_to_top,
                "w": None},
            "tail": {
                "t": "Go to End",
                "p": "Scroll to bottom",
                "c": "Ctrl+Alt+B",
                "s": self.scroll_to_bottom,
                "w": None},
            "log": {
                "t": "Show Log",
                "p": "Show the log",
                "c": "Ctrl+Alt_L",
                "s": self.show_full_log,
                "w": None},
            "requests": {
                "t": "Requests",
                "p": "Show pending requests",
                "c": "Ctrl+Alt+R",
                "s": self.show_requests,
                "w": None},
            "failures": {
                "t": "Failures",
                "p": "Show failures",
                "c": "Ctrl+Alt+F",
                "s": self.show_failures,
                "w": None},
            "pressure": {
                "t": "Pressure",
                "p": "Show loads on services",
                "c": "Ctrl+Alt+P",
                "s": self.show_pressure,
                "w": None}}
        for key, obj in self.editor_actions.items():
            self.editor_actions[key]["w"] = \
                QAction(QIcon('images/favicon.jpg'), obj["t"], self)
            self.editor_actions[key]["w"].setToolTip(obj["p"])
            self.editor_actions[key]["w"].setShortcut(obj["c"])
            self.editor_actions[key]["w"].triggered.connect(obj["s"])

    def create_menus(self):
        """Define menus and menu items."""
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(0, 0, 225, 25)
        self.menu_bar.setStyleSheet(self.SS.get_style('menu'))

        self.menu_file = self.menu_bar.addMenu("File")
        self.menu_file.addAction(self.tool_actions["save"]["w"])
        self.menu_file.addAction(self.tool_actions["exit"]["w"])
        self.menu_bar.addMenu(self.menu_file)

        self.menu_edit = self.menu_bar.addMenu("Edit")
        self.menu_edit.addAction(self.tool_actions["add"]["w"])
        self.menu_edit.addAction(self.tool_actions["remove"]["w"])
        self.menu_edit.addAction(self.tool_actions["undo"]["w"])
        self.menu_bar.addMenu(self.menu_edit)

        self.menu_window = self.menu_bar.addMenu("Window")
        self.menu_window.addAction(self.tool_actions["schema"]["w"])
        self.menu_window.addAction(self.tool_actions["monitor"]["w"])
        self.menu_window.addAction(self.tool_actions["control"]["w"])
        self.menu_window.addAction(self.tool_actions["test"]["w"])
        self.menu_bar.addMenu(self.menu_window)

        self.menu_help = self.menu_bar.addMenu("Help")
        self.menu_bar.addMenu(self.menu_help)
        self.menu_help.addAction(self.tool_actions["help"]["w"])
        self.menu_help = QMenu(self.menu_bar)

    def create_toolbar(self):
        """Define toolbar container and tool buttons.
        Check out hover and pressed styles.
        """
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.toolbar.setGeometry(QRect(0, 0, 600, 60))
        for key, obj in self.tool_actions.items():
            tb = QToolButton(self.toolbar)
            tb.setFont(QFont('Arial', 9))
            tb.setStyleSheet(self.SS.get_style('editor'))
            tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            tb.setDefaultAction(obj["w"])
            self.toolbar.addWidget(tb)
        self.toolbar.move(380, 20)

    def create_editor_title(self):
        """Define area for display identifying current editor mode."""
        self.editor_title = QLabel(self)
        self.editor_title.setFont(QFont('Arial', 18))
        self.editor_title.setText("Schema Editor")
        self.editor_title.setStyleSheet(self.SS.get_style('status'))
        self.editor_title.setGeometry(QRect(0, 0, 250, 65))
        self.editor_title.move(10, 30)

    def create_editor(self):
        """Define area for display of Schema Editor, Monitor Display
        and Control Forms."""
        self.editor_display = QTextEdit(self)
        self.editor_display.setGeometry(QRect(0, 0, 825, 300))
        self.editor_display.setStyleSheet(self.SS.get_style('editor'))
        self.editor_display.setReadOnly(True)
        self.editor_display.move(15, 80)

    def create_editor_buttons(self):
        """Define push buttons related to the editor functions."""
        col = 35
        for key, obj in self.editor_actions.items():
            ed_btn = QPushButton(obj["t"], self)
            ed_btn.setGeometry(QRect(0, 0, 100, 40))
            ed_btn.setStyleSheet(self.SS.get_style('button'))
            ed_btn.addAction(obj["w"])
            ed_btn.clicked.connect(obj["s"])
            ed_btn.move(col, 380)
            col += ed_btn.width() + 5

    def create_opengl_display(self):
        """Define a canvas area."""
        self.canvas = QOpenGLWidget(self)
        self.canvas.setGeometry(QRect(0, 0, 400, 175))
        self.canvas.initializeGL()
        self.canvas.setStyleSheet(self.SS.get_style('canvas'))
        self.canvas.move(0, 450)

    def create_help_display(self):
        """Define a help display area."""
        self.help_display = QTextEdit(self)
        self.help_display.setGeometry(QRect(0, 0, 375, 175))
        self.help_display.setStyleSheet(self.SS.get_style('help'))
        self.help_display.setReadOnly(True)
        self.help_display.move(450, 450)

    def create_statusbar(self):
        """Define status bar display area."""
        self.status_bar = QLineEdit(self)
        self.status_bar.setGeometry(QRect(0, 0, 850, 30))
        self.status_bar.setStyleSheet(self.SS.get_style('status'))
        self.status_bar.setReadOnly(True)
        self.status_bar.setAlignment(Qt.AlignHCenter)
        self.status_bar.setFrame(True)
        self.status_bar.setText("Ready Player One")
        self.status_bar.move(0, 620)


# Run program
if __name__ == '__main__':
    """Instantiate the app and start the event loop.
    """
    app = QApplication(sys.argv)
    ex = SaskanServices()
    sys.exit(app.exec_())
