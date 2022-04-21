#!/usr/bin/python3.9
"""
:module:    saskan_eyes.py
:author:    GM (genuinemerit @ pm.me)
BoW Saskan App Admin GUI."""
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
from se_diagram_wdg import DiagramWidget        # type: ignore
from se_help_wdg import HelpWidget              # type: ignore
from se_modes_tbx import ModesToolbox           # type: ignore
from se_monitor_wdg import MonitorWidget        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore
from se_record_mgmt import RecordMgmt           # type: ignore
from wire_tap import WireTap                    # type: ignore

BT = BootTexts()
FI = FileIO()
RI = RedisIO()
SS = SaskanStyles()
WT = WireTap()


class SaskanEyes(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs."""

    def __init__(self):
        """super() call is required."""
        WT.log_module(__file__, __name__, self)
        super().__init__()
        self.ARGS = self.init_configs()
        self.WDG = self.load_meta("widget")
        self.initialize_UI()

    # Command line argument handlers
    # ==============================================================
    def init_configs(self):
        """Handle command-line arguments."""

        def set_arguments():
            """Define command-line arguments."""
            parser = argparse.ArgumentParser(description=BT.txt.app_desc)
            parser.add_argument(
                '--force-refresh', action='store_true', help=BT.txt.refresh_desc)
            parser.add_argument(
                '--info', action='store_true', help=BT.txt.info_desc)
            parser.add_argument(
                '--warn', action='store_true', help=BT.txt.warn_desc)
            parser.add_argument(
                '--tracef', action='store_true', help=BT.txt.tracef_desc)
            parser.add_argument(
                '--traced', action='store_true', help=BT.txt.traced_desc)
            parser.add_argument(
                '--debug', action='store_true', help=BT.txt.debug_desc)
            args = parser.parse_args()
            return args
 
        def set_defaults():
            """Set default config file values if not already set."""
            ok, _, _ = FI.get_file(BT.log_level)
            if not ok:
                ok, err = FI.write_file(BT.log_level, BT.txt.error_val)
            if ok:
                ok, _, _ = FI.get_file(BT.trace_level)
                if not ok:
                    ok, err = FI.write_file(BT.trace_level, BT.txt.notrace_val)
            if ok:
                ok, _, _ = FI.get_file(BT.debug_level)
                if not ok:
                    ok, err = FI.write_file(BT.debug_level, BT.txt.nodebug_val)
            if not ok:
                print(err)
                exit(1)
 
        def handle_arguments(args):
            """Get current settings, then assign actions based on arguments."""
            ok = True
            if args.traced:
                ok, err = FI.write_file(BT.trace_level, BT.txt.traced_val)
            elif args.tracef:
                ok, err = FI.write_file(BT.trace_level, BT.txt.tracef_val)
            if args.warn:
                ok, err = FI.write_file(BT.log_level, BT.txt.warn_val)
            elif args.info:
                ok, err = FI.write_file(BT.log_level, BT.txt.info_val)
            if args.debug:
                ok, err = FI.write_file(BT.debug_level, BT.txt.debug_val)
            if not(ok):
                print(err)
                exit(1)

            if args.force_refresh:
                self.refresh_configs()

        args = set_arguments()
        set_defaults()
        handle_arguments(args)
        WT.log_function(self.init_configs, self)
        return args

    def refresh_configs(self):
        """Refresh Basement DB texts, configs from JSON config file."""

        def load_cfg_file(p_config_file_path: str):
            """Read data from config file."""
            WT.log_function(load_cfg_file, self)
            ok, err, configs = FI.get_file(p_config_file_path)
            if not ok:
                print(f"{BT.txt.err_file} {err}")
                exit(1)
            elif configs is None:
                print(f"{BT.txt.no_file}{p_config_file_path}")
                exit(1)
            config_data = json.loads(configs)
            return(config_data)

        def set_configs(p_config_data: dict,
                        p_catg: str):
            """Set text and widget metadata records on Basement DB."""
            WT.log_function(set_configs, self)
            db = "basement"
            for k, values in p_config_data.items():
                key = RI.clean_redis_key(f"{p_catg}:{k}")
                record = {db: {"name": key} | values}
                record, update = \
                    RI.set_audit_values(record, p_include_hash=True)
                key = record["name"]
                if update:
                    RI.do_update(db, record)
                else:
                    RI.do_insert(db, record)

        WT.log_function(self.refresh_configs, self)
        set_configs(load_cfg_file(BT.file_widgets), "widget")

    # Load and save texts and widget metadata
    # ==============================================================
    def load_meta(self, p_catg):
        """Load configuration data from db to memory."""
        WT.log_function(self.load_meta, self)
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
        """Update Basement DB with modified widget record."""
        WT.log_function(self.save_meta, self)
        db = "basement"
        self.WDG[p_wdg_catg]["w"]["name"] = p_qt_wdg.objectName()
        record = {"basement":
                  {"name": f"widget:{p_wdg_catg}"} | self.WDG[p_wdg_catg]}
        record, _ = \
            RI.set_audit_values(record, p_include_hash=True)
        RI.do_update(db, record)
        self.WDG[p_wdg_catg]["w"]["object"] = p_qt_wdg

    # GUI / Main App handlers
    # ==============================================================
    def initialize_UI(self):
        """Set window size and name. Show the window."""
        WT.log_function(self.initialize_UI, self)
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowTitle(self.WDG['about']['app']['a'])
        self.setStyleSheet(SS.get_style('base'))
        self.setFont(QFont('Arial', 16))
        # ==============================================================
        self.make_menus()
        self.make_statusbar()
        self.make_modes_toolbox()
        self.make_svc_control_wdg()
        self.make_svc_monitor_wdg()
        self.make_help_widget()
        self.make_db_editor_wdg()
        # self.make_graph_diagram_wdg()
        # ==============================================================
        self.show()   # <== main window

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
          menu-items don't display or pop up properly. """
        WT.log_function(self.make_menus, self)
        menu_bar = QMenuBar(self)
        menu_bar.setObjectName("app.menu_bar")
        menu_bar.setGeometry(0, 0, 100, 25)
        menu_bar.setStyleSheet(SS.get_style('menu'))
        for _, menus in self.WDG["menus"]["menu"].items():
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
        """Handle exit action."""
        WT.log_function(self.exit_main, self)
        self.close()

    def show_about(self):
        """Display a message box."""
        WT.log_function(self.show_about, self)
        msg = self.WDG['about']['app']['c']
        mbox = QMessageBox()
        mbox.about(self, self.WDG['about']['app']['b'], msg)

    def show_about_qt(self):
        """Display a message box about Qt."""
        WT.log_function(self.show_about_qt, self)
        QMessageBox.aboutQt(self, self.WDG['about']['qt']['a'])

    # Statusbar make method
    # ==============================================================
    def make_statusbar(self):
        """Initialize status bar associated with QMainWindow."""
        WT.log_function(self.make_statusbar, self)
        self.statusBar().showMessage(self.WDG['about']['app']['a'])

    # Statusbar helper methods
    # ==============================================================
    def set_statusbar_text(self, p_text: str):
        """Display status bar text relevant to events from the main
        app widgets, like the menu or the toolbar."""
        WT.log_function(self.set_statusbar_text, self)
        self.statusBar().showMessage(p_text)

    # Make modes toolbox
    # ==============================================================
    def make_modes_toolbox(self):
        """Create mode toolbar and assign its actions.
        Move toolbox to upper-right corner of the main window."""
        WT.log_function(self.make_modes_toolbox, self)
        self.tbx_modes = ModesToolbox(self, self.WDG["tools"])
        self.WDG["tools"] = self.tbx_modes.get_tools()
        for tk, action in {
                "controls.tool": self.controls_mode_tool_click,
                "monitor.tool": self.monitor_mode_tool_click,
                "db_editor.tool": self.editor_mode_tool_click,
                "help.tool": self.help_mode_tool_click}.items():
            self.WDG["tools"][tk]["w"].triggered.connect(action)
        self.tbx_modes.move(935, 0)

    # Modes toolbox actions and helpers
    # ==============================================================
    def mode_tool_click(self,
                        p_tool_nm: str,
                        p_help_pg: str = None):
        """Define action for mode tool click.
        Optionally show main help page assoc w/ activated widget.
        :args:
            p_tool_nm: - key to metadata for the tool
            p_help_pg: - name of help page to show"""
        WT.log_function(self.mode_tool_click, self)
        tool = self.WDG["tools"][f"{p_tool_nm}.tool"]
        self.set_statusbar_text(tool["c"])
        if self.WDG[p_tool_nm]["w"].isVisible():
            self.WDG[p_tool_nm]["w"].hide()     # type: ignore
        else:
            self.WDG[p_tool_nm]["w"].show()     # type: ignore
            if p_help_pg is not None:
                self.helper.set_content(
                    path.join(BT.path_res, p_help_pg))
                self.helper.show()

    def controls_mode_tool_click(self):
        """Handle Controls Mode tool click."""
        WT.log_function(self.controls_mode_tool_click, self)
        self.mode_tool_click("controls", "svc_activation.html")

    def monitor_mode_tool_click(self):
        """Handle Services Monitor mode tool click."""
        WT.log_function(self.monitor_mode_tool_click, self)
        self.mode_tool_click("monitor", "svc_monitoring.html")

    def editor_mode_tool_click(self):
        """Handle DB Editor mode tool click."""
        WT.log_function(self.editor_mode_tool_click, self)
        self.mode_tool_click("db_editor", "db_help.html")

    def help_mode_tool_click(self):
        """Handle Help mode tool click."""
        WT.log_function(self.help_mode_tool_click, self)
        self.mode_tool_click("help", "saskan_help.html")

    # Make Service Controls widget.
    # ==============================================================
    def make_svc_control_wdg(self):
        """Create Service Controls widget.
        Its actions are handled within this class."""
        WT.log_function(self.make_svc_control_wdg, self)
        controls = ControlsWidget(self, self.WDG["controls"])
        self.WDG["controls"] = controls.get_tools()

    # Make Service Monitor widget.
    # ==============================================================
    def make_svc_monitor_wdg(self):
        """Create Service Monitor widget.
        Its actions are handled within this class."""
        WT.log_function(self.make_svc_monitor_wdg, self)
        monitor = MonitorWidget(self, self.WDG["monitor"])
        self.WDG["monitor"] = monitor.get_tools()

    # Make Help widget (web pages) display
    # ==============================================================
    def make_help_widget(self):
        """Define help display."""
        WT.log_function(self.make_help_widget, self)
        self.helper = HelpWidget(self, self.WDG["help"])
        self.WDG["help"] = self.helper.get_tools()

    # Make Database Editor and Record Management widgets
    # ==============================================================
    def make_db_editor_wdg(self):
        """Create DB Editor and Records Mgmt widgets.
        Their actions are handled in their class modules."""
        WT.log_function(self.make_db_editor_wdg, self)
        editor = DBEditorWidget(self, self.WDG["db_editor"])
        self.WDG["db_editor"] = editor.get_tools()
        recordio = RecordMgmt(self, self.WDG["record_io"], editor)
        self.WDG["record_io"] = recordio.get_tools()

    # Make widget to display networkx graph diagrams
    # ==============================================================
    def make_graph_diagram_wdg(self):
        """Generate a Graph Diagram."""
        WT.log_function(self.make_graph_diagram_wdg, self)
        self.netx = DiagramWidget(self.WDG["diagram"])
        self.WDG["diagram"] = self.netx.get_tools()

    # Graph diagram slots and helper functions
    # May be able to move these into the DiagramWidget class.
    # ==============================================================
    def show_graph_diagram(self):
        """Handle Graph Diagram show action."""
        WT.log_function(self.show_graph_diagram, self)
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
        except FileNotFoundError:
            print("User image file not found:" + img)

    def hide_graph_diagram(self):
        """Handle Graph Diagram hide action."""
        WT.log_function(self.hide_graph_diagram, self)
        if self.WDG["diagram"]["w"].isVisible():
            self.diagram_wdg.hide()


# Run program
if __name__ == '__main__':
    """Instantiate app and start event loop."""
    app = QApplication(sys.argv)
    # The class object has the .show() command in it:
    SRV = SaskanEyes()
    sys.exit(app.exec_())
