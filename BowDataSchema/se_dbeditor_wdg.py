#!/usr/bin/python3.9
"""
:module:    se_dbeditor_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Look for places where assigning an object name
  to a Qt widget or layout will be useful.
- Eventually move all text strings to SaskanTexts
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()


class DBEditorWidget(QWidget):
    """Build container for the DB Editor components.

    Define/enable the DB Editor functions widget.
    Define buttons, forms, texts for filtering
      and editing data on the Redis databases.

    @DEV:
    - Later ==> add similar Class for SQLite or Postgres.
    """
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.set_edits_meta()
        self.set_texts_meta()
        self.set_buttons_meta()
        self.set_rectyp_meta()
        self.make_db_editor_wdg()

    def set_edits_meta(self):
        """To use when applying edits and auto-corrects.

        This includes:
        - named enum lists
        - input masks
        - specialized functions

        @DEV:
        - Eventually some of these will be loaded
          from config files or startup parameters.
        """
        def bump_underbars(text):
            """Remove stray underbars

            - Remove leading or trailing underbars
            - Reduce multiple underbars to single underbars
            """
            r_str = text
            while "__" in r_str:
                r_str = r_str.replace("__", "_")
            while r_str[-1:] == "_":
                r_str = r_str[:-1]
            while r_str[:1] == "_":
                r_str = r_str[1:]
            return r_str

        def bump_redis_key(text):
            """Convert anything not a letter or colon to underbar.
            And make it lowercase.
            """
            r_str = text
            for char in r_str:
                if not char.isalpha() and char != ":":
                    r_str = r_str.replace(char, "_")
            return bump_underbars(r_str)

        def verify_host(p_value: str):
            """Validate value against enumerated list."""
            if p_value in ["localhost", "curwen"]:
                print(f"Host {p_value} is valid.")
                return True
            else:
                print(f"Host {p_value} is not valid.")
                return False

        self.mask = {"date": "0000-00-00",
                     "lower": "<"}
        self.edit = {"redis_key": bump_redis_key,
                     "hostlist": verify_host}

    # Text Widget Creation
    # ============================================================

    def set_texts_meta(self):
        """Define metadata for the DB Editor Text items.

        This metadata defines text-string attributes of text items.
        They may be display-only subtitles, placeholder hints
        in text inputs, the content of a label in a row-based line
        edits within forms, or the help caption associated with a
        push button or radio button.

        This dict also holds a copy of the instantiated widget.

        @DEV:
        - This should be further abstracted via BowQuiver.saskan_texts.
        """
        self.texts: dict = dict()
        texts_template = {
            "caption": str(),
            "display": str(),
            "hint": str(),
            "readonly": True,
            "active": False,
            "widget": None}
        texts = {"key_fields": {"display": "Key Fields"},
                 "value_fields": {"display": "Value Fields"},
                 "dbe_status": {"display": "Database Editor Status"},
                 "Key": {"hint": "lower case letters, underbars, colons only"},
                 "Cursor": {"hint": "Cursor/Result summary"},
                 "Pending": {"hint": "Pending changes"},
                 "Keys": {"display": "Key Fields"},
                 "Values": {"display": "Value Fields"},
                 "Types": {"display": "Select Record Type"},
                 "Get": {"display": "Find Record(s)"},
                 "Edit": {"display": "Edit Record"},
                 "Configs": {
                    "display": "Config Records (Basement DB)",
                    "caption": "Records defining config data structures."},
                 "Status": {
                    "display": "Status Flag Records (Basement DB)",
                    "caption": "Records defining status data structures."},
                 "Expire Rules": {
                    "display": "Expiration Rules (Basement DB)",
                    "caption": "Records holding record expiration rules."},
                 "Retry Rules": {
                    "display": "Retry Rules (Basement DB)",
                    "caption": "Records holding message retry rules."},
                 "Topics": {
                    "display": "Topic Records (Schema DB)",
                    "caption": "Records holding service topic definitions."},
                 "Plans": {
                    "display": "Plan Records (Schema DB)",
                    "caption": "Records holding service plan definitions."},
                 "Services": {
                    "display": "Service Records (Schema DB)",
                    "caption": "Records holding service definitions."},
                 "Schemas": {
                    "display": "Schema Records (Schema DB)",
                    "caption": "Records holding service schema definitions."},
                 "Response": {
                    "display": "Response Records (Harvest DB)",
                    "caption": "Records holding request responses and pubs."},
                 "Activator Log": {
                    "display": "Activator Events (Log DB)",
                    "caption": "Log records for service activator events."},
                 "Request Log": {
                    "display": "Request Events (Log DB)",
                    "caption": "Log records for service request/sub events."},
                 "Response Log": {
                    "display": "Response Events (Log DB)",
                    "caption": "Log records for service response/pub events."},
                 "Server Monitor": {
                    "display": "Server/Channel Monitor (Monitor DB)",
                    "caption": "Summary records for server/channel loads."},
                 "Requests Monitor": {
                    "display": "Requests Monitor (Monitor DB)",
                    "caption": "Summary records for request/sub events."},
                 "Responses Monitor": {
                    "display": "Responses Monitor (Monitor DB)",
                    "caption": "Summary records for response/pub events."},
                 "Find": {"caption": "Find keys matching search pattern. " +
                          "Select all keys if no text entered."},
                 "Next": {"caption":
                          "Retrieve next record from cursor IO result."},
                 "Prev": {"caption":
                          "Retrieve previous record from cursor IO result."},
                 "Add": {"caption":
                         "Create a new record of the selected type."},
                 "Delete": {"caption":
                            "Mark currently selected record for removal."},
                 "Save": {"caption":
                          "Commit all pending changes."},
                 "Undo": {"caption":
                          "Reverse the most recent edit (Ctrl+Z)."},
                 "Redo": {"caption":
                          "Re-apply the most recently undone edit (Ctrl+Y)."},
                 "Cancel": {"caption":
                            "Purge pending edits and close current editor " +
                            "without saving."},
                 "More": {"display": "+",
                          "caption":
                          "Add another input field."},
                 "Fewer": {"display": "-",
                           "caption":
                           "Remove an input field."},
                 "Max More": {"caption":
                              "Cannot add fields to list. Max reached."},
                 "Min Fewer": {"caption":
                               "Cannot remove fields from list. Min reached."}}
        for key in texts.keys():
            self.texts[key] = texts_template.copy()
            for this, do_it in texts[key].items():
                self.texts[key][this] = do_it

    # Text-widget make functions
    # ============================================================
    def make_text_subttl_wdg(self, p_text_key: str):
        """Create a sub-title text widget. Save it with metadata.

        :args: p_text_key: str - key to text metadata
        :returns: QLabel object
        """
        stt = SS.set_subtitle_style(
            QLabel(self.texts[p_text_key]["display"]))
        self.texts[p_text_key]["active"] = True
        self.texts[p_text_key]["widget"] = stt
        return (stt)

    def make_text_status_wdg(self, p_text_key: str):
        """Create a status/info text widget. Save it with metadata.

        :args: p_text_key: str - key to text metadata
        :returns: QLabel object
        """
        sta = SS.set_status_style(
            QLabel(self.texts[p_text_key]["display"]))
        self.texts[p_text_key]["active"] = True
        self.texts[p_text_key]["widget"] = sta
        return (sta)

    def make_text_input_wdg(self,
                            p_text_key: str,
                            p_readonly: bool = True):
        """Create a text input widget. Save it with metadata.

        :args:
            p_text_key: str - name of the text input
            p_readonly: bool - whether the input is read-only
        :returns: QLineEdit object
        """
        txt_wdg = SS.set_line_edit_style(QLineEdit(), False)
        hint = self.get_hint(p_text_key)
        txt_wdg.setPlaceholderText(hint)
        txt_wdg.setToolTip(hint)
        txt_wdg.setReadOnly(p_readonly)
        txt_wdg.setEnabled(True)
        self.texts[p_text_key]["active"] = True
        self.texts[p_text_key]["widget"] = txt_wdg
        return (txt_wdg)

    # Helper and Slot Actions for Text Widgets
    # ==============================================================
    def activate_texts(self, p_txts: list):
        """Activate selected set of input text widgets."""
        for inp_nm in p_txts:
            inp = self.texts[inp_nm]
            inp["widget"].setStyleSheet(SS.get_style("active_editor"))
            inp["widget"].setEnabled(True)
            inp["active"] = True

    def deactivate_texts(self, p_txts: list):
        """Deactivate specified set of input text widgets."""
        for inp_nm in p_txts:
            inp = self.texts[inp_nm]
            inp["widget"].setStyleSheet(SS.get_style("inactive_editor"))
            inp["widget"].setEnabled(False)
            inp["active"] = False

    def get_hint(self, p_text_key: str) -> str:
        """Return the hint (placeholder) value for a text item.

        :args: p_text_key: str - key to the text metadata
        :returns: str - the hint value
        """
        return (self.texts[p_text_key]["hint"])

    def set_cursor_result(self,
                          p_text: str = ""):
        """Assign text to Cursor result display."""
        self.activate_texts(["Cursor"])
        self.texts["Cursor"]["widget"].setText(p_text)

    def get_search_value(self):
        """Return value of the search/find text input widget.

        The search is for key values only.
        Adjust it to work as a wildcard search on redis by
          preceding and ending with asterisks.
        Include the rectyp name in the search text.
        Cast to lower case.

        :returns: tuple (
            db name cast lower for use on redis,
            search key value modified for use on redis)
        """
        db_nm, rectyp_nm = self.get_active_db_rectyp()
        search_key = self.texts["Key"]["widget"].text().strip()
        db_nm = db_nm.lower()
        rectyp_nm = rectyp_nm.lower()
        search_key = self.edit["redis_key"](search_key)
        if f"{rectyp_nm}:" not in search_key:
            search_key = f"{rectyp_nm}:{search_key}"
        if search_key[:1] != "*":
            search_key = "*" + search_key
        if search_key[-1:] != "*":
            search_key += "*"
        return (db_nm, search_key.lower())

    def show_status(self, p_text_nm: str):
        """Display text in dbe status bar text relevant to event.
        """
        if p_text_nm not in (None, "") \
            and p_text_nm in self.texts \
            and ("caption" in self.texts[p_text_nm] or
                 "display" in self.texts[p_text_nm]):
            if "caption" in self.texts[p_text_nm]:
                self.texts["dbe_status"]["widget"].setText(
                    self.texts[p_text_nm]["caption"])
            else:
                self.texts["dbe_status"]["widget"].setText(
                    self.texts[p_text_nm]["display"])

    def prep_editor_action(self,
                           p_action_nm: str):
        """Common functions used by DB Editor actions

        :args: p_action_nm - name of button or other widget that
            triggered the actione)
        """
        self.show_status(p_action_nm)
        self.set_cursor_result()

    # Push-Button Widget Creation
    # ============================================================

    def set_buttons_meta(self):
        """Define metadata for DB Editor button actions.

        Buttons are organized into groups, which facilitates
        containing into V and H boxes.  Help texts associated
        with buttons are defined in texts metadata.

        @DEV:
        - Could be further abstracted via BowQuiver.saskan_buttons.
        - Could add icons
        - Maybe can do some action slots here? E.g., if they
          can be handled entirely within the scope of this class.
        """
        self.buttons: dict = dict()
        button_template = {
            "icon": None,
            "keycmd": str(),
            "active": True,
            "action": None,
            "widget": None}
        self.buttons = {
            "Get": {"Find": {},
                    "Next": {},
                    "Prev": {}},
            "Edit": {"Add": {},
                     "Delete": {},
                     "Save": {},
                     "Undo": {},
                     "Redo": {},
                     "Cancel": {"action": self.push_cancel}},
            "List": {"More": {"action": self.add_row_to_list},
                     "Fewer": {"action": self.remove_row_from_list}}}
        for grp in self.buttons.keys():
            for btn_nm in self.buttons[grp].keys():
                for item in button_template.keys():
                    if item not in self.buttons[grp][btn_nm].keys():
                        self.buttons[grp][btn_nm][item] = button_template[item]

    # Push-button helper functions
    # ============================================================

    def make_push_button_wdg(self,
                             p_grp: str,
                             p_btn_name: str,
                             p_list_name: str = None):
        """Instantiate a push button object.

        By default, they are set up in an inactive state.

        :args:
            p_grp - metadata group for the button
            p_btn_name - metadata key / button name
            p_list_name - field_name for repeat-lists, add to button name
        :returns: QPushButton object
        """
        btn_text = p_btn_name
        list_nm = (":" + p_list_name) if p_list_name is not None else ""
        if p_btn_name in self.texts and \
            "display" in self.texts[p_btn_name] and \
                self.texts[p_btn_name]["display"] not in (None, "", [], {}):
            btn_text = self.texts[p_btn_name]["display"]
        btn = SS.set_button_style(QPushButton(btn_text), False)
        btn.setObjectName(f"{p_grp}.{p_btn_name}{list_nm}.btn")
        btn.setEnabled(False)
        if self.buttons[p_grp][p_btn_name]["action"] is not None:
            btn.clicked.connect(self.buttons[p_grp][p_btn_name]["action"])
        self.buttons[p_grp][p_btn_name]["widget"] = btn
        self.buttons[p_grp][p_btn_name]["active"] = False
        return (btn)

    def make_button_group_wdg(self,
                              p_grp: str,
                              p_list_name: str = None,
                              p_use_stt: bool = True,
                              p_activate: bool = False):
        """Make containers and put buttons in them.

        Default is that buttons are not activated.
        Optionally include a subtitle with it.
        Optionally activate buttons.

        :args:
            p_grp: str - name of the button group
            p_list_name: str - name to add to button, for list items (optional)
            p_use_stt: bool - whether to include a subtitle (optional)
            p_activate: bool - whether to activate buttons (optional)
        :returns: QVBoxLayout object
        """
        list_nm = p_list_name if p_list_name is not None else ""
        vbox = QVBoxLayout()
        if p_use_stt:
            vbox.addWidget(self.make_text_subttl_wdg(p_grp))
        hbox = QHBoxLayout()
        hbox.LeftToRight
        btn_list = list()
        for btn_nm, btn_attrs in self.buttons[p_grp].items():
            btn = self.make_push_button_wdg(p_grp, btn_nm, list_nm)
            btn_list.append(btn_nm)
            hbox.addWidget(btn)
        if p_activate:
            self.activate_buttons(p_grp, btn_list)
        hbox.addStretch()
        hbox.addSpacing(30)
        vbox.addLayout(hbox)
        return (vbox)

    # Push-button action slots and related helper methods
    # ============================================================

    def activate_buttons(self,
                         p_grp: str,
                         p_btns: list):
        """Activate selected set of push buttons

        :args:
            p_grp: str name of button group
            p_btns: list of button names in group
        """
        for btn_nm in p_btns:
            btn = self.buttons[p_grp][btn_nm]
            btn["widget"].setStyleSheet(SS.get_style("active_button"))
            btn["widget"].setEnabled(True)
            btn["active"] = True

    def deactivate_buttons(self,
                           p_grp: str,
                           p_btns: list):
        """Deactivate a specified set of push buttons

        :args:
            p_grp: str name of button group
            p_btns: list of button names in group
        """
        for btn_nm in p_btns:
            btn = self.buttons[p_grp][btn_nm]
            btn["widget"].setStyleSheet(SS.get_style("inactive_button"))
            btn["widget"].setEnabled(False)
            btn["active"] = False

    def select_record_type(self, p_rectyp_nm: str):
        """Generic function for record type selection actions.

        :args:
            p_rectyp_nm: name of selected record type"""
        self.show_status(p_rectyp_nm)
        self.activate_rectyp(p_rectyp_nm)

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        self.select_record_type("Configs")

    def select_status(self):
        """Slot for Editor Select Status Flags radio check action"""
        self.select_record_type("Status")

    def select_topics(self):
        """Slot for Editor Select Topics radio check action"""
        self.select_record_type("Topics")

    def push_cancel(self):
        """Slot for Editor Edit Push Button --> Cancel"""
        self.show_status("Cancel")
        self.deactivate_rectyp()

    def add_row_to_list(self):
        """Add an input row to form for list of fields.
        """
        list_nm = self.sender().objectName().split(":")[1].split(".")[0]
        list_values, list_form = self.get_list_fields(list_nm)
        rowcnt = len(list_values)
        if rowcnt > 4:
            self.show_status("Max More")
        else:
            self.show_status("More")
            db, rectyp = self.get_active_db_rectyp()
            edit_rules = [fld[1] for fld in
                          self.rectyps[db][rectyp]["value_fields"]
                          if fld[0] == list_nm][0]
            edit_wdg = SS.set_line_edit_style(QLineEdit())
            edit_wdg = self.apply_pre_edits(edit_rules, edit_wdg)
            list_form.insertRow(rowcnt, list_nm, edit_wdg)

    def remove_row_from_list(self):
        """Remove one input row from the form for list of field.
        """
        list_nm = self.sender().objectName().split(":")[1].split(".")[0]
        list_values, list_form = self.get_list_fields(list_nm)
        rowcnt = len(list_values)
        if rowcnt < 2:
            self.show_status("Min Fewer")
        else:
            self.show_status("Fewer")
            list_form.removeRow(rowcnt - 1)

    # Record Type Editor Widget Creation
    # ============================================================

    def set_rectyp_meta(self):
        """Define metadata for the DB Editors for each Record Type.

        The 'rectyp' widget is a container for input rows and buttons
        for each Record Type. This metadata is used to generate both
        the editor widget and items in a radio button group to select
        which rectyp to edit.

        Each 'rectyp' widget holds one or more form widgets and may
        also have some buttons, subtitles and other objects.

        Each form widget holds one or more input rows.
        In some cases, the number of input rows may be variable,
        per user inputs.

        There are edit rules for each input line.

        Some are hard-coded at the field-group (form layout) level.

        Key values are required, must be lower case,
        must not contain blanks, must contain a record type name in
        the first instance, only punctuation allowed in colon.
        These get auto-corrected.

        Values for Config and Status records are required.

        Value for Audit fields are always auto-generated, so there
        are not any edit rules for them and they cannot be changed
        by manual edits.

        @DEV:
        - Consider advantages/disadvantages of breaking out
          the meta into a separate json or other config file.

        Metadata edit rules are defined on value_fields forms only,
        as follows:

        - If no meta-data-driven rules are needed, then each value field
          is a list containiing only a string defining label content. Like:
            "value_fields": [["Field Name"], ["Field Value"]],

        - If meta-data-driven rules are needed, then the value field is
          defined as a list of two items, the label text and a set of
          1 to n rule names. Like:
            "value_fields":
            [["Host", ("notnull")],
             ["Port", ("notnull", "posint")]]

        - If meta-data-driven rule is complex in the sense that a particular
          input mask or regex is used, then there will be a rule name
          associated with that edit. Like:
            "audit_fields":
            [["Last Updated", ("datetime")]]

        - This also applies to values that take only values from an
          enumerated list. Like:
            "value_fields":
            [["Host", ("notnull", "hostlist")]]

        - Metadata-defined edit rules are:
            notnull -- cannot be empty set or all spaces
            number -- can be pos, neg or zero real
            posreal -- positive real number
            posint -- positive integer
            date -- Input mask or regex YYYYMMDD
            datetime -- Input mask or regex YYYYMMDDHHMMSS.SSS
            link -- must follow rules for key values
            list -- may occur 1 to x times

        @DEV:

        #   Qt tricks to try out:
        #   - use .setValidator() to trap for bad input. It provides a
        #     QtGui.QValidator object that can be used to trap for bad input.
        #     There are standard validators for Int, Double and Regex.
        #     Regex is probably the best way to do it.
        #     Some designers don't like the Qt validator because I guess
        #     it does not provide user feedback on bad input.

        #   - Check for conditions like .isModified(), .textChanged(),
        #      .textEdited(), .returnPressed(), .editingFinished(),
        #      Not sure when to use. On Add / Save clicks?

        #      .hasAcceptableInput() <-- to validate input vs a InputMask

        #   - Set an inputMask for specific patterns, for example,
        #           X = any non-blank character
        #           9 = any digit required
        #           < = all following characters are lower-cased

        #    - do an .isNumber() check

        #   - all values are stored as strings, but can have data types

        # - auto-corrects on some values
        #   - strip all values of leading and trailing white spaces
        #   - see redis_io.py for code on...
        #       - bump_stray_underbars()

        #  - auto-corrects on key values (see redis_io.py for code on...)
        #     - convert_to_spine() =
        #       - bump_stray_underbars() +
        #       - bump_char_to_underbar() +
        #       - make_lower_spine()

        # - if edits applied and verifications passed,
        # - then provide audit values, including hash key
        #   This would be done as a separate request since
        #   it may depend on whether doing an add, update,
        #   logical delete or physical delete.
        #   (see redis_io.py for code on...)
        #    - add_audit_values() =
        #      - set_version() +
        #      - set_timestamp() +
        #      - set_hash()

        """
        rectyp_template = {
            "db": str(),
            "key_fields": None,
            "value_fields": None,
            "active": False,
            "selector": None,
            "select_action": None,
            "widget": None}
        self.rectyps = {
            "Basement": {
                "Configs": {
                    "key_fields":
                    [["Config Category", ("notnull")],
                     ["Config ID", ("notnull")]],
                    "value_fields":
                    [["Field Name", ("notnull")],
                     ["Field Value", ("notnull")]],
                    "select_action": self.select_configs},
                "Status": {
                    "key_fields":
                    [["Status Category", ("notnull")],
                     ["Status ID", ("notnull")]],
                    "value_fields":
                    [["Field Name", ("notnull")],
                     ["Field Value", ("notnull")]],
                    "select_action": self.select_status},
                "Expire Rules": {},
                "Retry Rules": {}},
            "Schema":  {
                "Topics": {
                    "key_fields":
                    [["Topic Category", ("notnull")],
                     ["Topic ID", ("notnull")]],
                    "value_fields":
                    [["Host", ("notnull", "hostlist")],
                     ["Port", ("notnull", "posint")],
                     ["Channel ID", ("notnull")],
                     ["Caption"],
                     ["Description"],
                     ["Plans", ("notnull", "link", "list")]],
                    "select_action": self.select_topics},
                "Plans": {},
                "Services": {},
                "Schemas": {}},
            "Harvest": {
                "Response": {}},
            "Log": {
                "Activator Log": {},
                "Request Log": {},
                "Response Log": {}},
            "Monitor": {
                "Server Monitor": {},
                "Requests Monitor": {},
                "Responses Monitor": {}}}
        for key in self.rectyps.keys():
            for rectyp in self.rectyps[key].keys():
                for field, value in rectyp_template.items():
                    if field not in self.rectyps[key][rectyp].keys():
                        self.rectyps[key][rectyp][field] = value

    # Record Type Editor Widget make functions
    # ============================================================

    def make_rectyp_selectors(self):
        """Return collection(s) of radio buttons for selecting rectyp.

        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        vbox.addWidget(self.make_text_subttl_wdg("Types"))
        for db in self.rectyps.keys():
            hbox = QHBoxLayout()
            hbox.LeftToRight
            for rectyp in self.rectyps[db].keys():
                rdo_btn = SS.set_radiobtn_style(QRadioButton(rectyp))
                if self.rectyps[db][rectyp]["select_action"] is not None:
                    rdo_btn.clicked.connect(
                        self.rectyps[db][rectyp]["select_action"])
                hbox.addWidget(rdo_btn)
                self.rectyps[db][rectyp]["selector"] = rdo_btn
            hbox.addStretch(1)
            vbox.addLayout(hbox)
        return (vbox)

    def apply_pre_edits(self,
                        p_edit_rules: set,
                        p_edit_wdg: QLineEdit):
        """Format edit attributes of form line edit item

        :args:
            (Qt object) The edit item widget
            (set) Names of edit rules for the edit item
        :returns: Modified edit widget
        """
        edit_wdg = p_edit_wdg
        hint = ""
        if "notnull" in p_edit_rules:
            edit_wdg.setValidator(QRegExpValidator(
                QRegExp("[^\s]+"), edit_wdg))       # noqa W605
            hint += " required"
            edit_wdg.setPlaceholderText("Required")
        if "posint" in p_edit_rules:
            edit_wdg.setValidator(QIntValidator(edit_wdg))
            hint += " positive integer"
        if "link" in p_edit_rules:
            hint += f" {self.texts['Key']['hint']}"
        if hint != "":
            edit_wdg.setPlaceholderText(hint)
            edit_wdg.setToolTip(hint)
        return (edit_wdg)

    def make_rectyp_wdg(self,
                        db_nm: str,
                        rectyp_nm: str):
        """Return a container widget for selected db+record type.

        :returns: QWidget object containing a QVBoxLayout object
                  containing several Label widgets (sub-titles),
                  specialized edit buttons (like for list length),
                  and Form layouts (rows of related edit fields).
        """
        rectyp_wdg = QWidget()
        rectyp_layout = QVBoxLayout()
        rectyp_layout.addWidget(self.make_text_subttl_wdg(rectyp_nm))
        for f_grp in ["key_fields", "value_fields"]:
            if self.rectyps[db_nm][rectyp_nm][f_grp] is not None:
                # Add sub-title for group of fields
                rectyp_layout.addWidget(self.make_text_subttl_wdg(f_grp))
                form = QFormLayout()
                form_nm = f"{db_nm}:{rectyp_nm}:{f_grp}"
                form.setObjectName(form_nm)
                form.setLabelAlignment(Qt.AlignRight)
                for field in self.rectyps[db_nm][rectyp_nm][f_grp]:
                    field_nm = field[0]
                    edit_rules = field[1] if len(field) > 1 else ()
                    if "list" in edit_rules:
                        # Handle inputs where a list of values is allowed
                        list_vbox = QVBoxLayout()
                        list_vbox.setObjectName(
                            f"{db_nm}:{rectyp_nm}:{field_nm}.box")
                        list_form = QFormLayout()
                        list_form.setObjectName(
                            f"{db_nm}:{rectyp_nm}:{field_nm}.frm")
                        edit_wdg = SS.set_line_edit_style(QLineEdit())
                        edit_wdg = self.apply_pre_edits(edit_rules, edit_wdg)
                        list_form.addRow(field_nm, edit_wdg)
                        list_vbox.addLayout(list_form)
                        list_vbox.addLayout(
                            self.make_button_group_wdg(
                                "List", field_nm, False, True))
                        form.addRow(list_vbox)
                    else:
                        edit_wdg = SS.set_line_edit_style(QLineEdit())
                        edit_wdg = self.apply_pre_edits(edit_rules, edit_wdg)
                        form.addRow(field_nm, edit_wdg)
                rectyp_layout.addLayout(form)
        rectyp_wdg.setLayout(rectyp_layout)
        self.rectyps[db_nm][rectyp_nm]["widget"] = rectyp_wdg
        rectyp_wdg.hide()
        return (rectyp_wdg)

    # Record Type Editor Widget helper functions
    # ============================================================

    def get_active_db_rectyp(self):
        """Identify active db and record type.

        :returns: tuple (db name key, rectyp type key)
        """
        db_nm = None
        rectyp_nm = None
        done = False
        for db in self.rectyps.keys():
            for rectyp, attrs in self.rectyps[db].items():
                if attrs["active"]:
                    db_nm = db
                    rectyp_nm = rectyp
                    done = True
                    break
            if done:
                break
        return (db_nm, rectyp_nm)

    def get_key_fields(self):
        """Get name and value from fields on the Keys form
        of the active record type.

        :returns: tuple (
            dict of field name:field value,
            key value as used on database)

        @DEV:
        - I am losing the "ID" part of the key.
        - Started after adding verification and audit-gen logic.
        - Figure it out and fix it!! :-)
        """
        db, rectyp = self.get_active_db_rectyp()
        form_keys = dict()
        form_nm = f"{db}:{rectyp}:key_fields"
        key_form = \
            self.rectyps[db][rectyp]["widget"].findChild(QFormLayout, form_nm)
        for key_idx, key in enumerate(self.rectyps[db][rectyp]["key_fields"]):
            name = key_form.itemAt(
                key_idx, QFormLayout.LabelRole).widget().text()
            value = key_form.itemAt(
                key_idx, QFormLayout.FieldRole).widget().text()
            form_keys[name] = value
        # Use bump logic here to remove unwanted characters
        db_key = ":".join(form_keys.values()).lower()
        if (rectyp.lower() + ":") not in db_key:
            db_key = f"{rectyp.lower()}:{db_key}"
        db_key = self.edit["redis_key"](db_key)
        return (form_keys, db_key)

    def get_list_fields(self,
                        p_field_nm: str):
        """Get specified list form for the active record type.

        And for the requested list-of-values field name.

        :returns: tuple (
            list of field values,
            QFormLayout object)
        """
        db, rectyp = self.get_active_db_rectyp()
        list_form = None
        list_values = []
        list_form = \
            self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout, f"{db}:{rectyp}:{p_field_nm}.frm")
        for link_idx in range(list_form.rowCount()):
            value = list_form.itemAt(
                link_idx, QFormLayout.FieldRole).widget().text()
            list_values.append(value)
        return (list_values, list_form)

    def get_value_fields(self,
                         p_links_only: bool = False):
        """Get name and value from all fields on all sub-forms,
        excluding the Keys forms, for the active record type.
        """
        db, rectyp = self.get_active_db_rectyp()
        form_values: dict = {}
        form_rows = \
            self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout, f"{db}:{rectyp}:value_fields")
        for val_idx, val in enumerate(
                self.rectyps[db][rectyp]["value_fields"]):
            edit_rules = val[1] if len(val) > 1 else ()
            if "list" in edit_rules:
                name = val[0]
                value, _ = self.get_list_fields(name)
            else:
                name = form_rows.itemAt(
                    val_idx, QFormLayout.LabelRole).widget().text()
                value = form_rows.itemAt(
                    val_idx, QFormLayout.FieldRole).widget().text()
            if (not p_links_only) or (p_links_only and "link" in edit_rules):
                form_values[name] = value
        return (form_values)

    def get_all_fields(self):
        """Get all the field names and values for active edit form.

        :returns: (tuple)
            ( db name in lower case, as used on redis,
              dict {field name:field value, ...} in db record format)

        @DEV:
        - Add audit fields here?
        """
        db_nm, _ = self.get_active_db_rectyp()
        form_keys, db_key = self.get_key_fields()
        record = {"name": db_key}
        values = self.get_value_fields()
        for name, value in values.items():
            record[name] = value
        return (db_nm.lower(), record)

    def activate_rectyp(self,
                        p_rec: str):
        """Deactivate a Record Type Edit widget.

        :args: p_rec: str name of record type editor widget to activate.
        """
        done = False
        self.deactivate_rectyp()
        for db in self.rectyps.keys():
            for rectyp, attrs in self.rectyps[db].items():
                if rectyp == p_rec and attrs["active"] is False:
                    attrs["active"] = True
                    attrs["widget"].show()
                    self.activate_buttons("Edit", ["Add", "Cancel"])
                    self.activate_buttons("Get", ["Find"])
                    self.activate_texts(["Key", "Cursor"])
                    self.prep_editor_action(p_rec)
                    done = True
                    break
            if done:
                break

    def deactivate_rectyp(self):
        """Deactivate the active Record Type Edit widget."""
        done = False
        for db in self.rectyps.keys():
            for rectyp, attrs in self.rectyps[db].items():
                if attrs["active"]:
                    attrs["active"] = False
                    attrs["selector"].setChecked(False)
                    attrs["widget"].hide()
                    self.deactivate_buttons("Edit",
                                            ["Add", "Delete", "Save",
                                             "Undo", "Redo", "Cancel"])
                    self.deactivate_buttons("Get", ["Find", "Next", "Prev"])
                    self.deactivate_texts(["Key", "Cursor"])
                    done = True
                    break
            if done:
                break

    def run_rectyp_edits(self) -> bool:
        """Run the edits associated with the active record type.

        These are executed when an Add or Save button is pressed.

        :returns: (bool) True if all edits pass else False
        """
        db, rectyp = self.get_active_db_rectyp()
        form_keys, _ = self.get_key_fields()
        form_values = form_keys | self.get_value_fields()
        edits_passed = True
        error_msg = ""
        for f_grp in ["key_fields", "value_fields"]:
            for field in self.rectyps[db][rectyp][f_grp]:
                field_nm = field[0]
                edit_rules = field[1] if len(field) > 1 else ()
                if "notnull" in edit_rules:
                    if form_values[field_nm] in (None, "", [], {}):
                        error_msg = f"{field_nm} is required. "
                        edits_passed = False
                        break
                if "hostlist" in edit_rules:
                    if not (self.edit["hostlist"](form_values[field_nm])):
                        error_msg = "Invalid host name. "
                        edits_passed = False
                        break
            if not edits_passed:
                self.set_cursor_result(error_msg)
                break
        return (edits_passed)

    # Database Editor Widget make function
    # ============================================================

    def make_db_editor_wdg(self):
        """Create all components of Data Base Editor widget.
        """
        self.setGeometry(620, 40, 550, 840)
        self.dbe_layout = QVBoxLayout()
        self.dbe_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.dbe_layout)
        self.dbe_layout.addLayout(self.make_rectyp_selectors())
        vbox = self.make_button_group_wdg("Get")
        vbox.addWidget(self.make_text_input_wdg("Key", False))
        self.dbe_layout.addLayout(vbox)
        self.dbe_layout.addLayout(self.make_button_group_wdg("Edit"))
        self.dbe_layout.addWidget(self.make_text_input_wdg("Cursor"))
        for db, rectyps in self.rectyps.items():
            for rectyp in rectyps.keys():
                self.dbe_layout.addWidget(self.make_rectyp_wdg(db, rectyp))
        self.dbe_layout.addWidget(self.make_text_status_wdg("dbe_status"))
        self.show()
