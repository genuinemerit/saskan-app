#!/usr/bin/python3.9
"""
:module:    se_dbeditor_wdg.py

:author:    GM (genuinemerit @ pm.me)
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
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
    """
    def __init__(self,
                 parent: QWidget,
                 wdg_meta: dict):
        """super() call is required.

        This class is an instance of the QtPy5/pyside2 QWidget class.
        """
        super().__init__(parent)
        self.editor = wdg_meta
        pp(("self.editor", self.editor))
        # self.set_texts_meta()
        # self.set_buttons_meta()
        self.make_db_editor_wdg()

    def get_tools(self):
        """Return modified metadata"""
        return(self.editor)

    def make_title_lbl(self):
        """Create a status text widget."""
        title = QLabel(self.editor["a"])
        title.setStyleSheet(SS.get_style('title'))
        return(title)

    def make_editor_buttons(self,
                            p_box_key: str):
        """Create the buttons defined by the metadata.

        :args:
            p_box_key: str - key to Box meta w/ button defs
        """
        hbox = QHBoxLayout()
        hbox.LeftToRight
        hbox.addStretch()
        hbox.addSpacing(30)
        buttons = self.editor["boxes"][p_box_key]["buttons"]
        for btn_id, button in buttons.items():
            btn = SS.set_button_style(QPushButton(button["a"]))
            buttons[btn_id]["state"] = "inactive"
            buttons[btn_id]["widget"] = btn
        return (hbox)

    def make_text_input(self,
                        p_box_key: str):
        """Create text input widget defined for a box.

        :args:
            p_text_key: str - name of the text input
        :returns: QLineEdit object
        """
        input_text = self.editor["boxes"][p_box_key]["input"]
        txt_wdg = SS.set_line_edit_style(QLineEdit(), False)
        txt_wdg.setPlaceholderText(input_text["b"])
        txt_wdg.setToolTip(input_text["c"])
        txt_wdg.setReadOnly(True)
        txt_wdg.setEnabled(True)
        input_text["state"] = "inactive"
        input_text["widget"] = txt_wdg
        return (txt_wdg)

    def make_box_group(self,
                       p_box_key: str):
        """Make box containers. Put config'd buttons, texts in them.

        :args:
            p_box_key: str - name of the button group
        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        lbl = QLabel(self.editor["boxes"][p_box_key]["a"])
        vbox.addWidget(SS.set_subtitle_style(QLabel(lbl)))
        if "buttons" in self.editor["boxes"][p_box_key]:
            vbox.addLayout(self.make_editor_buttons(p_box_key))
        if "input" in self.editor["boxes"][p_box_key]:
            vbox.addWidget(self.make_text_input(p_box_key))
        return (vbox)

    def make_status_lbl(self):
        """Create a status label widget."""
        status_wdg = SS.set_status_style(
            QLabel(self.editor["status.txt"]["b"]))
        self.editor["status.txt"]["widget"] = status_wdg
        return(status_wdg)

    # Text widgets make functions
    # ============================================================

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

    def set_dbe_status(self,
                       p_text_nm: str = "",
                       p_text: str = ""):
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
        else:
            self.texts["dbe_status"]["widget"].setText(p_text)

    def prep_editor_action(self,
                           p_action_nm: str):
        """Common functions used by DB Editor actions

        :args: p_action_nm - name of button or other widget that
            triggered the actione)
        """
        self.set_dbe_status(p_action_nm)
        self.set_dbe_status()

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
        They are added in a call to RecordMgmt from main app.
        """
        self.setGeometry(620, 40, 550, 840)
        dbe_layout = QVBoxLayout()
        dbe_layout.setAlignment(Qt.AlignTop)
        self.setLayout(dbe_layout)
        dbe_layout.addWidget(self.make_title_lbl())
        dbe_layout.addLayout(self.make_box_group("get.box"))
        dbe_layout.addLayout(self.make_box_group("edit.box"))
        dbe_layout.addWidget(self.make_status_lbl())
        # self.hide()
        self.show()
        self.editor["widget"] = self
