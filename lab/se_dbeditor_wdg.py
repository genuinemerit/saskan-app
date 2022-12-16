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
from wire_tap import WireTap                    # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()
WT = WireTap()


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
        WT.log_module(__file__, __name__, self)
        super().__init__(parent)
        self.editor = wdg_meta
        self.make_db_editor_wdg()

    def get_tools(self):
        """Return modified metadata"""
        WT.log_function(self.get_tools, self)
        return(self.editor)

    # Database Editor Widget make functions
    # ============================================================
    def make_title_lbl(self):
        """Create a status text widget."""
        WT.log_function(self.make_title_lbl, self)
        title = QLabel(self.editor["a"])
        title.setStyleSheet(SS.get_style('title'))
        return(title)

    def make_editor_buttons(self,
                            p_box: str):
        """Create the buttons defined by the metadata.

        :args:
            p_box: str - key to Box meta w/ button defs
        """
        WT.log_function(self.make_editor_buttons, self)
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

    def make_text_inputs(self,
                         p_box: str):
        """Create text input widgets defined for a box.
        :args:
            p_box: str - key to text input container
        :returns: QLineEdit object"""
        WT.log_function(self.make_text_inputs, self)
        vbox = QVBoxLayout()
        inputs = self.editor["bx"][p_box]["inp"]
        for inpk, inp in inputs.items():
            inp_wdg = SS.set_line_edit_style(QLineEdit(), p_active=False)
            inp_wdg.setPlaceholderText(inp["b"])
            inp_wdg.setToolTip(inp["c"])
            inp_wdg.setReadOnly(True)
            inp_wdg.setEnabled(False)
            self.editor["bx"][p_box]["inp"][inpk]["s"] = "inactive"
            self.editor["bx"][p_box]["inp"][inpk]["w"] = inp_wdg
            vbox.addWidget(inp_wdg)
        return (vbox)

    def make_box_group(self,
                       p_box: str):
        """Make box containers. Put config'd buttons, text in them.
        :args:
            p_box: str - name of the button group
        :returns: QVBoxLayout object"""
        WT.log_function(self.make_box_group, self)
        vbox = QVBoxLayout()
        lbl = QLabel(self.editor["bx"][p_box]["a"])
        vbox.addWidget(SS.set_subtitle_style(lbl))
        if "bn" in self.editor["bx"][p_box]:
            vbox.addLayout(self.make_editor_buttons(p_box))
        if "inp" in self.editor["bx"][p_box]:
            vbox.addLayout(self.make_text_inputs(p_box))
        return (vbox)

    def make_status_lbl(self):
        """Create the Editor's status label."""
        WT.log_function(self.make_status_lbl, self)
        status_wdg = SS.set_status_style(
            QLabel(self.editor["status.txt"]["b"]))
        self.editor["status.txt"]["w"] = status_wdg
        return(status_wdg)

    def set_button_actions(self):
        """Assign actions to button slots.
        Other button actions are assigned in RecordMgmt class."""
        WT.log_function(self.set_button_actions, self)
        # Cancel / Stop Button
        self.editor["bx"]["edit.box"]["bn"]["cancel.btn"]["w"].clicked.connect(
            self.push_cancel)

    def make_db_editor_wdg(self):
        """Create all components of Data Base Editor widget.
        The dbe layout object is exposed so that it can be
        extended by the RecordsMgmt class."""
        WT.log_function(self.set_button_actions, self)
        self.setGeometry(620, 40, 550, 840)
        self.dbe = QVBoxLayout()
        self.dbe.setAlignment(Qt.AlignTop)
        self.setLayout(self.dbe)
        self.dbe.addWidget(self.make_title_lbl())
        self.dbe.addLayout(self.make_box_group("get.box"))
        self.dbe.addLayout(self.make_box_group("edit.box"))
        self.set_button_actions()
        self.dbe.addWidget(self.make_status_lbl())
        self.hide()
        self.editor["w"] = self

    # Action slots and helper methods
    # ==============================================================
    def set_dbe_status(self, p_status: str):
        """Set the status text of the DB Editor."""
        WT.log_function(self.set_dbe_status, self)
        self.editor["status.txt"]["w"].setText(p_status)

    def enable_texts(self,
                     p_box: str,
                     p_inputs: list = []):
        """Activate selected set of input text widgets.
        :args:
            p_box: str - name of the box containing text widgets
            p_inputs: list - list of text keys to activate."""
        WT.log_function(self.enable_texts, self)
        inputs = self.editor["bx"][p_box]["inp"]
        for inpk in p_inputs:
            widget = inputs[inpk]["w"]
            widget.setStyleSheet(SS.get_style("active_editor"))
            widget.setEnabled(True)
            widget.setReadOnly(False)
            self.editor["bx"][p_box]["inp"][inpk]["s"] = "active"

    def enable_buttons(self,
                       p_box: str,
                       p_btns: list):
        """Activate selected set of push buttons.
        :args:
            p_box: name of box containing buttons
            p_btns: list of button names in box to activate """
        WT.log_function(self.enable_buttons, self)
        for btnid in p_btns:
            btn = self.editor["bx"][p_box]["bn"][btnid]
            btn["w"].setStyleSheet(SS.get_style("active_button"))
            btn["w"].setEnabled(True)
            self.editor["bx"][p_box]["bn"][btnid]["s"] = "active"

    def disable_buttons(self,
                        p_box: str,
                        p_btns: list):
        """Deactivate a specified set of push buttons.
        :args:
            p_box: str - name of the box containing text widgets
            p_inputs: list - list of text keys to activate."""
        WT.log_function(self.disable_buttons, self)
        for btnid in p_btns:
            btn = self.editor["bx"][p_box]["bn"][btnid]
            btn["w"].setStyleSheet(SS.get_style("inactive_button"))
            btn["w"].setEnabled(False)
            self.editor["bx"][p_box]["bn"][btnid]["s"] = "inactive"

    def disable_texts(self,
                      p_box: str,
                      p_inputs: list = []):
        """Deactivate specified set of input text widgets.
        :args:
            p_box: str - name of the box containing text widgets
            p_inputs: list - list of text keys to activate."""
        WT.log_function(self.disable_texts, self)
        inputs = self.editor["bx"][p_box]["inp"]
        for inpk in p_inputs:
            widget = inputs[inpk]["w"]
            widget.setStyleSheet(SS.get_style("inactive_editor"))
            widget.setEnabled(False)
            widget.setReadOnly(True)
            self.editor["bx"][p_box]["inp"][inpk]["s"] = "inactive"

    def push_cancel(self):
        """Slot for Editor Edit Push Button --> Cancel"""
        WT.log_function(self.push_cancel, self)
        button = self.editor["bx"]["edit.box"]["bn"]["cancel.btn"]
        self.set_dbe_status(button["c"])
        # Add logic here to clear queues and reset widgets
        self.hide()
