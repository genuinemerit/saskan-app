#!/usr/bin/python3.9
"""
:module:    saskan_eyes.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI.
"""
import argparse
import json
import sys

from pprint import pprint as pp     # noqa: F401

from PySide2.QtGui import QFont
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QMenuBar

from boot_texts import BootTexts  # type: ignore
from file_io import FileIO  # type: ignore
from redis_io import RedisIO  # type: ignore
from se_controls_shell import ControlsShell     # type: ignore
from se_controls_wdg import ControlsWidget      # type: ignore
from se_dbeditor_wdg import DBEditorWidget      # type: ignore
from se_diagram_wdg import DiagramWidget        # type: ignore
from se_help_wdg import HelpWidget              # type: ignore
from se_menus_wdg import MenusWidget            # type: ignore
from se_modes_tbx import ModesToolbox           # type: ignore
from se_monitor_wdg import MonitorWidget        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore
from se_record_mgmt import RecordMgmt           # type: ignore

BT = BootTexts()
CS = ControlsShell()
FI = FileIO()
RI = RedisIO()
SS = SaskanStyles()


class SaskanEyes(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    May add other stuff later, like a Schema Editor and DB generator,
    link into the game itself, later on.
    """

    def __init__(self):
        """super() call is required."""
        super().__init__()
        self.initialize_CLI()
        self.TXT = self.load_meta("text")
        self.WDG = self.load_meta("widget")
        self.initialize_UI()

    # Command line option handlers
    # ==============================================================
    def initialize_CLI(self):
        """Handle command-line arguments."""
        parser = argparse.ArgumentParser(description=BT.txt.app_desc)
        parser.add_argument(
            '--force-refresh',
            action='store_true', help=BT.txt.refresh_desc)
        args = parser.parse_args()
        if args.force_refresh:
            self.refresh_configs()

    def refresh_configs(self):
        """Refresh Basement DB texts, configs from JSON config file"""

        def load_cfg_file(p_config_file_path: str):
            """Read data from config file."""
            ok, err, configs = FI.get_file(p_config_file_path)
            if not ok:
                print(err)
                exit(1)
            elif configs is None:
                print(f"{BT.txt.no_file}{p_config_file_path}")
                exit(1)
            config_data = json.loads(configs)
            return(config_data)

        def set_configs(p_config_data: dict,
                        p_catg: str):
            """Set basement db text and widget metadata records"""
            db = "basement"
            for k, values in p_config_data.items():
                key = RI.UT.clean_redis_key(f"{p_catg}:{k}")
                record = {"name": key} | values
                record, update = \
                    RI.set_audit_values(db, record, p_include_hash=True)
                key = record["name"]
                if update:
                    RI.do_update(db, record)
                else:
                    RI.do_insert(db, record)

        set_configs(load_cfg_file(BT.file_texts), "text")
        set_configs(load_cfg_file(BT.file_widgets), "widget")

    # Load and save texts and widget metadata
    # ==============================================================
    def load_meta(self, p_catg):
        """Load configuration data from db to memory."""
        db = "basement"
        keys: list = RI.find_keys(db, f"{p_catg}:*")
        data: dict = {}
        for k in keys:
            key = k.decode('utf-8').replace(f"{p_catg}:", "")
            record = RI.get_values(RI.get_record(db, k))
            data[key] = record
        return(data)

    def save_meta(self,
                  p_wdg_catg: str,
                  p_qt_wdg):
        """Update Basement DB with modified widget record"""
        db = "basement"
        self.WDG[p_wdg_catg]["widget"]["name"] = p_qt_wdg.objectName()
        self.WDG[p_wdg_catg]["state"] = "active"
        record = {"name": f"widget:{p_wdg_catg}"} | self.WDG[p_wdg_catg]
        record, _ = \
            RI.set_audit_values(db, record, p_include_hash=True)
        RI.do_update(db, record)
        self.WDG[p_wdg_catg]["widget"]["object"] = p_qt_wdg

    # GUI / Main App handlers
    # ==============================================================
    def initialize_UI(self):
        """Set window size and name. Show the window."""
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowTitle(self.TXT['app']['a'])
        self.setStyleSheet(SS.get_style('base'))
        self.setFont(QFont('Arial', 16))
        # ==============================================================
        self.make_state_containers()
        self.make_menus()
        self.make_statusbar()
        self.make_modes_toolbox()
        self.make_svc_controls_wdg()
        self.make_svc_monitor_wdg()
        self.make_db_editor_wdg()
        self.make_help_widget()
        self.make_graph_diagram_wdg()
        # ==============================================================
        self.show()   # <== main window

    # Constants, flags/state holders, and queues
    # ==============================================================
    def make_state_containers(self):
        """Define variables, containers for preserving state.
        Move these to metadata structures for each of the widgets
        and/or store in Redis Basement.

        Consider storing all of the metadata in Redis Basement.
        """
        self.is_active = {
            'controls_wdg': False,
            'monitor_wdg': False,
            'dbeditor_wdg': False,
            'help_wdg': False,
            'diagram_wdg': False}

    # Make menubar, menus and menu items
    # ==============================================================
    def make_menus(self):
        """Define menu bar, menus, menu items (actions).

        @DEV
        - Tried moving menu make, get, set to a separate Class.
        - Menus not working properly, neither in main app nor
          in a separate class. Not going to worry about this for now.
        - Not doing much with menus anyway. Work on it another time.
        - Interestingly, the Ctrl-Q command shortcut works, but the
          menu-items don't display.
        """
        menu_bar = QMenuBar(self)
        menu_bar.setObjectName("app.menu_bar")
        menu_bar.setGeometry(0, 0, 100, 25)
        menu_bar.setStyleSheet(SS.get_style('menu'))
        for mkey, menus in self.WDG["menus"]["menu"].items():
            mname = menus["name"]
            menu = menu_bar.addMenu(mname)
            for mi_key, m_item in menus["items"].items():
                mi_name = m_item["name"]
                mi_action = QAction(mi_name, self)
                mi_cmd = m_item["cmd"] if "cmd" in m_item.keys() else None
                if mi_cmd is not None:
                    mi_action.setShortcut(mi_cmd)
                if mi_key == "app_help":
                    mi_action.triggered.connect(self.show_about)
                elif mi_key == "qt_help":
                    mi_action.triggered.connect(self.show_about_qt)
                elif mi_key == "exit":
                    mi_action.triggered.connect(self.exit_main)
                menu.addAction(mi_action)
            menu_bar.addMenu(menu)
        self.save_meta("menus", menu_bar)

    # Menu actions and helper methods
    # ==============================================================
    def exit_main(self):
        """Slot for Exit action"""
        self.close()

    def show_about(self):
        """Display a message box."""
        msg = self.TXT['app']['c']
        mbox = QMessageBox()
        mbox.about(self, self.TXT['app']['b'], msg)

    def show_about_qt(self):
        """Display a message box about Qt."""
        QMessageBox.aboutQt(self, self.TXT['qt']['a'])

    # Statusbar make method
    # ==============================================================
    def make_statusbar(self):
        """Initialize status bar associated with QMainWindow."""
        self.statusBar().showMessage(self.TXT['app']['a'])

    # Statusbar helper methods
    # ==============================================================
    def set_status_bar_text(self, p_text: str):
        """Display status bar text relevant to events from the main
        app widgets, like the menu or the toolbar.
        """
        self.statusBar().showMessage(p_text)

    # Make modes toolbox method
    # ==============================================================
    def make_modes_toolbox(self):
        """Create mode toolbar and assign its actions.

        Move this into a widget class, with its own status bar.
        """
        self.tbx_modes = ModesToolbox(self)
        acts = {"Control": self.controls_mode_action,
                "Monitor": self.monitor_mode_action,
                "Edit DB": self.db_editor_mode_action,
                "Help": self.help_mode_action}
        for key, act in acts.items():
            self.tbx_modes.acts[key]["widget"].triggered.connect(act)
        self.tbx_modes.move(935, 0)   # <-- move it to upper-right corner

    # Make Service Controls widget
    # Define a status bar for the widget so we can make the functions
    # more autonomous.
    # ==============================================================
    def make_svc_controls_wdg(self):
        """Create the Service Controls widget."""
        self.service_controls = ControlsWidget(self)
        for key, act in {
                "Start": self.start_services,
                "Stop": self.stop_services,
                "Show": self.show_services,
                "Test": self.test_services}.items():
            self.service_controls.acts[key]["widget"].clicked.connect(act)
        self.service_controls.hide()

    # Service Controls slot and helper methods
    # ==============================================================
    def controls_mode_action(self):
        """Slot for Controls Mode tool click action"""
        btn = self.tbx_modes.acts["Control"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
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
            self.set_status_bar_text(btn["caption"])
            status, msg = CS.start_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def stop_services(self):
        """Slot for Stop Services action"""
        btn = self.service_controls.acts["Stop"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
            status, msg = CS.stop_running_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def show_services(self):
        """Slot for Show Services action"""
        btn = self.service_controls.acts["Show"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
            status, msg = CS.check_running_services(p_service_nm='redis')
            self.service_controls.ctl_display.setText(msg)

    def test_services(self):
        """Slot for Test Services action"""
        btn = self.service_controls.acts["Test"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
            msg = """
        This will run pre-defined tests on the services.
            """
            self.service_controls.ctl_display.setText(msg)

    # Make Service Monitor widget
    # Create a stutus bar for the widget so we can make the functions
    # more autonomous.
    # ==============================================================
    def make_svc_monitor_wdg(self):
        """Create the Service Monitor widget."""
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

    # Service Monitor slot and helper methods
    # ==============================================================
    def monitor_mode_action(self):
        """Slot for Services Monitor mode tool click action"""
        btn = self.tbx_modes.acts["Monitor"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
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
            self.set_status_bar_text(btn["caption"])

    def mon_top(self):
        """Slot for Monitor Top button click action"""
        btn = self.service_monitor.acts["Top"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    def mon_tail(self):
        """Slot for Monitor Tail button click action"""
        btn = self.service_monitor.acts["Tail"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    def mon_full(self):
        """Slot for Monitor Full button click action"""
        btn = self.service_monitor.acts["Full"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    def mon_requests(self):
        """Slot for Monitor Requests button click action"""
        btn = self.service_monitor.acts["Requests"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    def mon_fails(self):
        """Slot for Monitor Fails button click action"""
        btn = self.service_monitor.acts["Fails"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    def mon_pressure(self):
        """Slot for Monitor Pressure button click action"""
        btn = self.service_monitor.acts["Pressure"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])

    # Make Database Editor and Record Management widgets
    # ==============================================================
    def make_db_editor_wdg(self):
        """Instantiate the DB Editor widget.
           Instantiate the Records Management widget.

        Define record types, specific editors for each record type,
        and functions to manage DB interactions. Dfeine DB IO actions.
        """
        self.db_editor = DBEditorWidget(self)
        self.RM = RecordMgmt(self, self.db_editor)
        self.db_editor.hide()

    # Database Editor and Record Management slots and helper methods
    # ==============================================================
    def db_editor_mode_action(self):
        """Slot for Edit Database modes tool click action.
        Show DB editor help page.
        """
        btn = self.tbx_modes.acts["Edit DB"]
        if btn["active"]:
            self.set_status_bar_text(btn["caption"])
            try:
                if self.is_active['dbeditor_wdg'] is False:
                    self.db_editor.show()
                    self.is_active['dbeditor_wdg'] = True
                    self.help.set_content("db_help.html")
                    # Display the diagram when there is something
                    #  interesting to show on it.
                    # self.show_graph_diagram()
                else:
                    self.db_editor.hide()
                    self.is_active['dbeditor_wdg'] = False
                    # self.hide_graph_diagram()
            except AttributeError:
                pass

    # Make Help widget (web pages) display
    # ==============================================================
    def make_help_widget(self):
        """Define help display.
        """
        self.help = HelpWidget(self)
        self.help.hide()

    # Help (Web pages) Display
    # ==============================================================
    def help_mode_action(self):
        """Slot for Help Mode tool click action"""
        btn = self.tbx_modes.acts["Help"]
        self.set_status_bar_text(btn["caption"])
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

    # Make widget to display networkx graph diagrams
    # ==============================================================
    def make_graph_diagram_wdg(self):
        """Generate a Graph Diagram.
        """
        self.network = DiagramWidget()
        # By default, creates a test diagram.
        # See DiagramWidget class method "set_content()" for more details.

    # Graph diagram slots and helper functions
    # May be able to move these into the DiagramWidget class.
    # ==============================================================
    def show_graph_diagram(self):
        """Slot for Graph Diagram show action"""
        try:
            if self.is_active['diagram_wdg'] is False:
                try:
                    img = self.network.get_image_path()
                    with open(img):
                        self.diagram_wdg = QLabel(self)
                        self.diagram_wdg.setGeometry(20, 650, 550, 200)
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

    def hide_graph_diagram(self):
        """Slot for Graph Diagram hide action"""
        try:
            if self.is_active['diagram_wdg'] is True:
                self.diagram_wdg.hide()
                self.is_active['diagram_wdg'] = False
        except AttributeError:
            pass


# Run program
if __name__ == '__main__':
    """Instantiate the app and start the event loop.
    """
    app = QApplication(sys.argv)
    # The class object has the .show() command in it:
    SRV = SaskanEyes()
    sys.exit(app.exec_())
