#!/usr/bin/python3.9
"""
:module:    se_dbeditor_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
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
        self.set_texts_meta()
        self.set_buttons_meta()
        self.set_rect_meta()
        self.make_db_editor_wdg()

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
                 "link_fields": {"display": "Link Fields"},
                 "dbe_status": {"display": "Database Editor Status"},
                 "Key": {"hint": "Search key value"},
                 "Cursor": {"hint": "Cursor/Result summary"},
                 "Pending": {"hint": "Pending changes"},
                 "Keys": {"display": "Key Fields"},
                 "Values": {"display": "Value Fields"},
                 "Links": {"display": "Link Fields"},
                 "Types": {"display": "Select Record Type"},
                 "Find": {"display": "Find Record(s)"},
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
                 "Get": {"caption": "Retrieve records of selected type. " +
                         "Select all if no key or wildcard entered."},
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
                 "More": {"caption":
                          "Add another input field for Links."},
                 "Fewer": {"caption":
                           "Remove an input field for Links."},
                 "Max More": {"caption":
                              "Cannot add more Links. Maximum reached."},
                 "Min Fewer": {"caption":
                               "Cannot remove more Links. Minimum reached."}}
        for key in texts.keys():
            self.texts[key] = texts_template.copy()
            for this, do_it in texts[key].items():
                self.texts[key][this] = do_it

    # Text-widget helper functions
    # ============================================================
    def get_hint(self, p_text_key: str) -> str:
        """Return the hint (placeholder) value for a text item.

        :args: p_text_key: str - key to the text metadata
        :returns: str - the hint value
        """
        return (self.texts[p_text_key]["hint"])

    def set_cursor_result(self, p_text: str):
        """Assign text to Cursor result display."""
        self.activate_texts(["Cursor"])
        self.texts["Cursor"]["widget"].setText(p_text)

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
        txt_wdg.setPlaceholderText(self.get_hint(p_text_key))
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
            "Find": {"Get": {},
                     "Next": {},
                     "Prev": {}},
            "Edit": {"Add": {},
                     "Delete": {},
                     "Save": {},
                     "Undo": {},
                     "Redo": {},
                     "Cancel": {"action": self.push_cancel}},
            "Links": {"More": {"action": self.push_more_links},
                      "Fewer": {"action": self.push_fewer_links}}}
        for grp in self.buttons.keys():
            for btn_nm in self.buttons[grp].keys():
                for item in button_template.keys():
                    if item not in self.buttons[grp][btn_nm].keys():
                        self.buttons[grp][btn_nm][item] = button_template[item]

    # Push-button helper functions
    # ============================================================

    def make_push_button_wdg(self,
                             p_grp: str,
                             p_key: str):
        """Instantiate a push button object.

        By default, they are set up in an inactive state.

        :args:
            p_grp - metadata group for the button
            p_key - metadata key for the button
        :returns: QPushButton object
        """
        btn = SS.set_button_style(QPushButton(p_key), False)
        btn.setEnabled(False)
        if self.buttons[p_grp][p_key]["action"] is not None:
            btn.clicked.connect(self.buttons[p_grp][p_key]["action"])
        self.buttons[p_grp][p_key]["widget"] = btn
        self.buttons[p_grp][p_key]["active"] = False
        return (btn)

    def make_button_group_wdg(self,
                              p_grp: str,
                              p_use_stt: bool = True,
                              p_activate: bool = False):
        """Make containers and put buttons in them.

        Default is that buttons are not activated.
        Optionally include a subtitle with it.
        Optionally activate buttons.

        :args:
            p_grp: str - name of the button group
            p_use_stt: bool - whether to include a subtitle
            p_activate: bool - whether to activate buttons
        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        if p_use_stt:
            vbox.addWidget(self.make_text_subttl_wdg(p_grp))
        hbox = QHBoxLayout()
        btn_list = list()
        for btn_nm, btn_attrs in self.buttons[p_grp].items():
            btn = self.make_push_button_wdg(p_grp, btn_nm)
            btn_list.append(btn_nm)
            hbox.addWidget(btn)
        if p_activate:
            self.activate_buttons(p_grp, btn_list)
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

    def select_record_type(self, p_rect_nm: str):
        """Generic function for record type selection actions.

        :args:
            p_rect_nm: name of selected record type"""
        self.show_status(p_rect_nm)
        self.activate_rect(p_rect_nm)

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
        self.deactivate_rect()

    def get_links_form(self):
        """Get links form for a specified record type.

        :returns: tuple (
            QFormLayout object or None,
            name (label) of the links field
            count of rows in the form or Zero)
        """
        link_form = None
        field_nm = None
        row_count = 0
        done = False
        self.show_status("More")
        for db in self.rects.keys():
            for rect, attrs in self.rects[db].items():
                if attrs["active"]:
                    # The last edit form is the one for Links
                    # Going with this method until I can figure
                    # out how to assign an ID to a form object.
                    forms = attrs["widget"].findChildren(QFormLayout)
                    field_nm = attrs['link_fields'][0]
                    link_form = forms[len(forms) - 1]
                    row_count = link_form.rowCount()
                    done = True
                    break
            if done:
                break
        return (link_form, field_nm, row_count)

    def push_more_links(self):
        """Add another input row to form for Links.
        """
        link_form, field_nm, row_count = self.get_links_form()
        if row_count > 4:
            self.show_status("Max More")
        else:
            self.show_status("More")
            link_form.insertRow(
                link_form.rowCount(), field_nm,
                SS.set_line_edit_style(QLineEdit()))

    def push_fewer_links(self):
        """Remove one input row from the form for Links.

        Not quite... I want the "link" form within the rect.
        """
        link_form, field_nm, row_count = self.get_links_form()
        if row_count < 2:
            self.show_status("Min Fewer")
        else:
            self.show_status("Fewer")
            link_form.removeRow(row_count - 1)

    # Record Type Editor Widget Creation
    # ============================================================

    def set_rect_meta(self):
        """Define metadata for the DB Editors for each Record Type.

        The 'rect' widget is a container for input rows and buttons
        for each Record Type. This metadata is used to generate both
        the editor widget and items in a radio button group to select
        which rect to edit.

        Each 'rect' widget holds one or more form widgets and may
        also have some buttons, subtitles and other objects.

        Each form widget holds one or more input rows.
        In some cases, the number of input rows may be variable,
        per user inputs.
        """
        rect_template = {
            "db": str(),
            "key_fields": None,
            "value_fields": None,
            "link_fields": None,
            "active": False,
            "selector": None,
            "select_action": None,
            "widget": None}
        self.rects = {"Basement": {
                        "Configs": {
                          "key_fields": ["Config Category", "Config ID"],
                          "value_fields": ["Field Name", "Field Value"],
                          "select_action": self.select_configs},
                        "Status": {
                          "key_fields": ["Status Category", "Status ID"],
                          "value_fields": ["Field Name", "Field Value"],
                          "select_action": self.select_status},
                        "Expire Rules": {},
                        "Retry Rules": {}},
                      "Schema":  {
                        "Topics": {
                          "key_fields": ["Template", "Saskan Topic"],
                          "value_fields": ["Host", "Port", "Caption", "Desc"],
                          "link_fields": ["Plans"],
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
        for key in self.rects.keys():
            for rect in self.rects[key].keys():
                for field, value in rect_template.items():
                    if field not in self.rects[key][rect].keys():
                        self.rects[key][rect][field] = value

    # Record Type Editor Widget helper functions
    # ============================================================

    def make_rect_selectors(self):
        """Return a collection(s) of radio buttons for selecting rect type."""
        vbox = QVBoxLayout()
        vbox.addWidget(self.make_text_subttl_wdg("Types"))
        for db in self.rects.keys():
            hbox = QHBoxLayout()
            for rect in self.rects[db].keys():
                rdo_btn = SS.set_radiobtn_style(QRadioButton(rect))
                if self.rects[db][rect]["select_action"] is not None:
                    rdo_btn.clicked.connect(
                        self.rects[db][rect]["select_action"])
                hbox.addWidget(rdo_btn)
                # hbox.addStretch(1)
                self.rects[db][rect]["selector"] = rdo_btn
            vbox.addLayout(hbox)
        return (vbox)

    def make_rect_wdg(self,
                      db_nm: str,
                      rect_nm: str):
        """Return a container widget for selected db/rect type."""
        rect_wdg = QWidget()
        rect_layout = QVBoxLayout()
        show_fields = ["key_fields", "value_fields", "link_fields"]
        rect_layout.addWidget(self.make_text_subttl_wdg(rect_nm))
        for f_grp in show_fields:
            if self.rects[db_nm][rect_nm][f_grp] is not None:
                rect_layout.addWidget(self.make_text_subttl_wdg(f_grp))
                if f_grp == "link_fields":
                    rect_layout.addLayout(
                        self.make_button_group_wdg("Links", False, True))
                form = QFormLayout()
                form.setLabelAlignment(Qt.AlignRight)
                for field in self.rects[db_nm][rect_nm][f_grp]:
                    form.addRow(field, SS.set_line_edit_style(QLineEdit()))
                rect_layout.addLayout(form)
        rect_wdg.setLayout(rect_layout)
        self.rects[db_nm][rect_nm]["widget"] = rect_wdg
        rect_wdg.hide()
        return (rect_wdg)

    # Record Type Editor Widget slot actions
    # ============================================================

    def activate_rect(self,
                      p_rec: str):
        """Deactivate a Record Type Edit widget.

        :args: p_rec: str name of record type editor widget to activate.
        """
        done = False
        self.deactivate_rect()
        for db in self.rects.keys():
            for rect, attrs in self.rects[db].items():
                if rect == p_rec and attrs["active"] is False:
                    attrs["active"] = True
                    attrs["widget"].show()
                    self.activate_buttons("Edit", ["Cancel"])
                    self.activate_buttons("Find", ["Get"])
                    self.activate_texts(["Key", "Cursor"])
                    done = True
                    break
            if done:
                break

    def deactivate_rect(self):
        """Deactivate the active Record Type Edit widget."""
        done = False
        for db in self.rects.keys():
            for rect, attrs in self.rects[db].items():
                if attrs["active"]:
                    attrs["active"] = False
                    attrs["selector"].setChecked(False)
                    attrs["widget"].hide()
                    self.deactivate_buttons("Edit", ["Cancel"])
                    self.deactivate_buttons("Find", ["Get", "Next", "Prev"])
                    self.deactivate_texts(["Key", "Cursor"])
                    done = True
                    break
            if done:
                break

    # Database Editor Widget Creation
    # ============================================================

    def make_db_editor_wdg(self):
        """Create all components of Data Base Editor widget.
        """
        self.setGeometry(620, 40, 550, 840)
        self.dbe_layout = QVBoxLayout()
        self.dbe_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.dbe_layout)
        self.dbe_layout.addLayout(self.make_rect_selectors())
        vbox = self.make_button_group_wdg("Find")
        vbox.addWidget(self.make_text_input_wdg("Key", False))
        self.dbe_layout.addLayout(vbox)
        self.dbe_layout.addLayout(self.make_button_group_wdg("Edit"))
        self.dbe_layout.addWidget(self.make_text_input_wdg("Cursor"))
        for db, rects in self.rects.items():
            for rect in rects.keys():
                self.dbe_layout.addWidget(self.make_rect_wdg(db, rect))
        self.dbe_layout.addWidget(self.make_text_status_wdg("dbe_status"))
        self.show()
