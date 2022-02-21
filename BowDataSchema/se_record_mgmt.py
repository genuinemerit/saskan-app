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
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from redis_io import RedisIO                    # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

RI = RedisIO()
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
                "Queues": {
                    "key_fields":
                    [["Hash ID", ("auto")]],
                    "value_fields":
                    [["Queue Value", ("auto", "list")]],
                    "select_action": self.select_queues},
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

    # Record Type Selector Widgets make functions
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

    # Record Type Selector helper and slot functions
    # ============================================================

    def select_record_type(self, p_rectyp_nm: str):
        """Generic function for record type selection actions.

        :args:
            p_rectyp_nm: name of selected record type"""
        print(f"Activating {p_rectyp_nm}")
        self.activate_rectyp(p_rectyp_nm)
        self.DBE.set_dbe_status(p_rectyp_nm)        # type: ignore

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        print("Select Configs")
        self.select_record_type("Configs")

    def select_status(self):
        """Slot for Editor Select Status Flags radio check action"""
        self.select_record_type("Status")

    def select_topics(self):
        """Slot for Editor Select Topics radio check action"""
        self.select_record_type("Topics")

    def select_queues(self):
        """Slot for Editor Select Queues radio check action"""
        self.select_record_type("Queues")

    # Record Type Editor Widget make functions
    # ============================================================

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
        fields_nm = "key_fields"
        form_nm = f"{db}:{rectyp}:{fields_nm}.frm"
        key_form = \
            self.rectyps[db][rectyp]["widget"].findChild(QFormLayout, form_nm)
        for key_idx, key in enumerate(
                self.rectyps[db][rectyp][fields_nm]):
            pp(("key_idx, key", key_idx, key))
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
                         p_db_nm: str = None,
                         p_rectyp_nm: str = None,
                         p_links_only: bool = False,):
        """Get name and value from all fields on all sub-forms,
        excluding the Keys forms, for the active record type.

        If db or rectype not specified, use active db and rectype.
        """
        db = p_db_nm
        rectyp = p_rectyp_nm
        form_values: dict = {}

        all_rows = self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout)
        pp(("values... all_rows", all_rows))

        fields_nm = "value_fields"
        form_nm = f"{db}:{rectyp}:{fields_nm}.frm"
        form_rows = \
            self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout, f"{db}:{rectyp}:{form_nm}")
        pp(("values... form_nm", form_nm))
        pp(("values... form_rows", all_rows))

        for val_idx, val in enumerate(
                self.rectyps[db][rectyp][fields_nm]):
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
        values = self.get_value_fields(db, rectyp)
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
                    self.DBE.activate_buttons(      # type: ignore
                        "Edit", ["Add", "Cancel"])
                    self.DBE.activate_buttons(      # type: ignore
                        "Get", ["Find"])
                    self.DBE.activate_texts(        # type: ignore
                        ["Key", "Cursor"])
                    self.DBE.prep_editor_action(p_rec)  # type: ignore
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
                    self.DBE.deactivate_buttons(
                        "Edit", ["Add", "Delete", "Save",
                                 "Undo", "Redo", "Cancel"])
                    self.DBE.deactivate_buttons(
                        "Get", ["Find", "Next", "Prev"])
                    self.DBE.deactivate_texts(["Key", "Cursor"])
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
        form_values = form_keys | self.get_value_fields(db, rectyp)
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
                self.DBE.set_dbe_status("", error_msg)  # type: ignore
                break
        return (edits_passed)

    # Database Editor Widget make function
    # ============================================================

    def make_db_editor_wdg(self):
        """Create record type forms for the Data Base Editor widget.

        And create selector checkboxes for record types.
        """
        self.DBE.dbe_layout.addLayout(self.make_rectyp_selectors())
        for db, rectyps in self.rectyps.items():
            for rectyp in rectyps.keys():
                self.DBE.dbe_layout.addWidget(
                    self.make_rectyp_wdg(db, rectyp))
        # Enable rec mgmt related button actions
        for key, act in {
                ("Edit", "Add"): self.add_record_to_db,
                ("Get", "Find"): self.find_record_keys}.items():
            # Refactor these to use a dict
            wdg = self.DBE.buttons[key[0]][key[1]]["widget"]
            wdg.clicked.connect(act)

    # Edit Trigger Actions
    # =====================
    def get_searchkey_value(self,
                            p_rectyp: str):
        """Return value of the search/find text input widget.

        The search is for key values only.
        Adjust it to work as a wildcard by
          preceding and ending with asterisks.
        Add rectyp name in the search text.
        Cast to lower case.

        :returns: tuple (
            db name cast lower for use on redis,
            search key value modified for use on redis)
        """
        search_key = \
            self.DBE.texts["Key"]["widget"].text().strip()  # type: ignore
        rectyp_nm = p_rectyp.lower()
        search_key = self.edit["redis_key"](search_key)
        if f"{rectyp_nm}:" not in search_key:
            search_key = f"{rectyp_nm}:{search_key}"
        if search_key[:1] != "*":
            search_key = "*" + search_key
        if search_key[-1:] != "*":
            search_key += "*"
        return (search_key.lower())

    # IO Meta Functions
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
            self.DBE.set_dbe_status(  # type: ignore
                "",
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
        links = self.get_value_fields(p_db_nm, p_rectyp, True)
        if links != {}:
            for link_nm, link_values in links.items():
                for link_ix, link_val in enumerate(link_values):
                    link_key = \
                        self.edit["redis_key"](link_val)
                    p_record[link_nm][link_ix] = link_key
                    link_rec = self.find_redis_keys(
                        p_db_nm, p_rectyp, link_key, p_load_1st_rec=False)
                    if link_rec in (None, {}, []):
                        self.DBE.set_dbe_status(  # type: ignore
                            "",
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
        self.DBE.prep_editor_action("Add")                  # type: ignore
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.get_active_db_rectyp()
            _, record = self.get_all_fields()
        else:
            db = p_db_nm
            rectyp = p_rectyp_nm
            # It is an auto-generated record.
            # Need to specify the DB and record type.
            # Would we still use a Form widget to CREATE the record?
            # hmmm... probably not? But would it be doable? Why not?
            manual_add = False
            values = self.get_value_fields(db, rectyp)
            key = f"{rectyp.lower()}:{RI.UT.get_hash(str(values))}"
            record = {"name": key} | values
        result = self.get_redis_record(db, record["name"])
        if result in (None, [], {}):
            if self.run_rectyp_edits():
                if not self.validate_links(db, rectyp, record):
                    return False
                if manual_add:
                    record = RI.set_audit_values(record, p_include_hash=True)
                else:
                    record = RI.set_audit_values(record, p_include_hash=False)
                RI.do_insert(db, record)
                return True
        else:
            self.DBE.set_dbe_status(   # type: ignore
                "",
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
            self.DBE.set_dbe_status(   # type: ignore
                "",
                f"No record found with key like '{p_key_pattern}'")
        else:
            for res in result_b:
                result.append(res.decode("utf-8"))
            result = sorted(result)
            rcnt = len(result)
            rword = "record" if rcnt == 1 else "records"
            self.DBE.set_dbe_status(   # type: ignore
                "",
                f"{rcnt} {rword} found with key like '{p_key_pattern}'")
            if p_load_1st_rec:
                # Get first record from find key list, display in editor
                # Select first record in the set of found keys.
                _ = self.get_redis_record(db, result[0])
                # If more than one key was found,
                if len(result) > 1:
                    self.DBE.activate_buttons(   # type: ignore
                        "Get", ["Next", "Prev"])
                else:
                    self.DBE.deactivate_buttons(   # type: ignore
                        "Get", ["Next", "Prev"])
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
        self.DBE.prep_editor_action("Find")
        db, rectyp = self.get_active_db_rectyp()
        search_key = self.get_searchkey_value(rectyp)
        _ = self.find_redis_keys(
            db.lower(), rectyp, search_key, p_load_1st_rec=True)
