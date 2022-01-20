#!/usr/bin/python3.9
"""
:module:    se_dbeditor_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QCheckBox
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QRadioButton
# from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()


class DBEditorWidget(QWidget):
    """Build container for the DB Editor components.

    Define/enable the DB Editor functions widget.
    Define the checkboxes, buttons and actions for filtering
      and editing data on the Redis databases.
    Later ==> similar functions for SQLite or MariaDB's.k.
    """
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.acts: dict = dict()
        self.selects: dict = dict()
        self.texts: dict = dict()
        self.set_dbeditor_actions()
        self.set_dbeditor_selects()
        self.set_dbeditor_texts()
        self.make_dbeditor_widget()

    def set_dbeditor_actions(self):
        """Define metadata for DB Editor button actions.

        @DEV:
        - Here and in other widget classes, consider how to define
          metadata rules managing interactions between buttons.
        - For example, "button A" should be active only when such-and-such
          an activity is pending.
        - It may be better to store event queues in these classes rather than
          in the parent application class.
        """
        acts_template = {
            "group": str(),
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        acts = {"Get":
                {"group": "Find Records",
                 "title": "Get/Find Record(s)",
                 "caption": "Retrieve records from selected DB(s) " +
                            "using the selected filter(s)."},
                "Next":
                {"group": "Find Records",
                 "title": "Get Next Record",
                 "caption": "Retrieve next record from selected DB(s) " +
                            "using the selected filter(s)."},
                "Prev":
                {"group": "Find Records",
                 "title": "Get Previous Record",
                 "caption": "Retrieve previous record from selected DB(s) " +
                            "using the selected filter(s)."},
                "Add":
                {"group": "Edit Records",
                 "title": "Create a New Record",
                 "caption": "Provide a form for creating a new record " +
                            "using the selected filter(s)."},
                "Delete":
                {"group": "Edit Records",
                 "title": "Delete a Record",
                 "caption": "Mark the currently selected record for " +
                            " logical delete."},
                "Save":
                {"group": "Edit Records",
                 "title": "Save a Record",
                 "caption": "Commit currently pending changes to the " +
                            "pertinent database(s)."},
                "Undo":
                {"group": "Edit Records",
                 "title": "Reverse an Edit",
                 "caption": "Reverse the effect of the most recent " +
                            "pending edit."},
                "Redo":
                {"group": "Edit Records",
                 "title": "Redo an Edit",
                 "caption": "Re-apply the effect of the most recently " +
                            "reversed edit."},
                "Cancel":
                {"group": "Edit Records",
                 "title": "Cancel an Edit",
                 "caption": "Purge all pending edits. This means to " +
                            "quit DB Editor mode without saving."}}
        for key in acts.keys():
            self.acts[key] = acts_template.copy()
            for this, do_it in acts[key].items():
                self.acts[key][this] = do_it

    def set_dbeditor_selects(self):
        """Define metadata for DB Editor checkbox actions.
    - Select DB:
        - checkboxes -> Sandbox, Schema, Harvest, Log, Monitor
    - Select Record:
        - checkboxes -> All, Primitives, Topics, Plans, Services,
        Schema, Requests, Responses
        - text -> by-key, by-key-regex
    - Select Rules:
        - checkboxes -> Expirations, Retry-rate, Retry-limit
        """
        sel_template = {
            "group": str(),
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        selects = {"Sandbox DB":
                   {"group": "Select DB",
                    "title": "Select Sandbox DB",
                    "caption": "Edit the Sandbox database, " +
                               "which is Redis namespace #0."},
                   "Schema DB":
                   {"group": "Select DB",
                    "title": "Select Schema DB",
                    "caption": "Edit the Schema database, " +
                               "which is Redis namespace #1."},
                   "Harvest DB":
                   {"group": "Select DB",
                    "title": "Select Harvest DB",
                    "caption": "Edit the Harvest database, " +
                               "which is Redis namespace #2."},
                   "Log DB":
                   {"group": "Select DB",
                    "title": "Select Log DB",
                    "caption": "Edit the Log database, " +
                               "which is Redis namespace #3."},
                   "Monitor DB":
                   {"group": "Select DB",
                    "title": "Select Monitor DB",
                    "caption": "Edit the Monitor database, " +
                               "which is Redis namespace #4."},
                   "All":
                   {"group": "Select Records",
                    "title": "Get All Records",
                    "caption": "Select all records matching current filters."},
                   "Prims":
                   {"group": "Select Records",
                    "title": "Get Primitive Records",
                    "caption": "Select records definig primitive data " +
                               "structures or data types."},
                   "Topics":
                   {"group": "Select Records",
                    "title": "Get Topics Records",
                    "caption": "Select records holding Topic definitions."},
                   "Plans":
                   {"group": "Select Records",
                    "title": "Get Plans Records",
                    "caption": "Select records holding Plan definitions."},
                   "Services":
                   {"group": "Select Records",
                    "title": "Get Services Records",
                    "caption": "Select records holding Service definitions."},
                   "Schemas":
                   {"group": "Select Records",
                    "title": "Get Schema Records",
                    "caption": "Select records holding Schema definitions."},
                   "Requests":
                   {"group": "Select Packages",
                    "title": "Get Request or Subscribe Packages",
                    "caption": "Select records holding Request packages." +
                               "This includes Subscriptions."},
                   "Responses":
                   {"group": "Select Packages",
                    "title": "Get Response or Publish Packages",
                    "caption": "Select records holding Response packages." +
                               "This includes Publications."},
                   "Expirations":
                   {"group": "Select Rules",
                    "title": "Get Expiration rules",
                    "caption": "Select records holding definition of " +
                               "expiration/purge rules for packages."},
                   "Retry Rate":
                   {"group": "Select Rules",
                    "title": "Get Retry Rate rules",
                    "caption": "Select records defining timing of retries" +
                               "for certain types of failed requests."},
                   "Retry Limit":
                   {"group": "Select Rules",
                    "title": "Get Retry Limit rules",
                    "caption": "Select records defining count of retries " +
                               "for certain types of failed requests."}}
        for key in selects.keys():
            self.selects[key] = sel_template.copy()
            for this, do_it in selects[key].items():
                self.selects[key][this] = do_it

    def set_dbeditor_texts(self):
        """Define metadata for DB Editor text inputs.

        Not sure it is really necessary to have a separate function for these.
        - Select Record:
            - text -> by-key
        """
        txts_template = {
            "group": str(),
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        txts = {"Key":
                {"group": "Select Records",
                 "title": "Find by Key",
                 "caption": "Retrieve records from selected DB(s) " +
                            "for specific key or key-regex."}}
        for key in txts.keys():
            self.texts[key] = txts_template.copy()
            for this, do_it in txts[key].items():
                self.texts[key][this] = do_it

    def make_dbeditor_forms(self):
        """Define Forms components of the Service Monitor widget.

        The forms layout thing is nice. Will probably want to specify
        different patterns based on different record types. May also
        want to create a regular text edit box for showing search results.

        It might make sense to embed the forms themselves inside yet
        another widget so they are easy to hide/show. Afaik, that only
        works with the "native" widget object.

        Deciding which form or text box to show should be driven by
        what actions have been taken, what is pending in the event queue,
        what filters are set, and so on.

        The edit fields defined so far are just examples to show how the
        form layout works.
        """
        # self.dbedit_form = QTextEdit()
        catg_name_txt = SS.set_line_edit_style(QLineEdit())
        subcatg_name_txt = SS.set_line_edit_style(QLineEdit())
        catg_vers_txt = SS.set_line_edit_style(QLineEdit())
        topic_txt = SS.set_line_edit_style(QLineEdit())
        msg_name_txt = SS.set_line_edit_style(QLineEdit())
        msg_action_txt = SS.set_line_edit_style(QLineEdit())
        topic_vers_txt = SS.set_line_edit_style(QLineEdit())
        value_name_txt = SS.set_line_edit_style(QLineEdit())
        value_context_txt = SS.set_line_edit_style(QLineEdit())
        hash_id_txt = SS.set_line_edit_style(QLineEdit())
        timestamp_txt = SS.set_line_edit_style(QLineEdit())
        self.dbedit_form = QFormLayout()
        self.dbedit_form.setLabelAlignment(Qt.AlignRight)
        self.dbedit_form.addRow("Category:", catg_name_txt)
        self.dbedit_form.addRow("Sub-Category:", subcatg_name_txt)
        self.dbedit_form.addRow("Category Version:", catg_vers_txt)
        self.dbedit_form.addRow("Topic:", topic_txt)
        self.dbedit_form.addRow("Message Name:", msg_name_txt)
        self.dbedit_form.addRow("Message Action:", msg_action_txt)
        self.dbedit_form.addRow("Topic Version:", topic_vers_txt)
        self.dbedit_form.addRow("Value Name:", value_name_txt)
        self.dbedit_form.addRow("Value Context:", value_context_txt)
        self.dbedit_form.addRow("Hash ID:", hash_id_txt)
        self.dbedit_form.addRow("Last Update Timestamp:", timestamp_txt)
        # self.dbedit_form.setStyleSheet(SS.get_style('active_editor'))
        self.edt_layout.addLayout(self.dbedit_form)

    def make_dbeditor_db_selects(self):
        """Define Select DBs group components of the Service Monitor widget."""
        grp = "Select DB"
        title = QLabel(grp)
        title.setStyleSheet(SS.get_style('subtitle'))
        title.setFont(QFont('Arial', 9))
        self.edt_layout.addWidget(title)
        sel_hbx = QHBoxLayout()
        for key, val in {k: v for k, v in self.selects.items()
                         if v["group"] == grp}.items():
            sel_click = QRadioButton(key)
            sel_click.setStyleSheet(SS.get_style('radiobtn'))
            sel_click.setFont(QFont('Arial', 9))
            sel_hbx.addWidget(sel_click)
        sel_hbx.addStretch(1)
        self.edt_layout.addLayout(sel_hbx)

    def make_dbeditor_find_buttons(self):
        """Define Find Button components of the Service Monitor widget.
           plus the text input for find by key.
        """
        grp = "Find Records"
        title = QLabel(grp)
        title.setStyleSheet(SS.get_style('subtitle'))
        title.setFont(QFont('Arial', 9))
        self.edt_layout.addWidget(title)
        btn_hbx = QHBoxLayout()
        for key, val in {k: v for k, v in self.acts.items()
                         if v["group"] == grp}.items():
            btn = SS.set_button_style(QPushButton(key))
            btn_hbx.addWidget(btn)
        sel_txt = QLineEdit()
        sel_txt.setStyleSheet(SS.get_style('editor'))
        sel_txt.setFont(QFont('Arial', 9))
        sel_txt.setPlaceholderText("Key or regex")
        btn_hbx.addWidget(sel_txt)
        btn_hbx.addStretch(1)
        self.edt_layout.addLayout(btn_hbx)

    def make_dbeditor_rec_selects(self):
        """Define Select Groups components of the Service Monitor widget."""
        for grp in ("Select Records", "Select Packages", "Select Rules"):
            title = QLabel(grp)
            title.setStyleSheet(SS.get_style('subtitle'))
            title.setFont(QFont('Arial', 9))
            self.edt_layout.addWidget(title)
            sel_hbx = QHBoxLayout()
            for key, val in {k: v for k, v in self.selects.items()
                             if v["group"] == grp}.items():
                sel_click = QCheckBox(key)
                sel_click.setStyleSheet(SS.get_style('checkbox'))
                sel_click.setFont(QFont('Arial', 9))
                sel_hbx.addWidget(sel_click)
            sel_hbx.addStretch(1)
            self.edt_layout.addLayout(sel_hbx)

    def make_dbeditor_edit_buttons(self):
        """Define Edit Button components of the Service Monitor widget.
        """
        grp = "Edit Records"
        title = QLabel(grp)
        title.setStyleSheet(SS.get_style('subtitle'))
        title.setFont(QFont('Arial', 9))
        self.edt_layout.addWidget(title)
        btn_hbx = QHBoxLayout()
        for key, val in {k: v for k, v in self.acts.items()
                         if v["group"] == grp}.items():
            btn = SS.set_button_style(QPushButton(key))
            btn_hbx.addWidget(btn)
        btn_hbx.addStretch(1)
        self.edt_layout.addLayout(btn_hbx)

    def make_dbeditor_widget(self):
        """Define components of the Service Monitor widget.
        Do in this order:
        - Select DB radio buttons
        - Edit Records push buttons + key input
        - Select Records filters (checkboxes)
        - Edit DB push buttons
        """
        self.setGeometry(620, 40, 550, 600)
        self.edt_layout = QVBoxLayout()
        self.setLayout(self.edt_layout)
        title = QLabel("DB Editor")
        title.setStyleSheet(SS.get_style('title'))
        self.edt_layout.addWidget(title)
        self.make_dbeditor_forms()
        edt_btns_vbx = QVBoxLayout()
        self.edt_layout.addLayout(edt_btns_vbx)
        self.make_dbeditor_find_buttons()
        self.make_dbeditor_db_selects()
        self.make_dbeditor_rec_selects()
        self.make_dbeditor_edit_buttons()
