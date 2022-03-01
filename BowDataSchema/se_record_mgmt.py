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
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from boot_texts import BootTexts                # type: ignore
from redis_io import RedisIO                    # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

BT = BootTexts()
RI = RedisIO()
SS = SaskanStyles()


class RecordMgmt(QWidget):
    """Handle set-up, set, get for predefined record types.

    Closely related to the DB Editor Widget Class.

    Values for Audit fields are auto-generated, so there
        are not any edit rules for them and they cannot be changed
        by manual edits.

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

    @DEV:
    - Work on ordering editor boxes using indexes
    """
    def __init__(self,
                 parent: QWidget,
                 wdg_meta: dict,
                 db_editor: object):
        """super() call is required.

        The DB editor widget is also passed in.
        """
        super().__init__(parent)
        self.recs = wdg_meta
        self.editor = db_editor
        self.ed_meta = db_editor.get_tools()  # type: ignore
        self.set_edits_meta()
        self.extend_db_editor_wdg()

    def get_tools(self):
        """Return modified metadata"""
        return(self.recs)

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

        def bump_redis_key(p_text: str):
            """Convert anything not a letter or colon to underbar.
            And make it lowercase.
            """
            r_str = p_text.strip()
            for char in r_str:
                if not char.isalpha() and \
                   not char.isdigit() and \
                   not char == ":":
                    r_str = r_str.replace(char, "_")
            return bump_underbars(r_str.lower())

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

    # Record Type Selector Widgets make functions
    # ============================================================
    def make_selectors(self):
        """Return collection(s) of radio buttons for selecting rectyp.

        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        lbl = QLabel(self.recs["bx"]["select.box"]["a"])
        vbox.addWidget(SS.set_subtitle_style(lbl))
        for dbk, db in self.recs["db"].items():
            if dbk == "audit":
                continue
            hbox = QHBoxLayout()
            hbox.LeftToRight
            lbl = QLabel(self.recs["db"][dbk]["name"])
            hbox.addWidget(SS.set_subtitle_style(lbl))
            for dmk, dm in self.recs["db"][dbk]["dm"].items():
                rdo_btn = SS.set_radiobtn_style(QRadioButton(dm["a"]))
                self.recs["db"][dbk]["dm"][dmk]["w"] = rdo_btn
                hbox.addWidget(rdo_btn)
                action = None
                if dbk == "basement.db":
                    if dmk == "configs":
                        action = self.select_configs
                    elif dmk == "status":
                        action = self.select_status
                elif dbk == "schema.db":
                    if dmk == "topics":
                        action = self.select_topics
                elif dbk == "harvest.db":
                    if dmk == "queues":
                        action = self.select_queues
                self.recs["db"][dbk]["dm"][dmk]["action"] = action
                rdo_btn.clicked.connect(action)
            hbox.addStretch(1)
            vbox.addLayout(hbox)
        return (vbox)

    # Record Type Editor Form Widget make functions
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
            hint += f" {self.editor.texts['Key']['hint']}"  # type: ignore
        if hint != "":
            edit_wdg.setPlaceholderText(hint)
            edit_wdg.setToolTip(hint)
        return (edit_wdg)

    def make_edit_form(self,
                       p_dbk: str,
                       p_dmk: str):
        """Return a form widget for a specific db+domain rec type.

        :returns: QWidget object containing a QVBoxLayout object
                  containing several Label widgets (sub-titles),
                  specialized edit buttons (like for list length),
                  and Form layouts (rows of related edit fields).

        @DEV
        - So the form layout has to be "set" in a widget.
        - Only need another box if going to put more stuff in it.
        - Might need a box for +/- buttons on lists.
        """
        wdg = QWidget()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        for fk, fields in self.recs["db"][p_dbk]["dm"][p_dmk]["rec"].items():
            # Use some kind of styling to indicate key fields
            # Unicode characters for picture of a key: 🔑
            for fnm, fld in fields.items():
                edit_wdg = SS.set_line_edit_style(QLineEdit())
                if "hint" in fld.keys():
                    edit_wdg.setPlaceholderText(fld["hint"])
                form.addRow(fld["name"], edit_wdg)
        wdg.setLayout(form)
        return(wdg)
        """
        for f_grp in ["key_fields", "value_fields"]:
            if self.rectyps[db_nm][rectyp_nm][f_grp] is not None:
                # Add sub-title for group of fields
                rectyp_layout.addWidget(
                    self.editor.make_text_subttl_wdg(f_grp))  # type: ignore
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
                                self.editor.make_button_group_wdg(
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
        """

    def set_button_actions(self):
        """Assign actions to button slots.

        Other button actions are assigned in DBEditor class.
        """
        # Find-keys Button
        self.ed_meta["bx"]["get.box"]["bn"]["find.btn"]["w"].clicked.connect(
            self.push_find_keys)

    # Database Editor Widget extend function
    # ============================================================
    def extend_db_editor_wdg(self):
        """Create record type forms for the Data Base Editor widget.

        And create selector checkboxes for record types.
        """
        self.set_button_actions()
        self.editor.dbe.addLayout(self.make_selectors())
        for dbk, db in self.recs["db"].items():
            if dbk == "audit":
                continue
            for dmk, dm in db["dm"].items():
                recwdg = QWidget()
                vbox = QVBoxLayout()
                txt = (self.recs["db"][dbk]["name"] + ": " +
                       self.recs["db"][dbk]["dm"][dmk]["a"])
                vbox.addWidget(SS.set_subtitle_style(QLabel(txt)))
                vbox.addWidget(self.make_edit_form(dbk, dmk))
                recwdg.setLayout(vbox)
                recwdg.hide()
                self.recs["db"][dbk]["dm"][dmk]["w"] = recwdg
                self.editor.dbe.addWidget(recwdg)
        """
        # Enable rec mgmt related button actions
        for key, act in {
                ("Edit", "Add"): self.add_record_to_db,
                ("Get", "Find"): self.find_record_keys}.items():
            # Refactor these to use a dict
            wdg = self.editor.buttons[key[0]][key[1]]["widget"]
            wdg.clicked.connect(act)
        """

    # Editor Button helper and slot functions
    # ============================================================

    def get_active_search(self,
                          dom: str):
        """Return value of search-key text input widget...

        ..adjusted to work as a wildcard on keys in the active domain.

        :args:
            dom (str) name of active domain

        :returns: (str) search value modified for use on redis db
        """
        wdg = self.ed_meta["bx"]["get.box"]["inp"]["find.inp"]["w"]  # type: ignore
        search = self.edit["redis_key"](wdg.text())
        if f"{dom.lower()}:" not in search:
            search = f"{dom.lower()}:{search}"
        if search[:1] != "*":
            search = "*" + search
        if search[-1:] != "*":
            search += "*"
        return (search.lower())

    def get_active_domain(self):
        """Identify the currently active db and domain (rectype).

        :returns: tuple (db name key, domain/record type key)
        """
        db = None
        rectyp = None
        dbs = [dbk for dbk in self.recs["db"].keys() if dbk != "audit"]
        for dbk in dbs:
            domk = [dmk for dmk, dom in self.recs["db"][dbk]["dm"].items()
                    if dom["w"].isVisible()]
            if len(domk) > 0:
                db = dbk
                rectyp = domk[0]
                break
        return (db, rectyp)

    def push_find_keys(self):
        """Slot for DB Editor Find push button click action."""
        # self.editor.prep_editor_action("Find")
        db, rectyp = self.get_active_domain()
        search = self.get_active_search(rectyp)
        _ = self.find_redis_keys(
            db.lower(), rectyp, search, p_load_1st_rec=True)

    # Record Type Selector helper and slot functions
    # ============================================================
    def select_record_type(self,
                           p_dbk: str,
                           p_dmk: str):
        """Generic function for record type selection actions.

        :args:
            p_dmk: name of selected database type
            p_dmk: name of selected record type
        """
        txt = self.recs["db"][p_dbk]["dm"][p_dmk]["a"]
        self.editor.set_dbe_status(txt)        # type: ignore
        self.show_rectype(p_dbk, p_dmk)

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        self.select_record_type("basement.db", "configs")

    def select_status(self):
        """Slot for Editor Select Status Flags radio check action"""
        self.select_record_type("basement.db", "status")

    def select_topics(self):
        """Slot for Editor Select Topics radio check action"""
        self.select_record_type("schema.db", "topics")

    def select_queues(self):
        """Slot for Editor Select Queues radio check action"""
        self.select_record_type("harvest.db", "queues")

    # Record Type Editor Widget helper functions
    # ============================================================
    def hide_rectype(self):
        """Deactivate any showing Record Type Edit Form."""
        for db in self.recs["db"].keys():
            if db != "audit":
                for dm in self.recs["db"][db]["dm"].keys():
                    if self.recs["db"][db]["dm"][dm]["w"].isVisible():
                        self.recs["db"][db]["dm"][dm]["w"].hide()
        self.editor.disable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.disable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.disable_buttons("edit.box", ["cancel.btn"])  # type: ignore

    def show_rectype(self,
                     p_dbk: str,
                     p_dmk: str):
        """Activate a Record Type Edit Form.

        :args:
            p_dbk: key of database
            p_dmk: key of record (domain) type
        """
        self.hide_rectype()
        rec = self.recs["db"][p_dbk]["dm"][p_dmk]
        rec["w"].show()
        self.editor.enable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.enable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.enable_buttons("edit.box", ["cancel.btn"])  # type: ignore

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
            db, rectyp = self.get_active_domain()
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
            db, rectyp = self.get_active_domain()
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
            db, rectyp = self.get_active_domain()
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

    def run_rectyp_edits(self) -> bool:
        """Run the edits associated with the active record type.

        These are executed when an Add or Save button is pressed.

        :returns: (bool) True if all edits pass else False
        """
        db, rectyp = self.get_active_domain()
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
                self.editor.set_dbe_status("", error_msg)  # type: ignore
                break
        return (edits_passed)

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
            self.editor.set_dbe_status(  # type: ignore
                f"{BT.txt.no_key}{p_select_key}'")
        else:
            print(f"GET Result: {result}")
            # put the values into the editor
            pass
        return (result)

    def find_redis_keys(self,
                        p_db_nm: str,
                        p_rectyp: str,
                        p_search: str,
                        p_load_1st_rec: bool = True):
        """Get a list of keys for selected DB matching the pattern.

        :args:
            p_db_nm - name of the database to search
            p_rectyp - record type to search
            p_search - pattern to match for keys
            p_load_1st_rec - load 1st record found into editor
        :returns: list of keys that match the pattern or None
        """
        db = p_db_nm
        result_b = RI.find_keys(db.replace(".db", ""), p_search)
        result: list = []
        if result_b in (None, [], {}):
            self.editor.set_dbe_status(   # type: ignore
                f"{BT.txt.no_key} '{p_search}'")
        else:
            for res in result_b:
                result.append(res.decode("utf-8"))
            result = sorted(result)
            if len(result) == 1:
                self.editor.set_dbe_status(   # type: ignore
                    f"{len(result)} {BT.txt.record_found}{p_search}")
            else:
                self.editor.set_dbe_status(   # type: ignore
                    f"{len(result)} {BT.txt.records_found}{p_search}")
            if p_load_1st_rec:
                records = self.get_redis_record(db, result[0])
                if len(records) > 1:
                    self.editor.enable_buttons(   # type: ignore
                        "get.box", ["Next"])
                else:
                    self.editor.disable_buttons(   # type: ignore
                        "get.box", ["Next", "Prev"])
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
                        self.editor.set_dbe_status(  # type: ignore
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
        self.editor.prep_editor_action("Add")                  # type: ignore
        if p_db_nm is None or p_rectyp_nm is None:
            db, rectyp = self.get_active_domain()
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
            self.editor.set_dbe_status(   # type: ignore
                "",
                "Insert rejected. Record already exists.")
            return False
