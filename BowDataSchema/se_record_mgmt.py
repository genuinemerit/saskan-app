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
from PySide2.QtWidgets import QPushButton
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
        def set_underbars(text):
            """Remove stray underbars

            - Remove leading or trailing underbars.
            - Reduce multiple underbars to single underbars.
            """
            r_str = text
            while "__" in r_str:
                r_str = r_str.replace("__", "_")
            while r_str[-1:] == "_":
                r_str = r_str[:-1]
            while r_str[:1] == "_":
                r_str = r_str[1:]
            return r_str

        def set_redis_key(p_text: str):
            """Convert anything not a letter or colon to underbar.

               And make it lowercase.
            """
            r_str = p_text.strip()
            for char in r_str:
                if not char.isalpha() and \
                   not char.isdigit() and \
                   not char == ":":
                    r_str = r_str.replace(char, "_")
            return set_underbars(r_str.lower())

        def verify_host(p_value: str):
            """Validate value against an enumerated list."""
            if p_value in ["localhost", "curwen"]:
                return True
            else:
                return False

        # exposed edit methods
        self.mask = {"date": "0000-00-00",
                     "lower": "<"}
        self.edit = {"dbkey": set_redis_key,
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
            hbox = QHBoxLayout()
            hbox.LeftToRight
            lbl = QLabel(self.recs["db"][dbk]["name"])
            hbox.addWidget(SS.set_subtitle_style(lbl))
            for dmk, dm in self.recs["db"][dbk]["dm"].items():
                rdo_btn = SS.set_radiobtn_style(QRadioButton(dm["a"]))
                self.recs["db"][dbk]["dm"][dmk]["w_sel"] = rdo_btn
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

    def get_list_values(self,
                        db: str,
                        dm: str,
                        fgrp: str,
                        ftag: str):
        """Find all list field values for designated field meta tag.

        If it comes back empty, that means no values have been assigned
        yet to an list-type edit line widget. This can also
        be the case when the domain widget has not yet been completed,
        so the line-edit child-widget is not found.
        In either case, put one empty value in the list.

        :return:
            (list) List of values for the field
        """
        flix = 1
        ffnd = True
        list_values = []
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        while ffnd:
            try:
                flid = f"{db}:{dm}:{ftag}-{str(flix)}.ed"
                list_values.append(
                    dom_wdg.findChild(QLineEdit, flid).text())
                flix += 1
            except Exception as err:  # noqa F841
                ffnd = False

        if list_values == []:
            list_values = [""]
        return list_values

    def get_field_values(self,
                         db: str,
                         dm: str):
        """Get all field meta, names and edit values (if any) for specified domain.

        Note that findChild() method only works on Widgets, not on Forms

        :returns: (tuple)
            ( frec = dict in edit form format,
              dbrec = dict in redis db format )
        """
        meta = self.recs["db"][db]["dm"][dm]["rec"]
        frec: dict = {db: {dm: meta}}
        dbrec: dict = {db: {"name": {}, "values": {}, "audit": {}}}
        dbkey: str = ""  # redis key = "name" value on redis record
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        for fgrp, fields in meta.items():
            for ftag, rec in fields.items():
                # Set all rec values based on current form fields
                frec[db][dm][fgrp][ftag]["value"] = []
                flid = f"{db}:{dm}:{ftag}.ed"

                if "list" in rec["ed"]:

                    print(f"LIST flid: {flid}")

                    frec[db][dm][fgrp][ftag]["value"] = \
                        self.get_list_values(db, dm, fgrp, ftag)
                else:

                    print(f"SINGLETON flid: {flid}")

                    value = dom_wdg.findChild(QLineEdit, flid).text()
                    frec[db][dm][fgrp][ftag]["value"].append(value)
                    if fgrp == "keys":
                        dbkey += f"{value}:"
        dbkey = dbkey[:-1]
        if dm not in dbkey:
            dbkey = dm + ":" + dbkey
        dbrec[db]["name"] = self.edit["dbkey"](dbkey)
        for fgrp, mrec in frec[db][dm].items():
            dbrec[db][fgrp] = {}
            for flix, rec in mrec.items():
                dbrec[db][fgrp][flix] = rec["value"]

        pp(("frec", frec))
        pp(("dbrec", dbrec))

        return (frec, dbrec)

    def set_line_edit(self,
                      db: str,
                      dm: str,
                      fgrp: str,
                      ftag: str,
                      rec: dict,
                      p_add_row: bool = False):
        """Return an edit widget that can be added to form.

        :args:
            db (str) Tag of database in meta catalog
            dm (str) Tag of domain in meta catalog
            fgrp (str) Name of field group (keys or vals)
            ftag (str) Tag of edit line field in meta catalog
            rec (dict) Record meta data for this field
            p_add_row (bool) True if this is a not the first row in a list
        :returns: (QWidget) line edit
        """
        ew = SS.set_line_edit_style(QLineEdit())
        if "list" in rec["ed"]:
            list_values = self.get_list_values(db, dm, fgrp, ftag)
            flix = len(list_values)
            if p_add_row:
                flix += 1
            ew.setObjectName(f"{db}:{dm}:{ftag}-{str(flix)}.ed")
        else:
            ew.setObjectName(f"{db}:{dm}:{ftag}.ed")
        if "hint" in rec.keys():
            ew.setPlaceholderText(rec["hint"])
            ew.setToolTip(rec["hint"])
        return (ew)

    def set_list_row(self,
                     db: str,
                     dm: str,
                     fgrp: str,
                     ftag: str,
                     rec: dict,
                     p_add_row: bool = False):
        """Return a box widget containing next row in a list.

        :args:
            db (str) Name (meta index) of database
            dm (str) Name (meta index) of domain
            fgrp (str) Name of group ('keys' or 'vals')
            ftag (str) Name (meta index) of field
            rec (dict) Field meta data
            p_add_row (bool) True if this is a not the first row in a list
        :returns: (QWidget) hbox containting edit field and button
        """
        def add_list_btn(p_btn_txt: str,
                         p_btn_nm: str,
                         p_action):
            """Add a button to add or remove a new list item."""
            btn = SS.set_button_style(QPushButton(p_btn_txt), p_active=True)
            list_values = self.get_list_values(db, dm, fgrp, ftag)
            flix = len(list_values)
            if p_add_row:
                flix += 1
            btn.setObjectName(
                f"{db}_{dm}_{fgrp}_{ftag}-{str(flix)}_{p_btn_nm}")
            btn.clicked.connect(p_action)
            return (btn)

        hbox = QHBoxLayout()
        rec = self.recs["db"][db]["dm"][dm]["rec"][fgrp][ftag]
        hbox.addWidget(self.set_line_edit(db, dm, fgrp, ftag, rec, p_add_row))
        hbox.addWidget(add_list_btn(
                "+", "add.btn", self.add_row_to_list))
        hbox.addWidget(add_list_btn(
                "-", "rmv.btn", self.remove_row_from_list))
        return (hbox)

    def make_edit_form(self,
                       db: str,
                       dm: str):
        """Return a form widget for a specific db+domain rec type.

        It returns a form layout contained inside a generic widget.

        Hint-styling indicates key fields and edits.
        Example --> unicode key character: 🔑

        :returns: QWidget object containing a QVBoxLayout object
                  containing sub-title widgets, edit buttons -
                  like for list length, form layouts/rows of
                  related edit fields.
        """
        frm_wdg = QWidget()
        form = QFormLayout()
        form.setObjectName(f"{db}:{dm}.frm")
        form.setLabelAlignment(Qt.AlignRight)
        for fgrp, recs in self.recs["db"][db]["dm"][dm]["rec"].items():
            for ftag, rec in recs.items():
                if "list" in rec["ed"]:
                    form.addRow(rec["title"],
                                self.set_list_row(db, dm, fgrp, ftag, rec))
                else:
                    form.addRow(rec["title"],
                                self.set_line_edit(db, dm, fgrp, ftag, rec))
        frm_wdg.setLayout(form)
        return(frm_wdg)

    def init_list_button_visiblity(self):
        """Set initial visiblity state for list-type edit item buttons"""
        for dbk, db in self.recs["db"].items():
            for dmk, dm in db["dm"].items():
                dom_wdg = self.recs["db"][dbk]["dm"][dmk]["w_dom"]
                for fgrp, recs in dm["rec"].items():
                    for ftag, rec in recs.items():
                        if "list" in rec["ed"]:
                            tag = f"{dbk}_{dmk}_{fgrp}_{ftag}-1_"
                            dom_wdg.findChild(
                                QPushButton, tag+"add.btn").setVisible(True)
                            dom_wdg.findChild(
                                QPushButton, tag+"rmv.btn").setVisible(False)

    def set_list_button_visiblity(self,
                                  db,
                                  dm,
                                  fgrp,
                                  ftag):
        """Set the visibility of the add/remove list button."""
        list_values = self.get_list_values(db, dm, fgrp, ftag)
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        max_flix = len(list_values)
        for flix in range(1, max_flix + 1):
            add_btn = f"{db}_{dm}_{fgrp}_{ftag}-{str(flix)}_add.btn"
            rmv_btn = f"{db}_{dm}_{fgrp}_{ftag}-{str(flix)}_rmv.btn"
            if flix < max_flix:
                dom_wdg.findChild(
                    QPushButton, add_btn).setVisible(False)
                dom_wdg.findChild(
                    QPushButton, rmv_btn).setVisible(False)
            else:
                dom_wdg.findChild(
                    QPushButton, add_btn).setVisible(True)
                if max_flix > 1:
                    dom_wdg.findChild(
                        QPushButton, rmv_btn).setVisible(True)
                else:
                    dom_wdg.findChild(
                        QPushButton, rmv_btn).setVisible(False)

    def add_row_to_list(self):
        """Add an input row to form for list of fields.

        Remove '_add.btn' to derive the object ID of the line edit,
        then split on '_' (if any) and take first part to get the
        original meta field tag.
        """
        db, dm, fgrp, flid = tuple(
            self.sender().objectName().replace("_add.btn", "").split("_"))
        frec, dbrec = self.get_field_values(db, dm)
        ftag = flid.split("-")[0]
        rec = frec[db][dm][fgrp][ftag]
        # Add rows to the form widget
        form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
            QFormLayout, f"{db}:{dm}.frm")
        form_wdg.addRow(rec["title"],
                        self.set_list_row(
                            db, dm, fgrp, ftag, rec, p_add_row=True))
        self.set_list_button_visiblity(db, dm, fgrp, ftag)

    def remove_row_from_list(self):
        """Remove one input row from the form for list of fields.

        Remove '_rmv.btn' to derive the object ID of the line edit,
        then split on '_' (if any) and take first part to get the
        original meta field tag and the index of the selected edit line.

        Since values are collected from the form, don't need to manage
        any storage of values, e.g., removing a value.  However, we do
        need to do something to handle numbering (flix) of list items.
        And that gets tricky. So we will restrict adding and removing buttons
        to appear only on the LAST item in a list.

        Keep in mind that the rowCount() on the Form Layout includes ALL of
        the fields presently on the form, not only the List fields. Another
        reason it is easier to manipulate only the last field in the List.

        This may also be a good reason to allow only one List-type field per
        domain. At least until I can figure out a nicer way to manage the adds
        and removals. I think it can be done passing in the actual widget (or
        maybe its ID?) to be removed, but keep in mind that that is a Layout
        (a HBox) and not a LineEdit widget.
        """
        db, dm, fgrp, flid = tuple(
            self.sender().objectName().replace("_rmv.btn", "").split("_"))
        frec, dbrec = self.get_field_values(db, dm)
        ftag = flid.split("-")[0]
        form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
            QFormLayout, f"{db}:{dm}.frm")
        form_wdg.removeRow(form_wdg.rowCount() - 1)
        self.set_list_button_visiblity(db, dm, fgrp, ftag)

    def set_ed_button_actions(self):
        """Assign actions to button slots defined in the DBEditor class.

        Other editor button actions are assigned in the DBEditor class.
        """
        # Find-keys Button
        self.ed_meta["bx"]["get.box"]["bn"]["find.btn"]["w"].clicked.connect(
            self.push_find_keys)

    # Database Editor Widget extend function
    # ============================================================
    def extend_db_editor_wdg(self):
        """Create record type forms for the Data Base Editor widget.

        The "dom widget" is a generic widget containing a QVBoxLayout,
        which in turns contains a QWidget/QFormLayout for each record
        within the domain. When doing a findChild(), typically to find
        a line-edit widget attached to a QFormLayout, execute the method
        against the dom_wdg. It is the only widget that gets saved in
        the metadata catalog when working with editor-level edit objects.

        And create selector checkboxes for record types.
        """
        self.editor.dbe.addLayout(self.make_selectors())
        for dbk, db in self.recs["db"].items():
            for dmk, dm in db["dm"].items():
                dom_wdg = QWidget()
                vbox = QVBoxLayout()
                txt = (self.recs["db"][dbk]["name"] + ": " +
                       self.recs["db"][dbk]["dm"][dmk]["a"])
                vbox.addWidget(SS.set_subtitle_style(QLabel(txt)))
                vbox.addWidget(self.make_edit_form(dbk, dmk))
                dom_wdg.setLayout(vbox)
                dom_wdg.hide()
                self.recs["db"][dbk]["dm"][dmk]["w_dom"] = dom_wdg
                self.editor.dbe.addWidget(dom_wdg)
        self.init_list_button_visiblity()
        self.set_ed_button_actions()

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
        wdg = \
            self.ed_meta["bx"]["get.box"]["inp"]["find.inp"]["w"]
        search = self.edit["dbkey"](wdg.text())
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
        for dbk in self.recs["db"].keys():
            domk = [dmk for dmk, dom in self.recs["db"][dbk]["dm"].items()
                    if dom["w_dom"].isVisible()]
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
    def select_domain(self,
                      p_dbk: str,
                      p_dmk: str):
        """Generic function for record type selection actions.

        :args:
            p_dbk: name of selected database type
            p_dmk: name of selected record type (domain)
        """
        txt = self.recs["db"][p_dbk]["dm"][p_dmk]["a"]
        self.editor.set_dbe_status(txt)        # type: ignore
        self.show_domain(p_dbk, p_dmk)

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        self.select_domain("basement.db", "configs")

    def select_status(self):
        """Slot for Editor Select Status Flags radio check action"""
        self.select_domain("basement.db", "status")

    def select_topics(self):
        """Slot for Editor Select Topics radio check action"""
        self.select_domain("schema.db", "topics")

    def select_queues(self):
        """Slot for Editor Select Queues radio check action"""
        self.select_domain("harvest.db", "queues")

    # Record Type Editor Widget helper functions
    # ============================================================
    def hide_domain(self):
        """Hide any visible Record Type Edit Form."""
        for db in self.recs["db"].keys():
            for dm in self.recs["db"][db]["dm"].keys():
                if self.recs["db"][db]["dm"][dm]["w_dom"].isVisible():
                    self.recs["db"][db]["dm"][dm]["w_dom"].hide()
        self.editor.disable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.disable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.disable_buttons("edit.box", ["cancel.btn"])  # type: ignore

    def show_domain(self,
                    p_dbk: str,
                    p_dmk: str):
        """Activate/Show the selected Record Type Edit Form.

        :args:
            p_dbk: key of database
            p_dmk: key of record (domain) type
        """
        self.hide_domain()
        self.recs["db"][p_dbk]["dm"][p_dmk]["w_dom"].show()
        self.editor.enable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.enable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.enable_buttons("edit.box", ["cancel.btn"])  # type: ignore

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

        fields_nm = "value_fields"
        form_nm = f"{db}:{rectyp}:{fields_nm}.frm"
        form_rows = \
            self.rectyps[db][rectyp]["widget"].findChild(
                QFormLayout, f"{db}:{rectyp}:{form_nm}")

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

    def run_rectyp_edits(self) -> bool:
        """Run the edits associated with the active record type.

        These are executed when an Add or Save button is pressed.

        :returns: (bool) True if all edits pass else False
        """
        db, rectyp = self.get_active_domain()
        form_values = self.get_value_fields(db, rectyp)
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
            # see notes below
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

                # Let's work first on displaying the 1st record returned,
                # then on expiry time stamps & rules, then on queue recs.

                # To load from db record to editor form(s), use functions
                # in the DB Editor class:
                #  db_editor.set_key_fields(record)
                #  db_editor.set_value_fields(record)
                #   sub-function: db_editor.set_list_field(field, value)
                #  consider whether to display audit and expiry values?
                #    I am thinking yes. Why not? Just can't edit them.

                # Populate the rectyp editor widget and forms for first record.
                # Define functions like:
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
                        self.edit["dbkey"](link_val)
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

        On Redis records, the key value is referenced as the "name".

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
            _, record = self.get_field_values(db, rectyp)
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
