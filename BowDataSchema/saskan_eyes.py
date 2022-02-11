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
        self.setGeometry(100, 100, 1200, 900)
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
                    # Display the diagram when there is something
                    #  interesting to show on it.
                    # self.show_diagram()
                else:
                    self.db_editor.hide()
                    self.is_active['dbeditor_wdg'] = False
                    # self.hide_diagram()
            except AttributeError:
                pass

    def get_redis_record(self,
                         p_db_nm: str,
                         p_select_key: str):
        """Get a record from Redis DB
        :args: p_db_nm - name of Redis DB
                p_select_key - key of record to be retrieved
        :returns: records as a dict or None
        """
        result = RI.get_record(p_db_nm, p_select_key)
        if result is None:
            self.db_editor.set_cursor_result(
                f"No records found with key like '{p_select_key}'")
        else:
            print(f"GET Result: {result}")
            # put the values into the editor
            pass
        return (result)

    def find_redis_keys(self,
                        p_db_nm: str,
                        p_key_pattern: str,
                        p_load_records: bool = True):
        """Get a list of keys for selected DB matching the pattern.

        :args:
            p_db_nm - name of the database to search
            p_key_pattern - pattern to match for keys
            p_load_records - load 1st record found into editor
        :returns: list of keys that match the pattern or None
        """
        result_b = RI.find_records(p_db_nm, p_key_pattern)
        result: list = []
        if result_b in (None, [], {}):
            self.db_editor.set_cursor_result(
                f"No record found with key like '{p_key_pattern}'")
        else:
            for res in result_b:
                result.append(res.decode("utf-8"))
            result = sorted(result)
            # select the first record in the set
            rcnt = len(result)
            rword = "record" if rcnt == 1 else "records"
            self.db_editor.set_cursor_result(
                f"{rcnt} {rword} found with key like '{p_key_pattern}'")
            if p_load_records:
                # Put first record found into the editor
                _ = self.get_redis_record(p_db_nm, result[0])
                self.db_editor.activate_buttons("Get", ["Next", "Prev"])
        return (result)

    def push_add_btn(self) -> bool:
        """Slot for DB Editor Edit/Add push button click action.

        Get all values from active edit form.
        Check to see if record w/key already exists on DB.

        For now, reject Add if rec already exists.
        Later, maybe provide update option.

        :returns: (bool) True if record was added, False if not
        """
        self.db_editor.prep_editor_action("Add")
        db_nm, record = self.db_editor.get_all_fields()
        result = self.get_redis_record(db_nm, record["name"])
        if result in (None, [], {}):
            # Do edits associated with the record type.
            if self.db_editor.run_rectyp_edits():
                # If all OK, then do link auto-formatting and checks.
                links = self.db_editor.get_value_fields(p_links_only=True)
                if links != {}:
                    pp(("links", links))
                    for link_nm, link_values in links.items():
                        for link_ix, link_val in enumerate(link_values):
                            print(f"link_val: {link_val}")
                            link_key = \
                                self.db_editor.edit["redis_key"](link_val)
                            print(f"link_key: {link_key}")
                            record[link_nm][link_ix] = link_key
                            link_rec = self.find_redis_keys(
                                db_nm, link_key, p_load_records=False)
                            if link_rec in (None, {}, []):
                                self.db_editor.set_cursor_result(
                                    f"No record found with key '{link_key}'")
                                return False
                # If all OK, then format the Audit fields.
                pp((f"Attempting a {db_nm} insert for record: ", record))
                # nx means "write a new record. do not overwrite existing"
                RI.do_upsert(db_nm, "nx", record, {})
                return True
        # - prep the record
        #   - convert value package to bytes
        #   - encrypt value package (maybe)
        # - add the record
        #   - if insert succeeds show success message
        #   - if we move to a pending/commit/save model,
        #       then update the pending queue & status
        #   - display error message if insert fails
        else:
            # Record already exists, reject the add.
            self.db_editor.set_cursor_result(
                "Insert rejected. Record already exists.")
            return False

    def push_find_btn(self):
        """Slot for DB Editor Find push button click action."""
        self.db_editor.prep_editor_action("Find")
        db_nm, search_key = self.db_editor.get_search_value()
        result = self.find_redis_keys(db_nm, search_key)
        pp(("FIND result", result))

    def create_db_editor(self):
        """Instantiate the DB Editor widget.

        Provide actions for events outside of widget's class.
        """
        self.db_editor = DBEditorWidget(self)
        for key, act in {
                ("Edit", "Add"): self.push_add_btn,
                ("Get", "Find"): self.push_find_btn}.items():
            wdg = self.db_editor.buttons[key[0]][key[1]]["widget"]
            wdg.clicked.connect(act)
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
