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
# from PySide2.QtWidgets import QCheckBox
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
    Define buttons, forms, texts for filtering
      and editing data on the Redis databases.

    @DEV:
    - Later ==> add similar Class for SQLite or Postgres.
    """
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.set_dbeditor_forms()
        self.set_dbeditor_texts()
        self.set_dbeditor_buttons()
        self.set_dbeditor_selects()
        self.make_dbeditor_widget()

    def set_dbeditor_forms(self):
        """Define metadata for the DB Editor forms.

        @DEV:
        - May want to combine forms and some selects metadata into one dict.
        """
        self.forms: dict = dict()
        forms_template = {
            "db": str(),
            "title": str(),
            "active": True,
            "widget": object}
        forms = {"Configs":
                 {"db": "Basement",
                  "title": "Config Record (Basement DB)",
                  "key": ["Config Category", "Config ID"],
                  "fields": ["Field Name", "Field Value"],
                  "active": False},
                 "States":
                 {"db": "Basement",
                  "title": "State Record (Basement DB)",
                  "key": ["Status Category", "Status ID"],
                  "fields": ["Field Name", "Field Value"],
                  "active": False},
                 "Topics":
                 {"db": "Schema",
                  "title": "Topics Template (Schema DB)",
                  "key": ["Template", "Saskan Topic"],
                  "fields": ["Host", "Port", "Caption", "Description"],
                  "refs": [("Plans", "list")],
                  "active": False}}
        for key in forms.keys():
            self.forms[key] = forms_template.copy()
            for this, do_it in forms[key].items():
                self.forms[key][this] = do_it

    def set_dbeditor_texts(self):
        """Define metadata for the DB Editor Text Inputs.
        """
        self.texts: dict = dict()
        texts_template = {
            "caption": str(),
            "hint": str(),
            "readonly": False,
            "active": True,
            "widget": object}
        texts = {"Key":
                 {"caption": "Search key value",
                  "hint": "Search key value",
                  "active": False},
                 "Cursor":
                 {"caption": "Summary of IO result",
                  "hint": "Cursor/Result summary",
                  "readonly": True,
                  "active": False},
                 "Pending":
                 {"caption": "Summary of pending changes",
                  "hint": "Pending changes",
                  "readonly": True,
                  "active": False}}
        for key in texts.keys():
            self.texts[key] = texts_template.copy()
            for this, do_it in texts[key].items():
                self.texts[key][this] = do_it

    def set_dbeditor_buttons(self):
        """Define metadata for DB Editor button actions."""
        self.acts: dict = dict()
        acts_template = {
            "group": str(),
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        acts = {"Get":
                {"group": "Find Record(s)",
                 "title": "Get/Find Record(s)",
                 "caption": "Retrieve records of selected type. " +
                            "Select all if no key or wildcard entered."},
                "Next":
                {"group": "Find Record(s)",
                 "title": "Get Next Record",
                 "caption": "Retrieve next record from cursor IO result."},
                "Prev":
                {"group": "Find Record(s)",
                 "title": "Get Previous Record",
                 "caption": "Retrieve previous record from cursor IO result."},

                "Add":
                {"group": "Edit Record",
                 "title": "Create a New Record",
                 "caption": "Use current form values to create a new record " +
                            "of the selected type."},
                "Delete":
                {"group": "Edit Record",
                 "title": "Delete a Record",
                 "caption": "Mark the currently selected record for " +
                            " logical delete."},
                "Save":
                {"group": "Edit Record",
                 "title": "Save a Record",
                 "caption": "Commit all pending changes to the " +
                            "pertinent database(s)."},
                "Undo":
                {"group": "Edit Record",
                 "title": "Reverse an Edit",
                 "caption": "Reverse the effect of most recent edit."},
                "Redo":
                {"group": "Edit Record",
                 "title": "Redo an Edit",
                 "caption": "Re-apply the effect of most recently " +
                            "reversed edit."},
                "Cancel":
                {"group": "Edit Record",
                 "title": "Cancel Edits",
                 "caption": "Purge pending edits. Close current " +
                            "edit form without saving."}}
        for key in acts.keys():
            self.acts[key] = acts_template.copy()
            for this, do_it in acts[key].items():
                self.acts[key][this] = do_it

    def set_dbeditor_selects(self):
        """Define metadata for DB Editor checkbox actions.
        """
        self.selects: dict = dict()
        sel_template = {
            "group": str(),
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        selects = {"Configs":
                   {"group": "Basement",
                    "title": "Get Config Records",
                    "caption": "Select records defining configuration data " +
                               "structures."},
                   "States":
                   {"group": "Basement",
                    "title": "Get State Records",
                    "caption": "Select records defining state (status) data " +
                               "structures."},

                   "Topics":
                   {"group": "Schema",
                    "title": "Get Topics Records",
                    "caption": "Select records holding Topic definitions."},
                   "Plans":
                   {"group": "Schema",
                    "title": "Get Plans Records",
                    "caption": "Select records holding Plan definitions."},
                   "Services":
                   {"group": "Schema",
                    "title": "Get Services Records",
                    "caption": "Select records holding Service definitions."},
                   "Schemas":
                   {"group": "Schema",
                    "title": "Get Schema Records",
                    "caption": "Select records holding Schema definitions."},

                   "Requests":
                   {"group": "Harvest",
                    "title": "Get Request or Subscribe Packages",
                    "caption": "Select records holding Request packages." +
                               "This includes Subscriptions."},
                   "Responses":
                   {"group": "Harvest",
                    "title": "Get Response or Publish Packages",
                    "caption": "Select records holding Response packages." +
                               "This includes Publications."},

                   "Expirations":
                   {"group": "Rules",
                    "title": "Get Expiration rules",
                    "caption": "Select records holding definition of " +
                               "expiration/purge rules for packages."},
                   "Retry Rate":
                   {"group": "Rules",
                    "title": "Get Retry Rate rules",
                    "caption": "Select records defining timing of retries" +
                               "for certain types of failed requests."},
                   "Retry Limit":
                   {"group": "Rules",
                    "title": "Get Retry Limit rules",
                    "caption": "Select records defining count of retries " +
                               "for certain types of failed requests."}}
        for key in selects.keys():
            self.selects[key] = sel_template.copy()
            for this, do_it in selects[key].items():
                self.selects[key][this] = do_it

    def make_subtitle(self, p_title: str):
        """Generic function to make a sub-title widget.

        :args: p_title: str - the subtitle text
        :returns: QLabel - the subtitle label object
        """
        title = QLabel(p_title)
        title.setStyleSheet(SS.get_style('subtitle'))
        title.setFont(QFont('Arial', 9))
        return (title)

    def set_form_widget(self, p_form_key: str):
        """Generic method for setting up a db form widget
        
        @DEV
        - Probably need more space for the form widget
        - Consider overlaying the Help or Control or Monitor
          spaces with the Diagram widget instead of trying to
          squeeze it in below the Editor.
        """
        if p_form_key in self.forms.keys():
            meta = self.forms[p_form_key]
            dbe_widget = QWidget()
            dbe_layout = QVBoxLayout()
            dbe_widget.setLayout(dbe_layout)
            title = QLabel(meta['title'])
            title.setStyleSheet(SS.get_style('title'))
            dbe_layout.addWidget(title)
            dbe_form = QFormLayout()
            dbe_form.setLabelAlignment(Qt.AlignRight)
            dbe_form.addWidget(self.make_subtitle("Key"))
            for field_nm in meta['key']:
                dbe_form.addRow(field_nm, SS.set_line_edit_style(QLineEdit()))
            dbe_form.addWidget(self.make_subtitle("Fields"))
            for field_nm in meta['fields']:
                dbe_form.addRow(field_nm, SS.set_line_edit_style(QLineEdit()))
            if 'refs' in meta.keys():
                # "refs": [("Plans", "list")],
                dbe_form.addWidget(self.make_subtitle("Links"))
                for link in meta['refs']:
                    dbe_form.addRow(link[0], SS.set_line_edit_style(QLineEdit()))
                    # If "list" then add some kind of widget to allow entering
                    # multiple values. Maybe a button or hyperlink with "more..."
                    # or "+".
            dbe_layout.addLayout(dbe_form)
            return (dbe_widget)

    def make_dbe_forms(self):
        """Generate a form widget for each record type.

        Everything is driven by metadata.
        """
        for form_key in self.forms.keys():
            dbe_widget = self.set_form_widget(form_key)
            self.edt_layout.addWidget(dbe_widget)
            self.forms[form_key]["widget"] = dbe_widget
            dbe_widget.hide()

    def make_dbe_record_selects(self):
        """Define Select Groups components of the Service Monitor widget."""
        self.edt_layout.addWidget(
            self.make_subtitle("Select a Record Type"))
        for grp in ("Basement", "Schema", "Harvest", "Rules"):
            sel_hbx = QHBoxLayout()
            for key, val in {k: v for k, v in self.selects.items()
                             if v["group"] == grp}.items():
                sel_click = QRadioButton(key)
                sel_click.setStyleSheet(SS.get_style('checkbox'))
                sel_click.setFont(QFont('Arial', 9))
                sel_hbx.addWidget(sel_click)
                self.selects[key]["widget"] = sel_click
            sel_hbx.addStretch(1)
            self.edt_layout.addLayout(sel_hbx)

    def make_dbe_find_key_input(self):
        """Define the text input for find by key.

        :returns: QLineEdit object
        """
        sel_txt = QLineEdit()
        sel_txt.setStyleSheet(SS.get_style('inactive_editor'))
        sel_txt.setFont(QFont('Arial', 9))
        sel_txt.setPlaceholderText(self.texts["Key"]["hint"])
        sel_txt.setEnabled(False)
        self.texts["Key"]["widget"] = sel_txt
        return (sel_txt)

    def set_up_push_button(self, p_key: str):
        """Generic function for initializing a push button object.

        :args: p_key - key/name for the button
        :returns: QPushButton object
        """
        btn = SS.set_button_style(QPushButton(p_key))
        btn.setStyleSheet(SS.get_style('inactive_button'))
        btn.setEnabled(False)
        self.acts[p_key]["widget"] = btn
        return (btn)

    def make_dbe_find_buttons(self):
        """Define Find Button components of the Data Base Editor widget.
           Plus the text input for find by key.
        """
        grp = "Find Record(s)"
        self.edt_layout.addWidget(self.make_subtitle(grp))
        btn_hbx = QHBoxLayout()
        for key, val in {k: v for k, v in self.acts.items()
                         if v["group"] == grp}.items():
            btn = self.set_up_push_button(key)
            btn_hbx.addWidget(btn)
        # Add key-input text box
        btn_hbx.addWidget(self.make_dbe_find_key_input())
        btn_hbx.addStretch(1)
        self.edt_layout.addLayout(btn_hbx)

    def make_dbe_edit_buttons(self):
        """Define Edit Button components of the Data Base Editor widget."""
        grp = "Edit Record"
        self.edt_layout.addWidget(self.make_subtitle(grp))
        btn_hbx = QHBoxLayout()
        for key, val in {k: v for k, v in self.acts.items()
                         if v["group"] == grp}.items():
            btn = self.set_up_push_button(key)
            btn_hbx.addWidget(btn)
        btn_hbx.addStretch(1)
        self.edt_layout.addLayout(btn_hbx)

    def make_dbe_cursor_display(self):
        """Define the text display for IO Cursor result.

        :returns: QLineEdit object (readonly)
        """
        disp_txt = QLineEdit()
        disp_txt.setStyleSheet(SS.get_style('inactive_editor'))
        disp_txt.setFont(QFont('Arial', 9))
        disp_txt.setReadOnly(True)
        disp_txt.setPlaceholderText(self.texts["Cursor"]["hint"])
        self.texts["Cursor"]["widget"] = disp_txt
        self.edt_layout.addWidget(disp_txt)

    def make_dbeditor_widget(self):
        """Define components of the Data Base Editor widget."""
        self.setGeometry(620, 40, 550, 600)
        self.edt_layout = QVBoxLayout()
        self.edt_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.edt_layout)
        edt_btns_vbx = QVBoxLayout()
        self.edt_layout.addLayout(edt_btns_vbx)
        self.make_dbe_record_selects()
        self.make_dbe_find_buttons()
        self.make_dbe_edit_buttons()
        self.make_dbe_cursor_display()
        self.show()
        # self.make_dbe_configs_form()
        self.make_dbe_forms()
        # self.make_dbs_states_form()
