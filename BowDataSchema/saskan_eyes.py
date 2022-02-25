#!/usr/bin/python3.9
"""
:module:    saskan_eyes.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI.
"""
import argparse
import json
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

from boot_texts import BootTexts                # type: ignore
from file_io import FileIO                      # type: ignore
from redis_io import RedisIO                    # type: ignore
from se_controls_wdg import ControlsWidget      # type: ignore
from se_dbeditor_wdg import DBEditorWidget      # type: ignore
from se_diagram_wdg import DiagramWidget      # type: ignore
from se_help_wdg import HelpWidget              # type: ignore
from se_modes_tbx import ModesToolbox           # type: ignore
from se_monitor_wdg import MonitorWidget        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore
from se_record_mgmt import RecordMgmt           # type: ignore

BT = BootTexts()
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
        self.make_svc_control_wdg()
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
            'control_wdg': False,
            'monitor_wdg': False,
            'editor_wdg': False,
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

    # Make modes toolbox
    # ==============================================================
    def make_modes_toolbox(self):
        """Create mode toolbar and assign its actions.

        Move toolbox to upper-right corner of the main window.
        """
        self.tbx_modes = ModesToolbox(self, self.WDG["tools"])
        self.WDG["tools"] = self.tbx_modes.get_tools()
        for tk, action in {
                "control.tool": self.controls_mode_tool_click,
                "monitor.tool": self.monitor_mode_tool_click,
                "editor.tool": self.editor_mode_tool_click,
                "help.tool": self.help_mode_tool_click}.items():
            self.WDG["tools"][tk]["widget"].triggered.connect(action)
        self.tbx_modes.move(935, 0)

    # Modes toolbox actions and helpers
    # ==============================================================
    def mode_tool_click(self,
                        p_tool_nm: str,
                        p_widget: object,
                        p_help_pg: str = None):
        """Generic action for mode tool click action

        Optionally show main help page assoc w/ activated widget.
        :args:
            p_tool_nm: str
                Name of the tool.
            p_widget: object
                Qt widget associated with the tool.
            p_help_pg:
                Name of the help page to show.
        """
        meta = self.WDG["tools"][f"{p_tool_nm}.tool"]
        self.set_status_bar_text(meta["c"])
        if self.is_active[f"{p_tool_nm}_wdg"] is False:
            p_widget.show()     # type: ignore
            if p_help_pg is not None:
                self.help.set_content(path.join(BT.path_res, p_help_pg))
                self.help.show()
            self.is_active[f"{p_tool_nm}_wdg"] = True
        else:
            p_widget.hide()     # type: ignore
            self.is_active[f"{p_tool_nm}_wdg"] = False

    def controls_mode_tool_click(self):
        """Slot for Controls Mode tool click action"""
        self.mode_tool_click("control", self.svc_control_wdg,
                             "svc_activation.html")

    def monitor_mode_tool_click(self):
        """Slot for Services Monitor mode tool click action"""
        self.mode_tool_click("monitor", self.service_monitor,
                             "svc_monitoring.html")

    def editor_mode_tool_click(self):
        """Slot for DB Editor mode tool click action."""
        self.mode_tool_click("editor", self.db_editor, "db_help.html")

    def help_mode_tool_click(self):
        """Slot for Help mode tool click action"""
        self.mode_tool_click("help", self.help, "saskan_help.html")

    # Make Service Controls widget.
    # ==============================================================
    def make_svc_control_wdg(self):
        """Create the Service Controls widget.

        All of its actions are handled within the class.
        """
        self.svc_control_wdg = ControlsWidget(self, self.WDG["controls"])
        self.WDG["controls"] = self.svc_control_wdg.get_tools()

    # Make Service Monitor widget.
    # Create a stutus bar for the widget so we can make the functions
    # more autonomous. Extend the class similarly to how the control
    # widget was modified.
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

    # Make Help widget (web pages) display
    # ==============================================================
    def make_help_widget(self):
        """Define help display.
        """
        self.help = HelpWidget(self)
        self.help.hide()

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
