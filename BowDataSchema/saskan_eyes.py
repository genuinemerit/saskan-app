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
from se_record_mgmt import RecordMgmt           # type: ignore

CS = ControlsShell()
FI = FileIO()
RI = RedisIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class SaskanEyes(QMainWindow):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    May add other stuff later, like a Schema Editor and DB generator,
    link into the game itself, later on.
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
        self.make_state_containers()
        self.make_menus()
        self.make_statusbar()
        self.make_modes_toolbox()
        self.make_svc_controls_wdg()
        self.make_svc_monitor_wdg()
        self.make_db_editor_wdg()
        self.make_records_mgmt_wdg()
        self.make_help_widget()
        self.make_graph_diagram_wdg()
        # ==============================================================
        self.show()   # <== main window

    # Constants, flags/state holders, and queues
    # ==============================================================
    def make_state_containers(self):
        """Define variables, containers for preserving state.

        @DEV:
        - Move config values to Redis or config file.
        - See if we can do away with "active" flags.
          Query a Qt signal for active state instead?
        """
        self.APP = path.join(UT.get_home(), 'saskan')
        self.RES = path.join(self.APP, 'res')
        self.LOG = path.join(self.APP, 'log')
        self.is_active = {
            'controls_wdg': False,
            'monitor_wdg': False,
            'dbeditor_wdg': False,
            'help_wdg': False,
            'diagram_wdg': False}

    # Make menu methods
    # ==============================================================
    def make_menus(self):
        """Define menu bar, menus, menu items (actions).

        @DEV
        - Consider moving menu construction, get, set
          to a separate Class.
        """
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

    # Menu actions and helper methods
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

    # Statusbar make method
    # ==============================================================
    def make_statusbar(self):
        """Initialize status bar associated with QMainWindow."""
        self.statusBar().showMessage(TX.tl.app)

    # Statusbar helper methods
    # ==============================================================
    def set_status_bar_text(self, p_text: str):
        """Display status bar text relevant to some event like a
        button or tool click.

        Ignore if no text passed in or status bar does not exist.

        @DEV
        - Consider moving status bar construction, get, set to
            a separate Class.
        """
        if p_text not in (None, ""):
            try:
                self.statusBar().showMessage(p_text)
            except AttributeError:
                pass

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

    # Make Database Editor widget
    # ==============================================================
    def make_db_editor_wdg(self):
        """Instantiate the DB Editor widget.

        Provide actions for events outside of widget's class.
        Use RecordMgmt class to define DB interactions.
        """
        self.db_editor = DBEditorWidget(self)
        for key, act in {
                ("Edit", "Add"): self.add_record_to_db,
                ("Get", "Find"): self.find_record_keys}.items():
            wdg = self.db_editor.buttons[key[0]][key[1]]["widget"]
            wdg.clicked.connect(act)
        self.db_editor.hide()

    # Make Records Management widget
    # ==============================================================
    def make_records_mgmt_wdg(self):
        """Instantiate the Records Management widget.

        Define record types, specific editors for each record type,
        and functions to manage DB interactions.
        """
        self.RM = RecordMgmt(self, self.db_editor)
        pp(("self.RM, self.db_editor", self.RM, self.db_editor))

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

    # Move these to RecordMgmt class ...
    # ==============================================================
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

    def validate_links(self,
                       p_db_nm: str,
                       p_rectyp: str,
                       p_record: dict):
        """Validate foreign key values before writing to DB.

        :args:
            p_db_nm - name of db containing the record type
            p_rectyp - record type
            p_record - record to be written to DB
        """
        links = self.db_editor.get_value_fields(p_links_only=True)
        if links != {}:
            for link_nm, link_values in links.items():
                for link_ix, link_val in enumerate(link_values):
                    link_key = \
                        self.db_editor.edit["redis_key"](link_val)
                    p_record[link_nm][link_ix] = link_key
                    link_rec = self.find_redis_keys(
                        p_db_nm, p_rectyp, link_key, p_load_1st_rec=False)
                    if link_rec in (None, {}, []):
                        self.db_editor.set_cursor_result(
                            f"No record found with key '{link_key}'")
                        return False
        return True

    def add_record_to_db(self,
                         p_is_auto: bool = False,
                         p_db_nm: str = None,
                         p_rectyp_nm: str = None):
        """Add a record to the DB per active record type in Editor.

        Acts as slot for DB Editor Edit/Add push button click action.
        Or if based on parameters, does automated record-add logic.

        Get all values from active edit form.
        Check to see if record w/key already exists on DB.
        Reject Add if rec already exists.

        :args:
            p_is_auto - True if this is an auto-add,
                        False if Add button was clicked
            p_db_nm - name of the DB to add the record to,
                      defaults to None for Add button clicks.
            p_rectyp_nm - name of the record type to add,
                      defaults to None for Add button clicks.

        :returns: (bool) True if record was added, False if not
        """
        manual_add = True
        self.db_editor.prep_editor_action("Add")
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.db_editor.get_active_record_type()
            _, record = self.db_editor.get_all_fields()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
            # It is an auto-generated record.
            # Need to specify the DB and record type.
            # Would we still use a Form widget to CREATE the record?
            # hmmm... probably not? But would it be doable? Why not?
            manual_add = False
            values = self.db_editor.get_value_fields(False, db, rectyp)
            key = f"{rectyp.lower()}:{RI.UT.get_hash(str(values))}"
            record = {"name": key} | values
        result = self.get_redis_record(db, record["name"])
        if result in (None, [], {}):
            if self.db_editor.run_rectyp_edits():
                if not self.validate_links(db, rectyp, record):
                    return False
                if manual_add:
                    record = RI.set_audit_values(record, p_include_hash=True)
                else:
                    record = RI.set_audit_values(record, p_include_hash=False)
                RI.do_insert(db, record)
                return True
        else:
            self.db_editor.set_cursor_result(
                "Insert rejected. Record already exists.")
            return False

    def find_redis_keys(self,
                        p_db_nm: str,
                        p_rectyp: str,
                        p_key_pattern: str,
                        p_load_1st_rec: bool = True):
        """Get a list of keys for selected DB matching the pattern.

        :args:
            p_db_nm - name of the database to search
            p_rectyp - record type to search
            p_key_pattern - pattern to match for keys
            p_load_1st_rec - load 1st record found into editor
        :returns: list of keys that match the pattern or None
        """
        db = p_db_nm
        result_b = RI.find_keys(db, p_key_pattern)
        result: list = []
        if result_b in (None, [], {}):
            self.db_editor.set_cursor_result(
                f"No record found with key like '{p_key_pattern}'")
        else:
            for res in result_b:
                result.append(res.decode("utf-8"))
            result = sorted(result)
            rcnt = len(result)
            rword = "record" if rcnt == 1 else "records"
            self.db_editor.set_cursor_result(
                f"{rcnt} {rword} found with key like '{p_key_pattern}'")
            if p_load_1st_rec:
                # Get first record from find key list, display in editor
                # Select first record in the set of found keys.
                _ = self.get_redis_record(db, result[0])
                # If more than one key was found,
                if len(result) > 1:
                    self.db_editor.activate_buttons("Get", ["Next", "Prev"])
                else:
                    self.db_editor.deactivate_buttons("Get", ["Next", "Prev"])
                # To load from db record to editor form(s), use functions
                # in the DB Editor class:
                #  db_editor.set_key_fields(record)
                #  db_editor.set_value_fields(record)
                #   sub-function: db_editor.set_list_field(field, value)
                #  consider whether to display audit and expiry values?
                #    I am thinking yes. Why not? Just can't edit them.

                # Populate the rectyp editor widget and forms for first record.
                # Don't pull in the widget here. Instead,
                # create functions in dbeditor_wdg like:
                #  set_key_fields()
                #  set_value_fields()
                #    and a sub-function probably for set_list_fields()
                #  Widget stored at:
                #    self.rectyps[db_nm][rectyp_nm]["widget"] = rectyp_wdg
                #  Name of the entire form:
                #    f"{db_nm}:{rectyp_nm}:{f_grp}.frm"
                #  Name of the list forms, if any:
                #    f"{db_nm}:{rectyp_nm}:{field_nm}.frm"

                # Create a Harvest Queue record with the keyset result.
                # Store list of found keys in the queue for use with
                #  Next and Prev buttons.
                # Use a Redis queue (a list) for this. On Harvest Queues.
                # Still need to store the hash/key locally and keep track
                # of which record in the list is being displayed/edited.
                # For adds:
                #   Store auto-generated Queue record in the Qt form first.
                #   Store the list of found keys as a single field value.
                #   Then call the Add record function.
                # Put it into the Harvest/Queue editor widget form(s),
                #  but don't display it.
                #
                # Should be able to find/display the queue record.
                # If the Queue record itself is target of a Find commend,
                #  then full list of keys needs to be displayed in
                #  individual "list"-type fields in the editor form.
                #  Queue records should not be edited manually.

                # This is an opportunity to learn setting expiry rules.
                # Consider how to display expiry times. Thinking that
                # should be an Audit field.

                # Don't create a queue if the find result is empty or has
                # only one record. Do expire the queue record after a short
                # time. Maybe expire the previous queue record if the Find
                # button is clicked again?

                # The record displayed in the editor is the first one
                # found by the Find. It may or may not be a Queue record.
                # It could be any kind of record on any database.

                # Let's work first on displaying the 1st record returned,
                # then on expiry time stamps & rules, then on queue recs.

                # Expire time can be set 4 ways:
                #    EXPIRE <key> <seconds> <-- from now
                #    EXPIREAT <key> <timestamp> <-- Unix timestamp
                #    PEXPIRE <key> <milliseconds> <-- from now
                #    PEXPIREAT <key> <milliseconds-timestamp> <-- Unix ts in ms
                #  Get expire time 4 ways:
                #    TTL <key> <-- get time to live in seconds
                #    PTTL <key> <-- get time to live in ms
                #    EXPIRETIME <key> <-- Unix timestamp
                #    PEXPIRETIME <key> <-- Unix timestamp in ms
                # I am thinking to set a rule in a Basement:Config record for
                #   each DB/record type. That will drive the expiry time.

        return (result)

    def find_record_keys(self):
        """Slot for DB Editor Find push button click action."""
        self.db_editor.prep_editor_action("Find")
        db_nm, search_key = self.db_editor.get_search_value()
        _ = self.find_redis_keys(db_nm, search_key, p_load_1st_rec=True)

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
