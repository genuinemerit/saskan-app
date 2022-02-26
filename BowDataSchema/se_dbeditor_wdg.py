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
        self.make_db_editor_wdg()

    def get_tools(self):
        """Return modified metadata"""
        return(self.editor)

    # Database Editor Widget make functions
    # ============================================================
    def make_title_lbl(self):
        """Create a status text widget."""
        title = QLabel(self.editor["a"])
        title.setStyleSheet(SS.get_style('title'))
        return(title)

    def make_editor_buttons(self,
                            p_box: str):
        """Create the buttons defined by the metadata.

        :args:
            p_box: str - key to Box meta w/ button defs
        """
        hbox = QHBoxLayout()
        hbox.LeftToRight
        hbox.addStretch()
        hbox.addSpacing(30)
        buttons = self.editor["bx"][p_box]["bn"]
        for btnid, button in buttons.items():
            btn = SS.set_button_style(QPushButton(button["a"]), p_active=False)
            btn.setEnabled(False)
            self.editor["bx"][p_box]["bn"][btnid]["s"] = \
                "inactive"
            self.editor["bx"][p_box]["bn"][btnid]["w"] = \
                btn
            hbox.addWidget(btn)
        return (hbox)

    def make_text_input(self,
                        p_box: str):
        """Create a text input widget defined for a box.

        :args:
            p_text_key: str - name of the text input
        :returns: QLineEdit object
        """
        input_text = self.editor["bx"][p_box]["input"]
        txt_wdg = SS.set_line_edit_style(QLineEdit(), p_active=False)
        txt_wdg.setPlaceholderText(input_text["b"])
        txt_wdg.setToolTip(input_text["c"])
        txt_wdg.setReadOnly(True)
        txt_wdg.setEnabled(False)
        input_text["s"] = "inactive"
        input_text["w"] = txt_wdg
        return (txt_wdg)

    def make_box_group(self,
                       p_box: str):
        """Make box containers. Put config'd buttons, text in them.

        :args:
            p_box: str - name of the button group
        :returns: QVBoxLayout object
        """
        vbox = QVBoxLayout()
        lbl = QLabel(self.editor["bx"][p_box]["a"])
        vbox.addWidget(SS.set_subtitle_style(lbl))
        if "bn" in self.editor["bx"][p_box]:
            vbox.addLayout(self.make_editor_buttons(p_box))
        if "input" in self.editor["bx"][p_box]:
            vbox.addWidget(self.make_text_input(p_box))
        return (vbox)

    def make_status_lbl(self):
        """Create the Editor's status label."""
        status_wdg = SS.set_status_style(
            QLabel(self.editor["status.txt"]["b"]))
        self.editor["status.txt"]["w"] = status_wdg
        return(status_wdg)

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
        self.activate_buttons("get.box", ["find.btn"])
        self.activate_texts("get.box")
        dbe_layout.addLayout(self.make_box_group("edit.box"))
        dbe_layout.addWidget(self.make_status_lbl())
        self.hide()
        self.editor["w"] = self

    # Action slots and helper methods
    # ==============================================================
    def set_dbe_status(self, p_status: str):
        """Set the status text of the DB Editor."""
        self.editor["status.txt"]["w"].setText(p_status)

    def activate_texts(self,
                       p_box: str,
                       p_inputs: list = []):
        """Activate selected set of input text widgets.

        :args:
            p_box: str - name of the box containing text widgets
            p_txts: list - list of text keys to activate. Optional.
             If only only one input in the box, use it.

        @DEV
            Probably tweak the metadata so there is always a list of inputs
        """
        if "input" in self.editor["bx"][p_box]:
            widget = self.editor["bx"][p_box]["input"]["w"]
            widget.setStyleSheet(SS.get_style("active_editor"))
            widget.setEnabled(True)
            widget.setReadOnly(False)
            self.editor["bx"][p_box]["input"]["s"] = "active"
        else:
            for inpid in p_inputs:
                widget = self.editor["bx"][p_box]["input"][inpid]["w"]
                widget.setStyleSheet(SS.get_style("active_editor"))
                widget.setEnabled(True)
                widget.setReadOnly(False)
                self.editor["bx"][p_box]["inputs"][inpid]["s"] = \
                    "active"

    def activate_buttons(self,
                         p_box: str,
                         p_btns: list):
        """Activate selected set of push buttons

        :args:
            p_box: name of box containing buttons
            p_btns: list of button names in box to activate
        """
        for btnid in p_btns:
            btn = self.editor["bx"][p_box]["bn"][btnid]
            btn["w"].setStyleSheet(SS.get_style("active_button"))
            btn["w"].setEnabled(True)
            self.editor["bx"][p_box]["bn"][btnid]["s"] = \
                "active"

    def deactivate_texts(self, p_txts: list):
        """Deactivate specified set of input text widgets."""
        for inp_nm in p_txts:
            inp = self.texts[inp_nm]
            inp["w"].setStyleSheet(SS.get_style("inactive_editor"))
            inp["w"].setEnabled(False)
            inp["active"] = False

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
            btn["w"].setStyleSheet(SS.get_style("inactive_button"))
            btn["w"].setEnabled(False)
            btn["active"] = False

    def push_cancel(self):
        """Slot for Editor Edit Push Button --> Cancel"""
        button = self.editor["bx"]["edit.box"]["bn"]["cancel.btn"]
        self.set_dbe_status(button["c"])
        self.deactivate_rectyp()

    def add_row_to_list(self):
        """Add an input row to form for list of fields.
        """
        list_nm = self.sender().objectName().split(":")[1].split(".")[0]
        list_values, list_form = self.get_list_fields(list_nm)
        rowcnt = len(list_values)
        if rowcnt > 4:
            button = self.editor["bx"]["edit.box"]["bn"]["fewer.btn"]
            self.set_dbe_status(button["c"])
        else:
            button = self.editor["bx"]["edit.box"]["bn"]["more.btn"]
            self.set_dbe_status(button["c"])
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
            button = self.editor["bx"]["edit.box"]["bn"]["fewer.btn"]
            self.set_dbe_status(button["lim"])
        else:
            button = self.editor["bx"]["edit.box"]["bn"]["more.btn"]
            self.set_dbe_status(button["lim"])
            list_form.removeRow(rowcnt - 1)
