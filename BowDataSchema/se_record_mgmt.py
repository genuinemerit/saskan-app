#!/usr/bin/python3.9
"""
:module:    se_record_mgmt.py

:author:    GM (genuinemerit @ pm.me)
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
# from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
# from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()


class RecordMgmt(QWidget):
    """Handle set-up, set, get for predefined record types.

    Closely related to the DB Editor Widget Class.
    """
    def __init__(self, parent: QWidget, DBE: object):
        """super() call is required.

        The DB editor widget is also passed in.
        """
        super().__init__(parent)
        self.DBE = DBE
        self.set_edits_meta()
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

        def bump_redis_key(text: str):
            """Convert anything not a letter or colon to underbar.
            And make it lowercase.
            """
            r_str = text
            for char in r_str:
                if not char.isalpha() and \
                   not char.isdigit() and \
                   not char == ":":
                    r_str = r_str.replace(char, "_")
            return bump_underbars(r_str)

        def verify_host(p_value: str):
            """Validate value against enumerated list."""
            if p_value in ["localhost", "curwen"]:
                return True
            else:
                return False

        self.mask = {"date": "0000-00-00",
                     "lower": "<"}
        self.edit = {"redis_key": bump_redis_key,
                     "hostlist": verify_host}

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

        Values for Audit fields are auto-generated, so there
        are not any edit rules for them and they cannot be changed
        by manual edits. The structure of Audit fields is defined
        in this Class, but separately from the record types.

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
            auto -- field is populated by system, cannot be edited
            date -- Input mask or regex YYYYMMDD
            datetime -- Input mask or regex YYYYMMDDHHMMSS.SSS
            link -- must follow rules for key values
            list -- may occur 1 to x times
            notnull -- cannot be empty set or all spaces
            number -- can be pos, neg or zero real
            posint -- positive integer
            posreal -- positive real number
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
                    "select_action": self.DBE.select_configs},
                "Status": {
                    "key_fields":
                    [["Status Category", ("notnull")],
                     ["Status ID", ("notnull")]],
                    "value_fields":
                    [["Field Name", ("notnull")],
                     ["Field Value", ("notnull")]],
                    "select_action": self.DBE.select_status},
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
                    "select_action": self.DBE.select_topics},
                "Plans": {},
                "Services": {},
                "Schemas": {}},
            "Harvest": {
                "Queues": {
                    "key_fields":
                    [["Hash ID", ("auto")]],
                    "value_fields":
                    [["Queue Value", ("auto", "list")]],
                    "select_action": self.DBE.select_queues},
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

        self.audit_fields = [
            ["Expiry Time", ("auto", "datetime")],
            ["Hash ID", ("auto")],
            ["Last Updated", ("auto", "datetime")],
            ["Version", ("auto")]
        ]

    # Record Type Editor Widget make functions
    # ============================================================

    def make_rectyp_selectors(self):
        """Return collection(s) of radio buttons for selecting rectyp.

        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        vbox.addWidget(self.DBE.make_text_subttl_wdg("Types"))
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
        if "auto" in p_edit_rules:
            edit_wdg.setReadOnly(True)
            hint += " automatically generated"
        if "notnull" in p_edit_rules:
            edit_wdg.setValidator(QRegExpValidator(
                QRegExp("[^\s]+"), edit_wdg))       # noqa W605
            hint += " required"
        if "posint" in p_edit_rules:
            edit_wdg.setValidator(QIntValidator(edit_wdg))
            hint += " positive integer"
        if "link" in p_edit_rules:
            hint += f" {self.DBE.texts['Key']['hint']}"  # type: ignore
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
        rectyp_layout.addWidget(
            self.DBE.make_text_subttl_wdg(rectyp_nm))  # type: ignore
        for f_grp in ["key_fields", "value_fields"]:
            if self.rectyps[db_nm][rectyp_nm][f_grp] is not None:
                # Add sub-title for group of fields
                rectyp_layout.addWidget(
                    self.DBE.make_text_subttl_wdg(f_grp))  # type: ignore
                form = QFormLayout()
                form_nm = f"{db_nm}:{rectyp_nm}:{f_grp}.frm"
                form.setObjectName(form_nm)
                form.setLabelAlignment(Qt.AlignRight)
                for field in self.rectyps[db_nm][rectyp_nm][f_grp]:
                    field_nm = field[0]
                    edit_rules = field[1] if len(field) > 1 else ()
                    if "list" in edit_rules:
                        # Handle inputs where a list of values is allowed
                        # Move this to a separate function
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
                        # If values are set automatically, then do not
                        # provide add/remove buttons
                        if "auto" not in edit_rules:
                            list_vbox.addLayout(
                                self.DBE.make_button_group_wdg(  # type: ignore
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

    def get_key_fields(self,
                       p_db_nm: str = None,
                       p_rectyp_nm: str = None):
        """Get name and value from fields on the Keys form
        of the active record type.

        if db or rectype not specified, use active db and rectype.

        :returns: tuple (
            dict of field name:field value,
            key value as used on database)
        """
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.get_active_db_rectyp()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
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
                        p_field_nm: str,
                        p_db_nm: str = None,
                        p_rectyp_nm: str = None):
        """Get specified list form for the active record type.

        And for the requested list-of-values field name.
        If db or rectype not specified, use active db and rectype.

        :returns: tuple (
            list of field values,
            QFormLayout object)
        """
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.get_active_db_rectyp()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
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
                         p_links_only: bool = False,
                         p_db_nm: str = None,
                         p_rectyp_nm: str = None):
        """Get name and value from all fields on all sub-forms,
        excluding the Keys forms, for the active record type.

        If db or rectype not specified, use active db and rectype.
        """
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.get_active_db_rectyp()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
        form_values: dict = {}
        form_rows = \
            self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout, f"{db}:{rectyp}:value_fields")
        for val_idx, val in enumerate(
                self.rectyps[db][rectyp]["value_fields"]):
            edit_rules = val[1] if len(val) > 1 else ()
            if "list" in edit_rules:
                name = val[0]
                value, _ = self.get_list_fields(name, db, rectyp)
            else:
                name = form_rows.itemAt(
                    val_idx, QFormLayout.LabelRole).widget().text()
                value = form_rows.itemAt(
                    val_idx, QFormLayout.FieldRole).widget().text()
            if (not p_links_only) or (p_links_only and "link" in edit_rules):
                form_values[name] = value
        return (form_values)

    def get_all_fields(self,
                       p_db_nm: str = None,
                       p_rectyp_nm: str = None):
        """Get all the field names and values for active edit form.

        if db and rectype not specified, use active db and rectype.

        :returns: (tuple)
            ( db name in lower case, as used on redis,
              dict {field name:field value, ...} in db record format)
        """
        if p_db_nm is None:
            db, rectyp = self.get_active_db_rectyp()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
        form_keys, db_key = self.get_key_fields(db, rectyp)
        record = {"name": db_key}
        values = self.get_value_fields(False, db, rectyp)
        for name, value in form_keys.items():
            record[name] = value
        for name, value in values.items():
            record[name] = value
        return (db.lower(), record)

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
        form_keys, _ = self.get_key_fields(db, rectyp)
        form_values = form_keys | self.get_value_fields(False, db, rectyp)
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
        """Create record type forms for the Data Base Editor widget.
        """
        self.DBE.dbe_layout.addLayout(self.make_rectyp_selectors())
        for db, rectyps in self.rectyps.items():
            for rectyp in rectyps.keys():
                self.DBE.dbe_layout.addWidget(
                    self.make_rectyp_wdg(db, rectyp))
        # self.DBE.show()
