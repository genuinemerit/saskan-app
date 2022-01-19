#!/usr/bin/python3.9
"""
:module:    saskan_services.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (Qt prototype)

@DEV:
- Refactoring now that main app inherits from QMainWindow.

  - Organized code so that it is more object-oriented, defining major
    widgets in distinct classes, similar to Kivy style. Also group
    code so that it functions related to a widget are grouped near
    each other, as opposed, to example, for putting all "action" methods
    together.

  - Re-introduced MenuBar. Keep it simple --> Quit, About

  - Use standard statusbar, the one that is "built in" to
    the QMainWindow class.

  - Use layouts to contain for all other widgets.

    - My understanding is that the children widgets get created
      first, then those existing widgets are added to the layout,
      then the layout is added to the main window using setLayout().

    - Use QHBoxLayout, QVBoxLayout first. Then QGridLayout.
        - I may end up using QGridLayout the most, but want to get a feel
      for the layout systems.

    - Use QFormLayout for the DB editign form(s)

    - Use QButtonGroup to group buttons, especially radio buttons.

    - Don't know what I am doing wrong, but the layout containers never
      seem to work as I want them to. Going to 86 that for now and just go
      back to placing things in the main window manually using move() + math.
      Funny, this is exactly what I ended up doing with Tk too.

      AAND... as soon as I "let it go", I figured it out. See code in the
      Service Controllers widget set-up. I had to first create a "widget" to
      hold the layouts.

  - Get QtOpenGL (canvas) working.
    - Display a simple graph of the services or the data.
"""

import sys

from os import path
from pprint import pprint as pp     # noqa: F401

from PySide2.QtCore import QRect
# from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
# from PySide2.QtWidgets import QButtonGroup
from PySide2.QtWidgets import QCheckBox
from PySide2.QtWidgets import QGroupBox
# from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QMenuBar
from PySide2.QtWidgets import QOpenGLWidget
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QTextEdit
# from PySide2.QtWidgets import QVBoxLayout
# from PySide2.QtWidgets import QWidget
# from PySide2.QtWidgets import QSizePolicy
# from PySide2.QtWidgets import QSpacerItem
# from PySide2.QtWidgets import QToolBar
# from PySide2.QtWidgets import QToolButton
# Add radio buttons to select a database.
# from PySide2.QtGui import QPixmap
# from PySide2.QtWidgets import QFileDialog
# from PySide2.QtWidgets import QFormLayout
# from PySide2.QtWidgets import QHBoxLayout
# from PySide2.QtWidgets import QMenu <-- used for pop-up menus only
# from PySide2.QtWidgets import QPlainTextEdit
# from PySide2.QtWidgets import QStatusBar

from BowQuiver.saskan_fileio import FileIO      # type: ignore
from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.saskan_utils import Utils        # type: ignore
from controller_shell import ControllerShell    # type: ignore
from modes_toolbox import ModesToolbox          # type: ignore
from redis_io import RedisIO                    # type: ignore
from saskan_styles import SaskanStyles          # type: ignore
from service_controls_widget import ServiceControlsWidget   # type: ignore

CS = ControllerShell()
FI = FileIO()
RI = RedisIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class SaskanServices(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    N.B. The class inherits from QMainWindow.
    """

    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.initialize_UI()

    def initialize_UI(self):
        """Set window size and name. Show the window."""
        self.setGeometry(100, 100, 1200, 760)
        self.setWindowTitle(TX.tl.app)
        self.setStyleSheet(SS.get_style('base'))
        self.setFont(QFont('Arial', 16))
        self.APP = path.join(UT.get_home(), 'saskan')
        self.RES = path.join(self.APP, 'res')
        self.LOG = path.join(self.APP, 'log')
        # ==============================================================
        self.create_queues()
        self.create_menus()
        self.create_statusbar()
        self.create_modes_tbx()
        self.create_service_controls()
        self.create_help_display()
        self.create_db_editor()
        self.create_canvas()
        self.show()

    # State Holders and Queues
    # ==============================================================
    def create_queues(self):
        """Define variables and other containers for preserving state."""
        self.is_active = {
            'controls_wdg': False}

    # Main Menu
    # ==============================================================
    def exit_app(self):
        """Slot for Exit action"""
        self.close()

    def show_about(self):
        """Display a message box."""
        msg = "Control, Monitor, Test and Edit the Saskan Services.\n\n" + \
            "Version: 0.0.1"
        mbox = QMessageBox()
        mbox.about(self, "About Saskan Eyes", msg)

    def show_about_qt(self):
        """Display a message box about Qt."""
        QMessageBox.aboutQt(self, "About Qt")

    def create_menus(self):
        """Define menu bar, menus, menu items (actions)."""
        mbar = QMenuBar(self)
        mbar.setGeometry(0, 0, 100, 25)
        mbar.setStyleSheet(SS.get_style('menu'))
        # File Menu
        menu_file = mbar.addMenu("File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.exit_app)
        menu_file.addAction(quit_action)
        mbar.addMenu(menu_file)
        # Help Menu
        menu_help = mbar.addMenu("Help")
        about_action = QAction("About Sasan Eyes", self)
        about_action.triggered.connect(self.show_about)
        menu_help.addAction(about_action)
        about_qt_action = QAction("About Qt", self)
        about_qt_action.triggered.connect(self.show_about_qt)
        menu_help.addAction(about_qt_action)
        mbar.addMenu(menu_help)

    # Statusbar
    # ==============================================================
    def create_statusbar(self):
        """Initialize status bar."""
        self.statusBar().showMessage(TX.tl.app)

    # Generic / Shared Actions
    # ==============================================================
    def show_button_status(self, p_text: str):
        """Display status bar text relevant to a button or tool click.

        Ignore if no text passed in or status bar does not exist.
        """
        if p_text not in (None, ""):
            try:
                self.statusBar().showMessage(p_text)
            except AttributeError:
                pass

    # Modes Toolbar and Actions
    # ==============================================================
    def show_log_display_title(self, p_text: str):
        """Display title for log display relevant to mode.

        Ignore if no text passed in or log display title widget does not exist.
        """
        if p_text not in (None, ""):
            try:
                self.log_display_title.setText(p_text)
            except AttributeError:
                pass

    def deactivate_all_buttons(self):
        """Deactivate all tools and buttons.
        Update later to handle log-display and db-editor buttons.
        # Unlikely we'd ever want to disable Modes tools, right?
        for key in self.tbx_modes.keys():
            if self.tbx_modes[key]["active"] is True:
                self.tbx_modes[key]["active"] = False
                self.tbx_modes[key]["widget"].setStyleSheet(
                    SS.get_style('inactive_tool'))
        """
        print("DEBUG: deactivate_all_buttons()")

    def activate_mode_buttons(self, p_mode: str):
        """Activate log-display and db-editor buttons relevant to mode."""
        print(f"DEBUG: activate_mode_buttons({p_mode})")

    def mode_state_actions(self, p_mode: str):
        """Do common functions for mode-change tools.

        Execute only if the mode tool is in an active state.
        """
        mode_act = self.tbx_modes.acts[p_mode]
        if mode_act["active"]:
            self.show_button_status(mode_act["caption"])
            self.show_log_display_title(mode_act["title"])
            self.deactivate_all_buttons()
            self.activate_mode_buttons(p_mode)

    def monitor_actions(self):
        """Slot for Monitor action"""
        self.mode_state_actions("Monitor")

    def edit_db_actions(self):
        """Slot for Edit Database action.
        Show DB editor help page.
        """
        self.mode_state_actions("Edit DB")
        if self.tbx_modes.acts["Edit DB"]["active"]:
            html_path = path.join(self.RES, "redis_help.html")
            ok, msg, _ = FI.get_file(html_path)
            if ok:
                try:
                    self.help_display.setUrl(f"file://{html_path}")
                except AttributeError:
                    pass
            else:
                pp((msg, html_path))

    def create_modes_tbx(self):
        """Create mode toolbar and assign its actions.

        A movable toolbox can go anywhere on the screen,
        including off the app window. If no move is done
        then the widget defaults to upper-left corner of
        its layout box.

        Now that I have a better sense of how layouts work,
        may want to try containing the toolbox, or even the
        entire app, in a layout.

        But don't worry about it too much. Putting each major
        section in its own widget, which can be shown/hidden,
        is a great next step.

        Probably don't want to make the toolbox movable tho'.
        """
        self.tbx_modes = ModesToolbox(self)
        acts = {"Control": self.controls_mode_action,
                "Monitor": self.monitor_actions,
                "Edit DB": self.edit_db_actions}
        for key, act in acts.items():
            self.tbx_modes.acts[key]["widget"].triggered.connect(act)
        self.tbx_modes.move(975, 0)   # <-- move to upper-right corner
        # self.tbx_modes.move(0, 50)  # <-- move to just below menu

    # Service Controls Display and Actions
    # ==============================================================
    # Start with a small prototype just to see if different displays
    # can be managed OK for controls, monitors, and tests.
    def controls_mode_action(self):
        """Slot for Controls Mode tool action"""
        self.mode_state_actions("Control")
        try:
            if self.is_active['controls_wdg'] is False:
                self.service_controls.show()
                self.is_active['controls_wdg'] = True
            else:
                self.service_controls.hide()
                self.is_active['controls_wdg'] = False
        except AttributeError:
            pass

    def start_services(self):
        """Slot for Start action"""
        self.show_button_status("ed_btn", "Control", "start")
        btn = self.editor_actions["Control"]["start"]
        if btn["a"]:
            msg = """
        Services must be started using shell script.
        Example:
            $ bash ../admin/controller.sh --run redis
            """
            self.editor_display.setText(msg)

    def stop_services(self):
        """Slot for Stop action"""
        self.show_button_status("ed_btn", "Control", "stop")
        btn = self.editor_actions["Control"]["stop"]
        if btn["a"]:
            status, msg = CS.stop_running_services(p_service_nm='redis')
            self.editor_display.setText(msg)

    def show_services(self):
        """Slot for Show Services action"""
        self.show_button_status("ed_btn", "Control", "show")
        btn = self.editor_actions["Control"]["show"]
        if btn["a"]:
            status, msg = CS.check_running_services(p_service_nm='redis')
            self.editor_display.setText(msg)

    def test_services(self):
        """Slot for Test Services action"""
        self.show_button_status("ed_btn", "Control", "test")
        btn = self.editor_actions["Control"]["test"]
        if btn["a"]:
            pass

    def create_service_controls(self):
        """Create the Service Controls widget."""
        self.service_controls = ServiceControlsWidget(self)
        for key, act in {
                "Start": self.start_services,
                "Stop": self.stop_services,
                "Show": self.show_services,
                "Test": self.test_services}.items():
            self.service_controls.control_actions[key]["widget"].clicked.connect(act)   # noqa: E501
        self.service_controls.hide()

    def create_service_monitors(self):
        """All or part of this may become a Class.
        Define/Enable the display-frame for monitor functions.
        Define the buttons and actions for:
        - Monitor: Refresh Log, Loads, Fails, Recent, Summary
        """
        pass
        """
                "top": {
                    "t": "Top",
                    "p": "Scrolling to top",
                    "a": False,
                    "s": self.scroll_to_top},
                "tail": {
                    "t": "Tail",
                    "p": "Scrolling to bottom",
                    "a": False,
                    "s": self.scroll_to_bottom},
                "log": {
                    "t": "Log",
                    "p": "Refreshing full log",
                    "a": False,
                    "s": self.show_full_log},
                "requests": {
                    "t": "Requests",
                    "p": "Showing pending requests",
                    "a": False,
                    "s": self.show_requests},
                "failures": {
                    "t": "Failures",
                    "p": "Showing failed requests",
                    "a": False,
                    "s": self.show_failures},
                "pressure": {
                    "t": "Pressure",
                    "p": "Showings loads on services",
                    "a": False,
                    "s": self.show_pressure}},
        """
    # Help (Web pages) Display
    # ==============================================================
    def show_help_page(self, p_html_file_nm: str):
        """Refresh the help page display.

        Content in help-display are URL-loaded HTML files.
        - Published to home/saskan/res
        - Edited, versioned in git repo under app's /html sub-dir

        :Args:
            - p_html_file_nm: str -> name of html file to display
        """
        html_path = path.join(self.RES, p_html_file_nm)
        ok, msg, _ = FI.get_file(html_path)
        print(msg, html_path)
        if ok:
            self.help.setUrl(f"file://{html_path}")

    def create_help_display(self):
        """Define help display and related actions as needed.

        QSS StyleSheet seems to have no effect on this widget.
        """
        self.help = QWebEngineView(self)
        self.help.setGeometry(QRect(0, 0, 600, 250))
        self.help.move(30, 475)
        self.show_help_page("saskan_help.html")

    # Database Editor and Actions
    # ==============================================================
    def create_db_editor(self):
        """All or part of this may become a Class.
        Define the display-frame for DB edit forms functions.
        Define queues and other infrastructure to support editing.
        Define the buttons, check-boxes, text inputs and actions for:
        - Select DB: Sandbox, Schema, Harvest, Log, Monitor
        - Select Record: All, Primitives, Topics, Plans, Services,
            Schema, Requests, Responses
        - Select Rules: Expirations, Refresh-rate, Retry-rate,
            Retry-limit, Retry-delay
        - Edit DB: Add, Delete, Update, Find, Find Next, Find Prev,
            Replace, Undo, Redo, Save, Cancel
        """
        pass
        """
                "save": {
                    "t": "Save",
                    "p": "Save current state",
                    "c": "Ctrl+S",
                    "a": False,
                    "s": self.save_state,
                    "w": None},
                "add": {
                    "t": "Add",
                    "p": "Insert a new record to the database",
                    "c": "Ctrl+N",
                    "a": False,
                    "s": self.add_item,
                    "w": None},
                "del": {
                    "t": "Delete",
                    "p": "Delete the current record from the database",
                    "c": "Ctrl+X",
                    "a": False,
                    "s": self.remove_item,
                    "w": None},
                "undo": {
                    "t": "Undo",
                    "p": "Reverse previous action",
                    "c": "Ctrl+Z",
                    "a": False,
                    "s": self.undo_item,
                    "w": None}},

            "Edit": {
                "find": {
                    "t": "Find -->",
                    "p": "Find items in Schema DB",
                    "a": False,
                    "s": self.find_record},
                "summary": {
                    "t": "Summary",
                    "p": "Show stats for Redis Databases",
                    "a": False,
                    "s": self.summarize_dbs},
                "select": {
                    "t": "Select -->",
                    "p": "Select Schema DB items",
                    "a": False,
                    "s": self.select_database_items}},
            "Select": {
                "topics": {
                    "t": "Topics",
                    "p": "Select topics in Schema DB",
                    "a": False,
                    "s": self.select_topics},
                "plans": {
                    "t": "Plans",
                    "p": "Select plans in Schema DB",
                    "a": False,
                    "s": self.select_plans},
                "services": {
                    "t": "Services",
                    "p": "Select services in Schema DB",
                    "a": False,
                    "s": self.select_services},
                "schemas": {
                    "t": "Schemas",
                    "p": "Select schemas in Schema DB",
                    "a": False,
                    "s": self.select_schemas},
                "primitives": {
                    "t": "Primitives",
                    "p": "Select prims in Schema DB",
                    "a": False,
                    "s": self.select_primitives}}}
        """

    def create_db_selectors(self):
        """Wrap up everything in tidy boxes.
        """
        # QGroupBox is SPECIFICALLY for a set of checkboxes.
        # Not a generic grouping box.
        # Maybe use it for the db-select checkboxes.
        grp_box_left = QGroupBox(self)
        self.addWidget(grp_box_left)
        grp_box_left.setFixedHeight(60000)
        grp_box_left.setFixedWidth(200)
        for lbl_no in range(5):
            lbl = QLabel(f"Test {lbl_no}", self)
            lbl.setStyleSheet(SS.get_style('info'))
            lbl.setFont(QFont('Arial', 16))
            grp_box_left.addWidget(lbl)

    # Canvas Display
    # ==============================================================
    def create_canvas(self):
        """All or part of this may become a Class.
        Define the OpenGL Canvas functions.
        """
        pass

    # Generic Helper Actions (old, maybe obsolete)
    # ==============================================================
    def activate_editor_buttons(self, p_catg: str):
        """Activate editor buttons for category p_catg.
        """
        for key in self.editor_actions[p_catg].keys():
            self.editor_actions[p_catg][key]["a"] = True
            self.ed_btn[key].setStyleSheet(SS.get_style('active_button'))

    def deactivate_db_edit_buttons(self):
        """Deactivate tool and editor widgets related to DB editing."""
        for key in self.tool_actions["Edit"].keys():
            self.tool_actions["Edit"][key]["a"] = False
            self.tb_btn[key].setStyleSheet(SS.get_style('inactive_tool'))
        for key in self.editor_actions["Edit"].keys():
            self.editor_actions["Edit"][key]["a"] = False
            self.ed_btn[key].setStyleSheet(SS.get_style('inactive_button'))
        for key in self.editor_actions["Select"].keys():
            self.editor_actions["Select"][key]["a"] = False
            self.ed_chk[key].setStyleSheet(SS.get_style('inactive_checkbox'))
        self.ed_find.setStyleSheet(SS.get_style('inactive_editor'))
        self.ed_find.setText("")
        self.ed_find.setReadOnly(True)

    def activate_db_edit_buttons(self):
        """Activate tool and editor widgets related to DB editing.

        @DEV:
        - Queues, state engines:
            - DB-Edit-Tool-Is-Active
            - DB-Edit-Tool-Is-Inactive
            - IO-Action-Is-Pending
            - IO-Actions-Completed-Queue
            - Record-Is-Selected
            - No-Record-Is-Selected

        - For any given IO action that causes a change, the reverse action
          needs to be defined

        - Save, Add, Delete, Undo active when DB-Edit tool is active, and...
        - Save -> active when a 'dirty' (non saved) IO action pending
        - Add -> active when a single Select checkbox is toggled on
        - Delete -> active when one Select checkbox is toggled on and
                    a single record has been selected
        - Undo -> becomes "Cancel" when a 'dirty' (non saved) IO action pending
        - Undo -> active when at least one completed item on IO queue.
        """
        for key in self.tool_actions["Edit"].keys():
            self.tool_actions["Edit"][key]["a"] = True
            self.tb_btn[key].setStyleSheet(SS.get_style('active_tool'))
        for key in self.editor_actions["Edit"].keys():
            self.editor_actions["Edit"][key]["a"] = True
            self.ed_btn[key].setStyleSheet(SS.get_style('active_button'))
        for key in self.editor_actions["Select"].keys():
            self.editor_actions["Select"][key]["a"] = True
            self.ed_chk[key].setStyleSheet(SS.get_style('active_checkbox'))
        self.ed_find.setStyleSheet(SS.get_style('active_editor'))
        self.ed_find.setText("")
        self.ed_find.setReadOnly(False)

    def handle_selects(self, p_key: str):
        """Handle selected record types"""
        btn = self.editor_actions["Select"][p_key]
        if btn["a"]:
            self.status_bar.setText("")
            if self.ed_chk[p_key].isChecked():
                self.status_bar.setText(btn["p"])

    # Various Actions (old, maybe obsolete)
    # ==============================================================

    def test_request(self):
        """Slot for Test action"""
        self.show_button_status("tb_btn", "Window", "test")
        self.editor_title.setText("Service Requests Tester")
        self.deactivate_db_edit_buttons()
        self.deactivate_editor_buttons()

    def save_state(self):
        """Slot for Save action"""
        self.show_button_status("tb_btn", "Edit", "save")

    def add_item(self):
        """Slot for Add action"""
        self.show_button_status("tb_btn", "Edit", "add")

    def remove_item(self):
        """Slot for Remove action"""
        self.show_button_status("tb_btn", "Edit", "del")

    def undo_item(self):
        """Slot for Undo action"""
        self.show_button_status("tb_btn", "Edit", "undo")

    def help_me(self):
        """Slot for Help action"""
        self.show_button_status("tb_btn", "Help", "help")

    # Editor Button Actions
    # ==============================================================
    def scroll_to_top(self):
        """Slot for Top action"""
        self.show_button_status("ed_btn", "Monitor", "top")

    def scroll_to_bottom(self):
        """Slot for Tail action"""
        self.show_button_status("ed_btn", "Monitor", "tail")

    def show_full_log(self):
        """Slot for Log action"""
        self.show_button_status("ed_btn", "Monitor", "log")

    def show_failures(self):
        """Slot for Failures action"""
        self.show_button_status("ed_btn", "Monitor", "failures")

    def show_requests(self):
        """Slot for Requests action"""
        self.show_button_status("ed_btn", "Monitor", "requests")

    def show_pressure(self):
        """Slot for Pressure action"""
        self.show_button_status("ed_btn", "Monitor", "pressure")

    def find_record(self):
        """Slot for Find Record action"""
        self.show_button_status("ed_btn", "Edit", "find")

    def summarize_dbs(self):
        """Slot for Summarize DBs action"""
        self.show_button_status("ed_btn", "Edit", "summary")
        dbs = RI.list_all_dbs()
        self.editor_display.setText(str(dbs))

    def select_database_items(self):
        """Slot for List Items action"""
        self.show_button_status("ed_btn", "Edit", "select")

    def select_topics(self):
        """Slot for List Topics action"""
        self.handle_selects("topics")

    def select_plans(self):
        """Slot for List Plans action"""
        self.handle_selects("plans")

    def select_services(self):
        """Slot for List Services action"""
        self.handle_selects("services")

    def select_schemas(self):
        """Slot for List Schemas action"""
        self.handle_selects("schemas")

    def select_primitives(self):
        """Slot for List Primitives action"""
        self.handle_selects("primitives")

    # Define Actions
    # ==============================================================
    def create_tool_actions(self):
        """Define actions triggered by menu items and toolbar buttons."""
        # Add these texts to saskan_texts.
        # Design icons for these actions.
        self.tool_actions = {
            "Window": {
                "ctl": {
                    "t": "Control",
                    "p": "Start, stop, manage services",
                    "c": "Ctrl+Alt+C",
                    "a": True,
                    "s": self.control_services,
                    "w": None},
                "mon": {
                    "t": "Monitor",
                    "p": "Monitor running services",
                    "c": "Ctrl+Alt+M",
                    "a": True,
                    "s": self.monitor_services,
                    "w": None},
                "database": {
                    "t": "DB",
                    "p": "Edit the services database",
                    "c": "Ctrl+Alt+S",
                    "a": True,
                    "s": self.edit_database,
                    "w": None},
                "test": {
                    "t": "Test",
                    "p": "Test service requests",
                    "c": "Ctrl+Alt+U",
                    "a": True,
                    "s": self.test_request,
                    "w": None}},
            "Edit": {
                "save": {
                    "t": "Save",
                    "p": "Save current state",
                    "c": "Ctrl+S",
                    "a": False,
                    "s": self.save_state,
                    "w": None},
                "add": {
                    "t": "Add",
                    "p": "Insert a new record to the database",
                    "c": "Ctrl+N",
                    "a": False,
                    "s": self.add_item,
                    "w": None},
                "del": {
                    "t": "Delete",
                    "p": "Delete the current record from the database",
                    "c": "Ctrl+X",
                    "a": False,
                    "s": self.remove_item,
                    "w": None},
                "undo": {
                    "t": "Undo",
                    "p": "Reverse previous action",
                    "c": "Ctrl+Z",
                    "a": False,
                    "s": self.undo_item,
                    "w": None}},
            "Help": {
                "help": {
                    "t": "Help",
                    "p": "Get help",
                    "c": "Ctrl+H",
                    "a": True,
                    "s": self.help_me,
                    "w": None},
                "exit": {
                    "t": "Exit",
                    "p": "Quit the application",
                    "c": "Ctrl+Q",
                    "a": True,
                    "s": self.exit_app,
                    "w": None}}}
        for catg, actions in self.tool_actions.items():
            for key, obj in actions.items():
                self.tool_actions[catg][key]["w"] = \
                    QAction(QIcon('images/favicon.jpg'), obj["t"], self)
                self.tool_actions[catg][key]["w"].setToolTip(obj["p"])
                self.tool_actions[catg][key]["w"].setShortcut(obj["c"])
                self.tool_actions[catg][key]["w"].triggered.connect(obj["s"])

    def create_editor_actions(self):
        """Define actions. Triggered by editor buttons."""
        # Add these texts to saskan_texts.
        # Include icons for these actions.
        self.editor_actions = {
            "Control": {
                "start": {
                    "t": "Start",
                    "p": "Starting up services",
                    "a": False,
                    "s": self.start_services},
                "stop": {
                    "t": "Stop",
                    "p": "Stopping all services",
                    "a": False,
                    "s": self.stop_services},
                "show": {
                    "t": "Show",
                    "p": "Showing services status",
                    "a": False,
                    "s": self.show_services},
                },
            "Monitor": {
                "top": {
                    "t": "Top",
                    "p": "Scrolling to top",
                    "a": False,
                    "s": self.scroll_to_top},
                "tail": {
                    "t": "Tail",
                    "p": "Scrolling to bottom",
                    "a": False,
                    "s": self.scroll_to_bottom},
                "log": {
                    "t": "Log",
                    "p": "Refreshing full log",
                    "a": False,
                    "s": self.show_full_log},
                "requests": {
                    "t": "Requests",
                    "p": "Showing pending requests",
                    "a": False,
                    "s": self.show_requests},
                "failures": {
                    "t": "Failures",
                    "p": "Showing failed requests",
                    "a": False,
                    "s": self.show_failures},
                "pressure": {
                    "t": "Pressure",
                    "p": "Showings loads on services",
                    "a": False,
                    "s": self.show_pressure}},
            "Edit": {
                "find": {
                    "t": "Find -->",
                    "p": "Find items in Schema DB",
                    "a": False,
                    "s": self.find_record},
                "summary": {
                    "t": "Summary",
                    "p": "Show stats for Redis Databases",
                    "a": False,
                    "s": self.summarize_dbs},
                "select": {
                    "t": "Select -->",
                    "p": "Select Schema DB items",
                    "a": False,
                    "s": self.select_database_items}},
            "Select": {
                "topics": {
                    "t": "Topics",
                    "p": "Select topics in Schema DB",
                    "a": False,
                    "s": self.select_topics},
                "plans": {
                    "t": "Plans",
                    "p": "Select plans in Schema DB",
                    "a": False,
                    "s": self.select_plans},
                "services": {
                    "t": "Services",
                    "p": "Select services in Schema DB",
                    "a": False,
                    "s": self.select_services},
                "schemas": {
                    "t": "Schemas",
                    "p": "Select schemas in Schema DB",
                    "a": False,
                    "s": self.select_schemas},
                "primitives": {
                    "t": "Primitives",
                    "p": "Select prims in Schema DB",
                    "a": False,
                    "s": self.select_primitives}}}

    def create_editor_title(self):
        """Define area for display identifying current editor mode."""
        self.editor_title = QLabel(self)
        self.editor_title.setFont(QFont('Arial', 18))
        self.editor_title.setStyleSheet(SS.get_style('status'))
        self.editor_title.setGeometry(QRect(0, 0, 275, 60))
        self.editor_title.move(10, 10)

    def create_editor(self):
        """Define area for display of Schema Editor, Monitor Display
        and Control Forms."""
        self.editor_display = QTextEdit(self)
        self.editor_display.setGeometry(QRect(0, 0, 825, 300))
        self.editor_display.setStyleSheet(SS.get_style('editor'))
        self.editor_display.setReadOnly(True)
        self.editor_display.move(10, 60)

    def create_ed_mon_ctl_buttons(self):
        """Define buttons related to the editor
        monitor and control functions."""
        self.ed_btn = dict()
        col = 35
        for catg in ["Control", "Monitor"]:
            for key, obj in self.editor_actions[catg].items():
                self.ed_btn[key] = QPushButton(obj["t"], self)
                self.ed_btn[key].setGeometry(QRect(0, 0, 85, 40))
                self.ed_btn[key].setStyleSheet(SS.get_style('inactive_button'))
                self.ed_btn[key].clicked.connect(obj["s"])
                self.ed_btn[key].move(col, 360)
                col += self.ed_btn[key].width() + 3

    def create_ed_db_widgets(self):
        """Define buttons and inputs related to editor functions
        for summarizing and selecting a database."""
        pass

    def create_ed_edit_widgets(self):
        """Define buttons and inputs related to the editor
        edit functions."""
        self.ed_chk = dict()
        col = 35
        for key, obj in self.editor_actions["Edit"].items():
            if key != "find":
                self.ed_btn[key] = QPushButton(obj["t"], self)
                self.ed_btn[key].setGeometry(QRect(0, 0, 115, 40))
                self.ed_btn[key].setStyleSheet(SS.get_style('inactive_button'))
                self.ed_btn[key].clicked.connect(obj["s"])
                self.ed_btn[key].move(col, 395)
                col += self.ed_btn[key].width() + 3
        col -= 6
        for key, obj in self.editor_actions["Select"].items():
            self.ed_chk[key] = QCheckBox(obj["t"], self)
            self.ed_chk[key].setGeometry(QRect(0, 0, 110, 30))
            self.ed_chk[key].setStyleSheet(SS.get_style('inactive_checkbox'))
            self.ed_chk[key].clicked.connect(obj["s"])
            self.ed_chk[key].move(col, 400)
            col += self.ed_chk[key].width()

    def create_ed_find_widgets(self):
        """Define buttons and inputs related to the editor
        find functions."""
        col = 35
        obj = self.editor_actions["Edit"]["find"]
        self.ed_btn["find"] = QPushButton(obj["t"], self)
        self.ed_btn["find"].setGeometry(QRect(0, 0, 115, 40))
        self.ed_btn["find"].setStyleSheet(SS.get_style('inactive_button'))
        self.ed_btn["find"].clicked.connect(obj["s"])
        self.ed_btn["find"].move(col, 430)
        self.ed_find = QLineEdit(self)
        self.ed_find.setGeometry(QRect(0, 0, 120, 30))
        self.ed_find.setStyleSheet(SS.get_style('inactive_editor'))
        self.ed_find.setReadOnly(True)
        self.ed_find.move(col + self.ed_btn["find"].width() - 3, 435)

    def create_opengl_display(self):
        """Define a canvas area.

        May want to keep this.
        Would like to show relationships of selected record(s).
        But for now, it is not used.
        More needed first...
        @DEV:
        - Add a frame for editing the active record.
        - It will be more like a form.
        - Keep the current "editor" text display but shrink it.
        - Consider some better language than just "editor".
        - Move the add/delete/undo buttons to the editor space.
        - Add a selector for what database to use.
        - Add a selector for editing the expiration rule on a DB.
        - Include rules for what selectors are available on what DBs.
        """
        self.canvas = QOpenGLWidget(self)
        self.canvas.setGeometry(QRect(0, 0, 150, 400))
        self.canvas.initializeGL()
        self.canvas.setStyleSheet(SS.get_style('canvas'))
        self.canvas.move(850, 80)

    def create_status_bar(self):
        """Define status bar display area.
        @DEV:
        - Try using the built-in status bar.
        """
        self.status_bar = QLineEdit(self)
        self.status_bar.setGeometry(QRect(0, 0, 850, 30))
        self.status_bar.setStyleSheet(SS.get_style('status'))
        self.status_bar.setReadOnly(True)
        self.status_bar.setAlignment(Qt.AlignHCenter)
        self.status_bar.setFrame(True)
        self.status_bar.setText("Ready Player One")
        self.status_bar.move(0, 720)


# Run program
if __name__ == '__main__':
    """Instantiate the app and start the event loop.
    """
    app = QApplication(sys.argv)
    # The class object has the .show() command in it:
    SRV = SaskanServices()
    sys.exit(app.exec_())
