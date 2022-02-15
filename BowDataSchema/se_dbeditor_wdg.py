#!/usr/bin/python3.9
"""
:module:    se_dbeditor_wdg.py

:author:    GM (genuinemerit @ pm.me)
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
# from PySide2.QtCore import QRegExp
# from PySide2.QtGui import QRegExpValidator
# from PySide2.QtGui import QIntValidator
# from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
# from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()


class DBEditorWidget(QWidget):
    """Build container for the DB Editor components.

    Define/enable the DB Editor functions widget.
    Define buttons, texts for making the DB Editor widgets.

    Functions relating to set-up, set, get of specific
    record types are defined in the closely-related
    RecordMgmt class.

    @DEV - 
    May want to look at use of QStackedWidget or, even better,
    .setCurrentIndex(), to determine order of items within the
    editor widget. OR mayhbe it is insertWidget(index, widget),
    which is used with QStackedWidget.

    This might make it easier to break things out in to sub-classes,
    i.e. so I don't necessarily have to build the sub-widgets in the
    order that I want them displayed.
    """
    def __init__(self, parent: QWidget):
        """super() call is required.

        This class is an instance of the QtPy5/pyside2 QWidget class.
        """
        super().__init__(parent)
        self.set_texts_meta()
        self.set_buttons_meta()
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
                 "Queues": {
                    "display": "Queue Records (Harvest DB)",
                    "caption": "Records holding temporary lists."},
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

    # Text widgets make functions
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
        search_key = self.RM.edit["redis_key"](search_key)
        if f"{rectyp_nm}:" not in search_key:
            search_key = f"{rectyp_nm}:{search_key}"
        if search_key[:1] != "*":
            search_key = "*" + search_key
        if search_key[-1:] != "*":
            search_key += "*"
        return (db_nm, search_key.lower())

    def set_cursor_result(self,
                          p_text: str = ""):
        """Assign text to Cursor result display."""
        self.activate_texts(["Cursor"])
        self.texts["Cursor"]["widget"].setText(p_text)

    def set_dbe_status(self, p_text_nm: str):
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
        self.set_dbe_status(p_action_nm)
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
        self.set_dbe_status(p_rectyp_nm)
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

    def select_queues(self):
        """Slot for Editor Select Queues radio check action"""
        self.select_record_type("Queues")

    def push_cancel(self):
        """Slot for Editor Edit Push Button --> Cancel"""
        self.set_dbe_status("Cancel")
        self.deactivate_rectyp()

    def add_row_to_list(self):
        """Add an input row to form for list of fields.
        """
        list_nm = self.sender().objectName().split(":")[1].split(".")[0]
        list_values, list_form = self.get_list_fields(list_nm)
        rowcnt = len(list_values)
        if rowcnt > 4:
            self.set_dbe_status("Max More")
        else:
            self.set_dbe_status("More")
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
            self.set_dbe_status("Min Fewer")
        else:
            self.set_dbe_status("Fewer")
            list_form.removeRow(rowcnt - 1)

    # Database Editor Widget make function
    # ============================================================

    def make_db_editor_wdg(self):
        """Create all components of Data Base Editor widget.

        Except for the Record Type forms.
        """
        self.setGeometry(620, 40, 550, 840)
        self.dbe_layout = QVBoxLayout()
        self.dbe_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.dbe_layout)
        # self.dbe_layout.addLayout(self.RM.make_rectyp_selectors())
        vbox = self.make_button_group_wdg("Get")
        vbox.addWidget(self.make_text_input_wdg("Key", False))
        self.dbe_layout.addLayout(vbox)
        self.dbe_layout.addLayout(self.make_button_group_wdg("Edit"))
        self.dbe_layout.addWidget(self.make_text_input_wdg("Cursor"))
        # for db, rectyps in self.RM.rectyps.items():
        #     for rectyp in rectyps.keys():
        #         self.dbe_layout.addWidget(
        #           self.RM.make_rectyp_wdg(db, rectyp))
        self.dbe_layout.addWidget(self.make_text_status_wdg("dbe_status"))
        # self.show()
