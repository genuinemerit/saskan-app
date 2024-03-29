#!/usr/bin/python3.9
"""
:module:    se_record_mgmt.py

:author:    GM (genuinemerit @ pm.me)
"""

from pprint import pformat as pf     # noqa: F401
from pprint import pprint as pp      # noqa: F401
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
from wire_tap import WireTap                    # type: ignore

BT = BootTexts()
RI = RedisIO()
SS = SaskanStyles()
WT = WireTap()


class RecordMgmt(QWidget):
    """Handle set-up, set, get for predefined record types.
    Closely related to the DB Editor Widget Class.
    Values for Audit fields are auto-generated, 
    No edit rules for them. They cannot be changed manually.
    @DEV:
    - Possible metadata-defined edit rules and masks might want to use...
        auto -- field is populated by system, cannot be edited
        date -- set format to YYYY-MM-DD
        datetime -- Input mask or regex YYYYMMDDHHMMSS.SSS
        dbkey -- convert to valid Redis key format
        hostname -- must be a valid hostname
        link -- must follow rules for key values
        list -- may occur 1 to x times
        lower -- convert values to lower-case
        nameval -- must follow rules for a named value
        notnull -- cannot be empty set or all spaces
        number -- can be pos, neg or zero real
        posint -- positive integer
        posreal -- positive real number
        yesno -- value must be "yes" or "no"
    - Work on ordering editor boxes using indexes?
    """
    def __init__(self,
                 parent: QWidget,
                 wdg_meta: dict,
                 db_editor: object):
        """super() call is required.
        The DB editor widget is also passed in."""
        WT.log_module(__file__, __name__, self)
        super().__init__(parent)
        self.recs = wdg_meta
        self.editor = db_editor
        self.ed_meta = db_editor.get_tools()  # type: ignore
        self.set_edits_meta()
        self.set_edits_cache()
        self.extend_db_editor_wdg()

    def get_tools(self):
        """Return modified metadata
        @public"""
        WT.log_function(self.get_tools, self)
        return(self.recs)

    def set_edits_meta(self):
        """To use when applying edits and auto-corrects.
        This includes:
        - named enum lists
        - input masks
        - specialized functions"""
        def set_underbars(text):
            """Remove stray underbars
            - Remove leading or trailing underbars.
            - Reduce multiple underbars to single underbars."""
            WT.log_function(set_underbars, self, 24, self.set_edits_meta)
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
               And make it lowercase."""
            WT.log_function(set_redis_key, self, 24, self.set_edits_meta)
            r_str = p_text.strip()
            for char in r_str:
                if not char.isalpha() and \
                   not char.isdigit() and \
                   not char == ":":
                    r_str = r_str.replace(char, "_")
            return set_underbars(r_str.lower())

        def verify_host(p_value: str):
            """Validate value against list of valid host names."""
            WT.log_function(verify_host, self, 24, self.set_edits_meta)
            if p_value in ["localhost", "curwen"]:
                return True
            else:
                return False

        def verify_yes_or_no(p_value: str):
            """Validate value in in (yes, no)."""
            WT.log_function(verify_yes_or_no, self, 24, self.set_edits_meta)
            if p_value.lower() in ["yes", "no"]:
                return True
            else:
                return False

        def verify_named_value(p_value: str):
            """Validate value has format like x:y."""
            WT.log_function(verify_named_value, self, 24, self.set_edits_meta)
            if (len(p_value) > 2 and
                    p_value.count(":") == 1 and
                    p_value.find(":") > 0):
                return True
            else:
                return False

        # exposed edit methods
        WT.log_function(self.set_edits_meta, self)
        self.mask = {"date": "0000-00-00",
                     "lower": "<"}
        self.edit = {"dbkey": set_redis_key,
                     "hostlist": verify_host,
                     "namedval": verify_named_value,
                     "yesno": verify_yes_or_no}

    def set_edits_cache(self):
        """For values shared between autonomous functions.
        These may eventually be stored as queues in the Harvest db."""
        WT.log_function(self.set_edits_cache, self)
        self.KEYS = []
        self.ACTIVE_KEY_IX = 0

    # Record Type Selector Widgets make functions
    # ============================================================
    def make_selectors(self):
        """Return collection(s) of radio buttons for selecting domain (rec type).
        :returns: QVBoxLayout object"""
        WT.log_function(self.make_selectors, self)
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
                    elif dmk == "plans":
                        action = self.select_plans
                    elif dmk == "services":
                        action = self.select_services
                    elif dmk == "schemas":
                        action = self.select_schemas
                elif dbk == "harvest.db":
                    if dmk == "queues":
                        action = self.select_queues
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
        This f is not being used yet.
        :args:
            (Qt object) The edit item widget
            (set) Names of edit rules for the edit item
        :returns: Modified edit widget"""
        WT.log_function(self.apply_pre_edits, self)
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
                        ftag: str):
        """Get list values from the form.
        Find all list field values for designated field meta tag.
        If it comes back empty, that means no values have been assigned
        yet to a list-type edit line widget. This can also
        be the case when the domain widget has not yet been completed,
        so the line-edit child-widget is not found.
        In either case, put one empty value in the list.
        :return:
            (list) List of values for the field"""
        WT.log_function(self.get_list_values, self)
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
            except Exception as _:  # noqa F841
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
              dbrec = dict in redis db format )"""
        WT.log_function(self.get_field_values, self)
        meta = self.recs["db"][db]["dm"][dm]["rec"]
        frec: dict = {db: {dm: meta}}
        ns = db.replace(".db", "")
        dbrec: dict = {ns: {"name": {}, "values": {}, "audit": {}}}
        dbkey: str = ""  # redis key = "name" value on redis record
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        for fgrp, fields in meta.items():
            for ftag, rec in fields.items():
                # Set all rec values based on current form fields
                frec[db][dm][fgrp][ftag]["values"] = []
                flid = f"{db}:{dm}:{ftag}.ed"
                if "list" in rec["ed"]:
                    frec[db][dm][fgrp][ftag]["values"] = \
                        self.get_list_values(db, dm, ftag)
                else:
                    value = dom_wdg.findChild(QLineEdit, flid).text()
                    frec[db][dm][fgrp][ftag]["values"].append(value)
                    if fgrp == "keys":
                        dbkey += f"{value}:"
        dbkey = dbkey[:-1]

        WT.log_msg("DEBUG", pf(("dm", dm, "dbkey before", dbkey)))

        key_prefix = dbkey.split(":")[0]
        if key_prefix != dm:
            dbkey = dm + ":" + dbkey

        WT.log_msg("DEBUG", pf(("dbkey after", dbkey)))

        dbrec[ns]["name"] = self.edit["dbkey"](dbkey)
        for ftag, rec in frec[db][dm]["keys"].items():
            dbrec[ns]["values"][ftag] = rec["values"]
        for ftag, rec in frec[db][dm]["vals"].items():
            dbrec[ns]["values"][ftag] = rec["values"]
        return (frec, dbrec)

    def set_form_values(self):
        """Set form field values based on Redis record values.
           Only call this function if it had been determined
           that one or more records were found with a key
           matching the search.
        @DEV:
        - Display list values properly.
            - On return from a find, make sure appropriate
              number of list elements/fields are defined, shown.
        - Display audit values as read-only fields or labels.
        - Enable the "delete" button.
        - Enable some kind of display of permitted enum values.
        - If key fields are edited, action is a (logical) delete + an insert,
          not just an insert. But we always do a logical delete + an insert
        - Treat key field edits like any others,
          but include a warning or notification.
        - BUT? Check for the use of a key field as a link value?
           - IF another record is using key value as a link, do we not
             allow an update (or delete). Do we modify the other record(s)?
          - Should we track link relationships in a way
            that will make them easier to find?  Two-way links (no)?
            Association tables (yes)?
        - Track if a change has been made. If so, enable the "Save" button
          and something like a "dirty" flag.
        - Use a queue structure to store pending changes?"""
        WT.log_function(self.set_form_values, self)
        db, dm = self.get_active_domain()
        nsid = db.replace(".db", "")
        key = self.KEYS[self.ACTIVE_KEY_IX]
        dbrec = self.get_redis_record(nsid, key)
        meta = self.recs["db"][db]["dm"][dm]["rec"]
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        
        WT.log_msg("DEBUG", pf(("dbrec", dbrec)))
        WT.log_msg("DEBUG", pf(("meta", meta)))

        for _, fields in meta.items():
            for ftag, rec in fields.items():
                flid = f"{db}:{dm}:{ftag}.ed"
                if "list" in rec["ed"]:
                    for flix, lval in enumerate(dbrec["values"][ftag]):
                        
                        WT.log_msg("DEBUG", f"flix # {flix}")
                        WT.log_msg("DEBUG", f"Value # {flix + 1}: {lval}")

                        if lval not in (None, ""):

                            WT.log_msg("DEBUG", "Value is not empty")

                            flid = f"{db}:{dm}:{ftag}-{str(flix + 1)}.ed"

                            WT.log_msg("DEBUG", f"Field ID: {flid}")

                            if flix > 0:

                                WT.log_msg("DEBUG", "Value index > 1 (flix > 0")

                                # unable to do an addWidget here
                                # why not? what is different from
                                #  when setting up form initially?
                                # generally, widgets are added to a box
                                # or to the self.editor.dbe  object.
                                # set_list_row() returns an hbox. It needs
                                # to be added to form object using addRow(), like:
                                # form.addRow(rec["title"],
                                #   self.set_list_row(db, dm, fgrp, ftag, rec)
                                # That form object then gets put in a box and
                                # attached to the dom_wdg.
                                # See how the form widget is retrieved in:
                                # remove_row_from_list()...
                                # ftag = flid.split("-")[0]
                                # form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
                                #   QFormLayout, f"{db}:{dm}.frm")
                                # form_wdg.removeRow(form_wdg.rowCount() - 1)
                                #   self.set_list_button_visiblity(db, dm, fgrp, ftag)
                                form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
                                   QFormLayout, f"{db}:{dm}.frm")

                                WT.log_msg("DEBUG", pf(("form_wdg", form_wdg)))
                                
                                form_wdg.addRow(rec["title"],
                                    self.set_list_row(db, dm, "vals", ftag, meta,
                                                      p_add_row=True))
                            dom_wdg.findChild(QLineEdit, flid).setText(lval)
                elif ftag in dbrec["values"]:
                    dom_wdg.findChild(QLineEdit, flid).setText(
                        dbrec["values"][ftag][0])
                else:
                    dom_wdg.findChild(QLineEdit, flid).setText("")

    def set_line_edit(self,
                      db: str,
                      dm: str,
                      ftag: str,
                      meta: dict,
                      p_add_row: bool = False):
        """Return an edit widget that can be added to form.

        :args:
            db (str) Tag of database in meta catalog
            dm (str) Tag of domain in meta catalog
            fgrp (str) Name of field group (keys or vals)
            ftag (str) Tag of edit line field in meta catalog
            meta (dict) Record meta data for this field
            p_add_row (bool) True if this is a not the first row in a list
        :returns: (QWidget) line edit
        """
        WT.log_function(self.set_line_edit, self)
        ew = SS.set_line_edit_style(QLineEdit())

        # We are not even getting to here when loading data from DB
        
        WT.log_msg("DEBUG", pf(("meta['ed']", meta["ed"])))

        if "list" in meta["ed"]:

            WT.log_msg("DEBUG", "Creating line edit item to append to list")

            # This assumes we want to get list values from the form
            # Is that true if we are popultating it from the database?

            list_values = self.get_list_values(db, dm, ftag)
            flix = len(list_values)
            if p_add_row:
                flix += 1
            list_line_edit_nm = f"{db}:{dm}:{ftag}-{str(flix)}.ed"
            ew.setObjectName(list_line_edit_nm)

            WT.log_msg("DEBUG", f"Added list item named: {list_line_edit_nm}")

        else:
            ew.setObjectName(f"{db}:{dm}:{ftag}.ed")
        if "hint" in meta.keys():
            ew.setPlaceholderText(meta["hint"])
            ew.setToolTip(meta["hint"])
        return (ew)

    def set_list_row(self,
                     db: str,
                     dm: str,
                     fgrp: str,
                     ftag: str,
                     meta: dict,
                     p_add_row: bool = False):
        """Return a box widget containing next row in a list.

        :args:
            db (str) Name (meta index) of database
            dm (str) Name (meta index) of domain
            fgrp (str) Name of group ('keys' or 'vals')
            ftag (str) Name (meta index) of field
            meta (dict) Field meta data
            p_add_row (bool) True if this is a not the first row in a list
        :returns: (QWidget) hbox containting edit field and button
        """
        def add_list_btn(p_btn_txt: str,
                         p_btn_nm: str,
                         p_action):
            """Add a button to add or remove a new list item."""
            WT.log_function(self.set_list_row, self, 24, add_list_btn)
            btn = SS.set_button_style(QPushButton(p_btn_txt), p_active=True)
            list_values = self.get_list_values(db, dm, ftag)
            flix = len(list_values)
            if p_add_row:
                flix += 1
            btn.setObjectName(
                f"{db}_{dm}_{fgrp}_{ftag}-{str(flix)}_{p_btn_nm}")
            btn.clicked.connect(p_action)
            return (btn)

        WT.log_function(self.set_list_row, self)
        hbox = QHBoxLayout()
        # meta = self.recs["db"][db]["dm"][dm]["rec"][fgrp][ftag]

        # We are not getting to here when loading data from DB
        WT.log_msg("DEBUG", "Setting a list row")
        WT.log_msg("DEBUG", pf(("meta", meta)))

        hbox.addWidget(self.set_line_edit(db, dm, ftag, meta, p_add_row))
        hbox.addWidget(add_list_btn(
                "+", "add.btn", self.add_row_to_list))
        hbox.addWidget(add_list_btn(
                "-", "rmv.btn", self.push_remove_row_button))
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
        WT.log_function(self.make_edit_form, self)
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
                                self.set_line_edit(db, dm, ftag, rec))
        frm_wdg.setLayout(form)
        return(frm_wdg)

    def init_list_button_visiblity(self):
        """Set initial visibility state for list-type edit item buttons"""
        WT.log_function(self.init_list_button_visiblity, self)
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
        WT.log_function(self.set_list_button_visiblity, self)
        list_values = self.get_list_values(db, dm, ftag)
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
                if max_flix == 1:
                    dom_wdg.findChild(
                        QPushButton, rmv_btn).setVisible(False)
                else:
                    dom_wdg.findChild(
                        QPushButton, rmv_btn).setVisible(True)
                if max_flix == 10:
                    dom_wdg.findChild(
                        QPushButton, add_btn).setVisible(False)
                else:
                    dom_wdg.findChild(
                        QPushButton, add_btn).setVisible(True)

    def add_row_to_list(self):
        """Add an input row to form for list of fields.

        Remove '_add.btn' to derive the object ID of the line edit,
        then split on '_' (if any) and take first part to get the
        original meta field tag.
        """
        WT.log_function(self.add_row_to_list, self)
        db, dm, fgrp, flid = tuple(
            self.sender().objectName().replace("_add.btn", "").split("_"))
        ftag, flix = tuple(flid.split("-"))
        frec, dbrec = self.get_field_values(db, dm)
        rec = frec[db][dm][fgrp][ftag]
        # Add rows to the form widget
        form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
            QFormLayout, f"{db}:{dm}.frm")
        form_wdg.addRow(rec["title"],
                        self.set_list_row(
                            db, dm, fgrp, ftag, rec, p_add_row=True))
        self.set_list_button_visiblity(db, dm, fgrp, ftag)

    def remove_row_from_list(self,
                             db,
                             dm,
                             fgrp,
                             flid):
        """Remove one input row from the form for list of fields.

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
        WT.log_function(self.remove_row_from_list, self)
        ftag = flid.split("-")[0]
        form_wdg = self.recs["db"][db]["dm"][dm]["w_dom"].findChild(
            QFormLayout, f"{db}:{dm}.frm")
        form_wdg.removeRow(form_wdg.rowCount() - 1)
        self.set_list_button_visiblity(db, dm, fgrp, ftag)

    def set_ed_button_actions(self):
        """Assign actions to button slots defined in the DBEditor class.
        Other editor button actions are assigned in the DBEditor class.
        """
        WT.log_function(self.set_ed_button_actions, self)
        # Find-keys Button
        self.ed_meta["bx"]["get.box"]["bn"]["find.btn"]["w"].clicked.connect(
            self.push_find_button)
        self.ed_meta["bx"]["get.box"]["bn"]["next.btn"]["w"].clicked.connect(
            self.push_next_button)
        self.ed_meta["bx"]["get.box"]["bn"]["prev.btn"]["w"].clicked.connect(
            self.push_prev_button)
        # Edit Buttons
        self.ed_meta["bx"]["edit.box"]["bn"]["add.btn"]["w"].clicked.connect(
            self.push_add_button)
        self.ed_meta["bx"]["edit.box"]["bn"]["clear.btn"]["w"].clicked.connect(
            self.push_clear_button)

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
        WT.log_function(self.extend_db_editor_wdg, self)
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

    def get_search_value(self,
                         dm: str):
        """Return value of search-key text input widget...

        ..adjusted to work as a wildcard on keys in the active domain.

        :args:
            dm (str) name of active domain

        :returns: (str) search value modified for use on redis db
        """
        WT.log_function(self.get_search_value, self)
        wdg = \
            self.ed_meta["bx"]["get.box"]["inp"]["find.inp"]["w"]
        sval = self.edit["dbkey"](wdg.text())
        if f"{dm.lower()}:" not in sval:
            sval = f"{dm.lower()}:{sval}"
        if sval[:1] != "*":
            sval = "*" + sval
        if sval[-1:] != "*":
            sval += "*"
        return (sval.lower())

    def get_active_domain(self):
        """Identify the currently active db and domain (rectype).

        :returns: tuple (db name key, domain/record type key)
        """
        WT.log_function(self.get_active_domain, self)
        db = None
        dm = None
        for dbk in self.recs["db"].keys():
            domk = [dmk for dmk, dom in self.recs["db"][dbk]["dm"].items()
                    if dom["w_dom"].isVisible()]
            if len(domk) > 0:
                db = dbk
                dm = domk[0]
                break
        return (db, dm)

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
        WT.log_function(self.select_domain, self)
        txt = self.recs["db"][p_dbk]["dm"][p_dmk]["a"]
        self.editor.set_dbe_status(txt)        # type: ignore
        self.show_domain(p_dbk, p_dmk)

    def select_configs(self):
        """Slot for Editor Select Configs radio check action"""
        WT.log_function(self.select_configs, self)
        self.select_domain("basement.db", "configs")

    def select_status(self):
        """Slot for Editor Select Status Flags radio check action"""
        WT.log_function(self.select_status, self)
        self.select_domain("basement.db", "status")

    def select_topics(self):
        """Slot for Editor Select Topics radio check action"""
        WT.log_function(self.select_topics, self)
        self.select_domain("schema.db", "topics")

    def select_plans(self):
        """Slot for Editor Select Plans radio check action"""
        WT.log_function(self.select_plans, self)
        self.select_domain("schema.db", "plans")

    def select_services(self):
        """Slot for Editor Select Services radio check action"""
        WT.log_function(self.select_services, self)
        self.select_domain("schema.db", "services")

    def select_schemas(self):
        """Slot for Editor Select Schemas radio check action"""
        WT.log_function(self.select_schemas, self)
        self.select_domain("schema.db", "schemas")

    def select_queues(self):
        """Slot for Editor Select Queues radio check action"""
        WT.log_function(self.select_queues, self)
        self.select_domain("harvest.db", "queues")

    # Record Type Editor Widget helper functions
    # ============================================================
    def hide_domain(self):
        """Hide any visible Record Type Edit Form."""
        WT.log_function(self.hide_domain, self)
        for db in self.recs["db"].keys():
            for dm in self.recs["db"][db]["dm"].keys():
                if self.recs["db"][db]["dm"][dm]["w_dom"].isVisible():
                    self.recs["db"][db]["dm"][dm]["w_dom"].hide()
        self.editor.disable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.disable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.disable_buttons("edit.box",               # type: ignore
                                    ["add.btn", "clear.btn", "cancel.btn"])

    def show_domain(self,
                    p_dbk: str,
                    p_dmk: str):
        """Activate/Show the selected Record Type Edit Form.

        :args:
            p_dbk: key of database
            p_dmk: key of record (domain) type
        """
        WT.log_function(self.show_domain, self)
        self.hide_domain()
        self.recs["db"][p_dbk]["dm"][p_dmk]["w_dom"].show()
        self.editor.enable_buttons("get.box", ["find.btn"])  # type: ignore
        self.editor.enable_texts("get.box", ["find.inp"])    # type: ignore
        self.editor.enable_buttons("edit.box",               # type: ignore
                                   ["add.btn", "clear.btn", "cancel.btn"])

    def run_domain_edits(self) -> bool:
        """Run the edits associated with the active record type.
        These are executed when an Add or Save button is pressed.
        :returns: (bool) True if all edits pass else False
        """
        WT.log_function(self.run_domain_edits, self)
        db, dm = self.get_active_domain()
        frec, _ = self.get_field_values(db, dm)
        err = ""
        for _, mrec in frec[db][dm].items():
            for _, rec in mrec.items():
                rules = rec["ed"]
                if 'notnull' in rules and \
                        rec["values"] in (None, [], "", ['']):
                    txt = self.recs["msg"]["value_req"]
                    err = f"{txt['a']}  <{rec['title']}> {txt['b']}"
                    break
                if 'posint' in rules:
                    for vix, val in enumerate(rec["values"]):
                        if not val.isnumeric() or int(val) < 1:
                            txt = self.recs["msg"]["value_bad"]
                            txtix = "" \
                                if len(rec["values"]) == 1 else f"[{vix + 1}]"
                            err = (f"{txt['a']}  <{rec['title']}{txtix}> " +
                                   f"{txt['b']}")
                            break
                for edit_rule in ('hostlist', 'yesno', 'namedval'):
                    if edit_rule in rules:
                        for vix, val in enumerate(rec["values"]):
                            if not (self.edit[edit_rule](val)):
                                txt = self.recs["msg"]["value_bad"]
                                txtix = "" \
                                    if len(rec["values"]) == 1 \
                                        else f"[{vix + 1}]"
                                err = (f"{txt['a']} <{rec['title']}{txtix}> " +
                                       f"{txt['b']}")
                                break
                            if err != "":
                                break
                        if err != "":
                            break
            if err != "":
                self.editor.set_dbe_status(err)  # type: ignore
                break
        return (True if err == "" else False)

    # IO Meta Functions
    # ==============================================================
    def get_redis_record(self,
                         p_ns: str,
                         p_key: str):
        """Get a record from Redis DB
        :args: p_ns - name of Redis DB (namespace)
               p_key - key of record to be retrieved
        :returns: records as a dict or None
        """
        WT.log_function(self.get_redis_record, self)
        result = RI.get_record(p_ns, p_key)
        if result is None:
            txt = self.recs["msg"]["rec_not_exist"]
            self.editor.set_dbe_status(  # type: ignore
                f"{txt['a']} {txt['b']} {txt['c']} <{p_key}>")
        else:
            print(f"get_redis_record() Result: {result}")
            # put the values into the editor
            # see notes below
            pass
        return (result)

    def find_redis_keys(self,
                        p_db: str,
                        p_dm: str,
                        p_search: str,
                        p_load_1st_rec: bool = True):
        """Get a list of keys for selected DB matching the pattern.
        :args:
            p_db - name (meta tag) of database
            p_dm - record type (domain) to search
            p_search - pattern (wildcard) to match for keys
            p_load_1st_rec - load 1st record found into editor
                       or not. For example, when validating links,
                       we don't want to actually display the
                       linked record.
        :returns: list of keys that match the pattern, or []
        @DEV:
        - If any changes are pending, enable the Save button, else disable.
          Diagram the process of state management for pending db events.
          What is a "pending" event?
        - Learn about setting expiry rules.
          Consider how to display expiry times. Should be an Audit field.
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
        # Set a rule in a Basement:Config record for each DB/record type
        #   to drive its expiry time.
        """
        WT.log_function(self.find_redis_keys, self)
        nsid = p_db.replace(".db", "")
        keys_b = RI.find_keys(nsid, p_search)
        keys: list = []
        if keys_b in (None, [], {}):
            txt = self.recs["msg"]["rec_not_exist"]
            self.editor.set_dbe_status(   # type: ignore
                f"{txt['a']} {txt['b']} {txt['c']} <{p_search}>")
            self.push_clear_button()
        else:
            for res in keys_b:
                keys.append(res.decode("utf-8"))
            self.KEYS = sorted(keys)
            txt = self.recs["msg"]["recs_found"]
            self.editor.set_dbe_status(   # type: ignore
                f"{txt['a']} {txt['b']} <{len(keys)}> {txt['c']} <{p_search}>")
            if p_load_1st_rec:
                self.ACTIVE_KEY_IX = 0
                if len(self.KEYS) > 1:
                    self.editor.enable_buttons(   # type: ignore
                        "get.box", ["next.btn"])
                self.set_form_values()

        return (keys)

    def validate_links(self,
                       db: str,
                       dm: str,
                       frec: dict):
        """Validate foreign key values before writing to DB.

        :args:
            db - name of db meta tag
            dm - doamin meta tag
            frec - form record values
        :returns: True if all links are valid, False if not
        """
        WT.log_function(self.validate_links, self)
        for _, mrec in frec[db][dm].items():
            for _, rec in mrec.items():
                if "link" in rec["ed"]:
                    for vix, val in enumerate(rec["values"]):
                        link = self.edit["dbkey"](val)
                        if link not in (None, [], (), ""):
                            link_rec = self.find_redis_keys(
                                db, dm, link, p_load_1st_rec=False)
                            if link_rec in (None, {}, []):
                                txt = self.recs["msg"]["link_bad"]
                                txtix = "" \
                                    if len(rec["values"]) == 1 \
                                        else f"[{vix + 1}]"
                                err = (f"{txt['a']} <{rec['title']}{txtix}> " +
                                       f"{txt['b']}")
                                self.editor.set_dbe_status(err)  # type: ignore
                                return False
        return True

    def push_remove_row_button(self):
        """Click the '-' button on last item in an edit list.

        Use '_rmv.btn' to derive the ID of the line edit object.
        """
        WT.log_function(self.push_remove_row_button, self)
        db, dm, fgrp, flid = tuple(
            self.sender().objectName().replace("_rmv.btn", "").split("_"))
        self.remove_row_from_list(db, dm, fgrp, flid)

    def push_find_button(self):
        """Slot for DB Editor Find push button click action.
        @DEV:
        - This is more or less working for now.
        - Come back to it later, as needed.
        """
        WT.log_function(self.push_find_button, self)
        db, dm = self.get_active_domain()
        search = self.get_search_value(dm)
        _ = self.find_redis_keys(
            db.lower(), dm, search, p_load_1st_rec=True)

    def push_next_button(self):
        """Slot for DB Editor Next push button click action."""
        WT.log_function(self.push_next_button, self)
        self.ACTIVE_KEY_IX += 1
        self.editor.enable_buttons(   # type: ignore
            "get.box", ["prev.btn"])
        if len(self.KEYS) == (self.ACTIVE_KEY_IX + 1):
            self.editor.disable_buttons(  # type: ignore
                "get.box", ["next.btn"])
        self.set_form_values()

    def push_prev_button(self):
        """Slot for DB Editor Next push button click action."""
        WT.log_function(self.push_prev_button, self)
        self.ACTIVE_KEY_IX -= 1
        self.editor.enable_buttons(   # type: ignore
            "get.box", ["next.btn"])
        if self.ACTIVE_KEY_IX == 0:
            self.editor.disable_buttons(  # type: ignore
                "get.box", ["prev.btn"])
        self.set_form_values()

    def auto_push_add_button(self):
        """Overlay for push_add_button to use with auto-adds."""
        WT.log_function(self.auto_push_add_button, self)

    def push_add_button(self,
                        p_auto: bool = False,
                        p_db: str = None,
                        p_dm: str = None):
        """Add a record to the DB
        Slot for DB Editor Edit/Add push button click action.
        Also can be based on parameters provided for auto-add logic.
        Get values from active edit form.
        Check to see if record w/key already exists on DB.
        Rejectif rec already exists with Redis key.
        The Redis key value is referenced as the "name".
        :args:
            p_auto - True if this is an auto-add,
                     Default = False if Add button was clicked
            p_db - meta tag of DB to add the record to,
                   Default = None for Add button clicks.
            p_dm - meta tag of domain (record type) to add,
                   Default = None for Add button clicks.
        :returns: (bool) True if record was added, False if not
        """
        WT.log_function(self.push_add_button, self)
        manual_add = True
        if p_db is None or p_dm is None:
            db, dm = self.get_active_domain()
            dbnm = db.replace(".db", "")
            frec, dbrec = self.get_field_values(db, dm)
        else:
            # It is an auto-generated record.
            # Need to specify the DB and record type.
            # Would we still use a Form widget to CREATE the record?
            # hmmm... probably not? But would it be doable? Why not?
            dbnm = p_db.replace(".db", "")
            dm = p_dm
            manual_add = False
            values = self.get_field_values(db, dm)  # how is this set?
            key = f"{dm.lower()}:{RI.UT.get_hash(str(values))}"
            dbrec = {dbnm: {"name": key, "values": values}}
        result = self.get_redis_record(dbnm, dbrec[dbnm]["name"])
        if result in (None, [], {}):
            if self.run_domain_edits():
                if not self.validate_links(db, dm, frec):
                    return False
                if manual_add:
                    dbrec, _ = RI.set_audit_values(dbrec, p_include_hash=True)
                else:
                    dbrec, _ = RI.set_audit_values(dbrec, p_include_hash=False)
                RI.do_insert(dbnm, dbrec)
                txt = self.recs["msg"]["rec_inserted"]
                self.editor.set_dbe_status(   # type: ignore
                    f"{txt['a']} {txt['b']} {txt['c']} <{dbrec['name']}>")
                return True
        else:
            txt = self.recs["msg"]["rec_exists"]
            self.editor.set_dbe_status(   # type: ignore
                txt['a'] + "  " + txt['b'] + " " + txt['c'])
            return False

    def push_clear_button(self):
        """Clear values from the current dom editor form.
        @DEV:
        - Handle list fields properly. Remove values and reduce list length.
        - Can't I just nuke the object and re-create it?
        """
        WT.log_function(self.push_clear_button, self)
        db, dm = self.get_active_domain()
        meta = self.recs["db"][db]["dm"][dm]["rec"]
        dom_wdg = self.recs["db"][db]["dm"][dm]["w_dom"]
        for fgrp, fields in meta.items():
            for ftag, rec in fields.items():
                flid = f"{db}:{dm}:{ftag}.ed"
                if "list" in rec["ed"]:
                    pp((fgrp, flid, ftag, rec))
                    # need to modify flid to be the specific list item (Row)?
                    # if "values" in rec:
                    #    for _ in range(1, len(rec["values"])):
                    #        self.remove_row_from_list(db, dm, fgrp, flid)
                    #    # rec["values"].pop()
                    pass
                else:
                    dom_wdg.findChild(QLineEdit, flid).setText("")
