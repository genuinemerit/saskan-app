#!/usr/bin/python3.9
"""
:module:    saskan_eyes.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI.
"""

import sys

from os import path
from pprint import pprint as pp     # noqa: F401

from PySide2.QtGui import QFont
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QMenuBar

from BowQuiver.saskan_fileio import FileIO      # type: ignore
from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.saskan_utils import Utils        # type: ignore
from redis_io import RedisIO                    # type: ignore
from se_controls_shell import ControlsShell     # type: ignore
from se_controls_wdg import ControlsWidget      # type: ignore
from se_dbeditor_wdg import DBEditorWidget      # type: ignore
from se_diagram_wdg import DiagramWidget        # type: ignore
from se_help_wdg import HelpWidget              # type: ignore
from se_modes_tbx import ModesToolbox           # type: ignore
from se_monitor_wdg import MonitorWidget        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

CS = ControlsShell()
FI = FileIO()
RI = RedisIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class SaskanServices(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    May add other stuff later, like a Schema Editor and DB generator.
    """

    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.initialize_UI()

    def initialize_UI(self):
        """Set window size and name. Show the window."""
        self.setGeometry(100, 100, 1200, 860)
        self.setWindowTitle(TX.tl.app)
        self.setStyleSheet(SS.get_style('base'))
        self.setFont(QFont('Arial', 16))
        # ==============================================================
        self.define_data()
        self.create_menus()
        self.create_statusbar()
        self.create_modes_toolbox()
        self.create_controls()
        self.create_monitor()
        self.create_db_editor()
        self.create_help()
        self.create_diagram()
        # ==============================================================
        self.show()   # <== main window

    # Constants, flags/state holders, and queues
    # ==============================================================
    def define_data(self):
        """Define variables, containers for preserving state."""
        self.APP = path.join(UT.get_home(), 'saskan')
        self.RES = path.join(self.APP, 'res')
        self.LOG = path.join(self.APP, 'log')
        self.is_active = {
            'controls_wdg': False,
            'monitor_wdg': False,
            'dbeditor_wdg': False,
            'help_wdg': False,
            'diagram_wdg': False}

    # Main Menu
    # ==============================================================
    def exit_main(self):
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
        quit_action.triggered.connect(self.exit_main)
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
        """Initialize status bar associated with QMainWindow."""
        self.statusBar().showMessage(TX.tl.app)

    # Generic / Helper Actions
    # ==============================================================
    def show_status(self, p_text: str):
        """Display status bar text relevant to some event like a
        button or tool click.

        Ignore if no text passed in or status bar does not exist.
        """
        if p_text not in (None, ""):
            try:
                self.statusBar().showMessage(p_text)
            except AttributeError:
                pass

    # Modes Toolbox
    # ==============================================================
    def create_modes_toolbox(self):
        """Create mode toolbar and assign its actions.
        """
        self.tbx_modes = ModesToolbox(self)
        acts = {"Control": self.controls_mode_action,
                "Monitor": self.monitor_mode_action,
                "Edit DB": self.db_editor_mode_action,
                "Help": self.help_mode_action}
        for key, act in acts.items():
            self.tbx_modes.acts[key]["widget"].triggered.connect(act)
        self.tbx_modes.move(935, 0)   # <-- move it to upper-right corner

    # Service Controls Display and Actions
    # ==============================================================
    def controls_mode_action(self):
        """Slot for Controls Mode tool click action"""
        btn = self.tbx_modes.acts["Control"]
        if btn["active"]:
            self.show_status(btn["caption"])
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
        """Slot for Start Services action"""
        btn = self.service_controls.acts["Start"]
        if btn["active"]:
            self.show_status(btn["caption"])
            status, msg = CS.start_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def stop_services(self):
        """Slot for Stop Services action"""
        btn = self.service_controls.acts["Stop"]
        if btn["active"]:
            self.show_status(btn["caption"])
            status, msg = CS.stop_running_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def show_services(self):
        """Slot for Show Services action"""
        btn = self.service_controls.acts["Show"]
        if btn["active"]:
            self.show_status(btn["caption"])
            status, msg = CS.check_running_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def test_services(self):
        """Slot for Test Services action"""
        btn = self.service_controls.acts["Test"]
        if btn["active"]:
            self.show_status(btn["caption"])
            msg = """
        This will run pre-defined tests on the services.
            """
            self.service_controls.ctl_display.setText(msg)

    def create_controls(self):
        """Create the Service Controls widget."""
        self.service_controls = ControlsWidget(self)
        for key, act in {
                "Start": self.start_services,
                "Stop": self.stop_services,
                "Show": self.show_services,
                "Test": self.test_services}.items():
            self.service_controls.acts[key]["widget"].clicked.connect(act)
        self.service_controls.hide()

    # Service Monitor Display and Actions
    # ==============================================================
    def monitor_mode_action(self):
        """Slot for Services Monitor mode tool click action"""
        btn = self.tbx_modes.acts["Monitor"]
        if btn["active"]:
            self.show_status(btn["caption"])
            try:
                if self.is_active['monitor_wdg'] is False:
                    self.service_monitor.show()
                    self.is_active['monitor_wdg'] = True
                else:
                    self.service_monitor.hide()
                    self.is_active['monitor_wdg'] = False
            except AttributeError:
                pass

    def mon_summary(self):
        """Slot for Monitor Summary button click action"""
        btn = self.service_monitor.acts["Summary"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_top(self):
        """Slot for Monitor Top button click action"""
        btn = self.service_monitor.acts["Top"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_tail(self):
        """Slot for Monitor Tail button click action"""
        btn = self.service_monitor.acts["Tail"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_full(self):
        """Slot for Monitor Full button click action"""
        btn = self.service_monitor.acts["Full"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_requests(self):
        """Slot for Monitor Requests button click action"""
        btn = self.service_monitor.acts["Requests"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_fails(self):
        """Slot for Monitor Fails button click action"""
        btn = self.service_monitor.acts["Fails"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def mon_pressure(self):
        """Slot for Monitor Pressure button click action"""
        btn = self.service_monitor.acts["Pressure"]
        if btn["active"]:
            self.show_status(btn["caption"])

    def create_monitor(self):
        """Create the Service Monitor widget.
        """
        self.service_monitor = MonitorWidget(self)
        for key, act in {
                "Summary": self.mon_summary,
                "Top": self.mon_top,
                "Tail": self.mon_tail,
                "Full": self.mon_full,
                "Requests": self.mon_requests,
                "Fails": self.mon_fails,
                "Pressure": self.mon_pressure}.items():
            self.service_monitor.acts[key]["widget"].clicked.connect(act)
        self.service_monitor.hide()

    # Database Editor and Actions
    # ==============================================================
    def db_editor_mode_action(self):
        """Slot for Edit Database modes tool click action.
        Show DB editor help page.
        """
        btn = self.tbx_modes.acts["Edit DB"]
        if btn["active"]:
            self.show_status(btn["caption"])
            try:
                if self.is_active['dbeditor_wdg'] is False:
                    self.db_editor.show()
                    self.is_active['dbeditor_wdg'] = True
                    self.help.set_content("db_help.html")
                    self.show_diagram()
                else:
                    self.db_editor.hide()
                    self.is_active['dbeditor_wdg'] = False
                    self.hide_diagram()
            except AttributeError:
                pass

    def deactivate_texts(self, p_inp_nm: list):
        """Generic function to deactivate a text input widget."""
        for inp_nm in p_inp_nm:
            inp = self.db_editor.texts[inp_nm]
            inp["widget"].setStyleSheet(SS.get_style("inactive_editor"))
            inp["widget"].setEnabled(False)
            inp["active"] = False

    def deactivate_buttons(self, p_btn_nm: list):
        """Generic function to deactivate a push button"""
        for btn_nm in p_btn_nm:
            btn = self.db_editor.acts[btn_nm]
            btn["widget"].setStyleSheet(SS.get_style("inactive_button"))
            btn["widget"].setEnabled(False)
            btn["active"] = False

    def deactivate_edit_form(self, p_rec: str = None):
        """Deactivate the Edit Form widget."""
        for key, form in self.db_editor.forms.items():
            if (p_rec is None or key != p_rec) and form["active"]:
                form["widget"].hide()
                form["active"] = False
                self.deactivate_buttons(["Cancel", "Get", "Next", "Prev"])
                self.deactivate_texts(["Key", "Cursor"])
                break

    def activate_texts(self, p_inp_nm: list):
        """Generic function to activate a text input widget."""
        for inp_nm in p_inp_nm:
            inp = self.db_editor.texts[inp_nm]
            inp["widget"].setStyleSheet(SS.get_style("active_editor"))
            inp["widget"].setEnabled(True)
            inp["active"] = True

    def activate_buttons(self, p_btn_nm: list):
        """Generic function to activate a push button"""
        for btn_nm in p_btn_nm:
            btn = self.db_editor.acts[btn_nm]
            btn["widget"].setStyleSheet(SS.get_style("active_button"))
            btn["widget"].setEnabled(True)
            btn["active"] = True

    def activate_edit_form(self, p_rec: str):
        """Generic functions when enabling a different edit form.
        """
        self.deactivate_edit_form((p_rec))
        if self.db_editor.forms[p_rec]["active"] is not True:
            self.show_status(
                self.db_editor.selects[p_rec]["caption"])
            try:
                self.db_editor.forms[p_rec]["widget"].show()
                self.db_editor.forms[p_rec]["active"] = True
                self.activate_buttons(["Cancel", "Get"])
                self.activate_texts(["Key", "Cursor"])
            except AttributeError:
                pass

    def push_cancel_btn(self):
        """Slot for Editor Edit Push Button --> Cancel"""
        btn = self.db_editor.acts["Cancel"]
        if btn["active"]:
            self.show_status(btn["caption"])
            self.deactivate_edit_form()

    def push_get_btn(self):
        """Slot for Editor Edit Push Button --> Get"""
        btn = self.db_editor.acts["Get"]
        if btn["active"]:
            self.show_status(btn["caption"])
            # Which record type is selected? --> what DB to search?
            # Is a specific key or wildcard key being requested?
            # Call redis_io for the query
            # If multiple records returned,
            #  show the first one
            #  activate the Next and Prev buttons
            #  display the cursor count and position
            # If no records returned,
            #  display a message

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        rec = "Configs"
        self.activate_edit_form(rec)

    def select_state_flags(self):
        """Slot for Editor Select State Flags radio check action"""
        rec = "States"
        self.activate_edit_form(rec)

    def create_db_editor(self):
        """All or part of this may become a Class.
        Define the display-frame for DB edit forms functions.
        Define queues, buttons to support editing.
        """
        self.db_editor = DBEditorWidget(self)
        # Editor Select radio buttons:
        for key, act in {
                "Configs": self.select_configs,
                "States": self.select_state_flags}.items():
            self.db_editor.selects[key]["widget"].clicked.connect(act)
        # Editor Find and Edit push buttons:
        for key, act in {
                "Cancel": self.push_cancel_btn,
                "Get": self.push_get_btn}.items():
            self.db_editor.acts[key]["widget"].clicked.connect(act)
        self.db_editor.hide()

    # Help (Web pages) Display
    # ==============================================================
    def help_mode_action(self):
        """Slot for Help Mode tool click action"""
        btn = self.tbx_modes.acts["Help"]
        self.show_status(btn["caption"])
        try:
            if self.is_active['help_wdg'] is False:
                self.help.set_content("saskan_help.html")
                self.help.show()
                self.is_active['help_wdg'] = True
            else:
                self.help.hide()
                self.is_active['help_wdg'] = False
        except AttributeError:
            pass

    def create_help(self):
        """Define help display.
        """
        self.help = HelpWidget(self)
        self.help.hide()

    # Diagram Display
    # ==============================================================
    def show_diagram(self):
        """Slot for Graph Diagram show action"""
        try:
            if self.is_active['diagram_wdg'] is False:
                try:
                    img = self.network.get_image_path()
                    with open(img):
                        self.diagram_wdg = QLabel(self)
                        self.diagram_wdg.setGeometry(625, 650, 550, 200)
                        pixmap = QPixmap(img)
                        self.diagram_wdg.setPixmap(pixmap)
                        self.diagram_wdg.setStyleSheet(SS.get_style("canvas"))
                        # self.diagram_wdg.move(625, 650)
                        self.diagram_wdg.show()
                        self.is_active['diagram_wdg'] = True
                except FileNotFoundError:
                    print("User image file not found:" + img)
        except AttributeError:
            pass

    def hide_diagram(self):
        """Slot for Graph Diagram hide action"""
        try:
            if self.is_active['diagram_wdg'] is True:
                self.diagram_wdg.hide()
                self.is_active['diagram_wdg'] = False
        except AttributeError:
            pass

    def create_diagram(self):
        """Generate a Graph Diagram.
        """
        self.network = DiagramWidget()
        # By default, creates a test diagram.
        # See DiagramWidget class method "set_content()" for more details.


# Run program
if __name__ == '__main__':
    """Instantiate the app and start the event loop.
    """
    app = QApplication(sys.argv)
    # The class object has the .show() command in it:
    SRV = SaskanServices()
    sys.exit(app.exec_())
