#!/usr/bin/python3.9
"""
:module:    se_controls_wdg.py

:author:    GM (genuinemerit @ pm.me)
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_controls_shell import ControlsShell     # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

CS = ControlsShell()
SS = SaskanStyles()
TX = SaskanTexts()


class ControlsWidget(QWidget):
    """Build container for the Service Controller components.

    Define a generic widget, then have the layouts inside of that.
    Give a geometry of the widget relative to the MainWindow.
    Use hide() and show(), not move().

    Define/enable the service control functions widget.
    Include functions for running pre-defined test suites.
    Define the buttons and actions for:
    - Control: Start, Stop, Show, Test
    """
    def __init__(self,
                 parent: QWidget,
                 wdg_meta: dict):
        """super() call is required."""
        super().__init__(parent)
        self.controls = wdg_meta
        self.make_controls_widget()

    def get_tools(self):
        """Return modified metadata"""
        return(self.controls)

    def make_title_lbl(self):
        """Create a status text widget."""
        title = QLabel(self.controls["a"])
        title.setStyleSheet(SS.get_style('title'))
        return(title)

    def make_display_wdg(self):
        """Create the main controls display window."""
        controller = QTextEdit()
        controller.setReadOnly(True)
        controller.setStyleSheet(SS.get_style('active_editor'))
        self.controls["disp.txt"]["w"] = controller
        return(controller)

    def make_controls_buttons(self):
        """Create the buttons associated with the Service Controller."""
        hbox = QHBoxLayout()
        hbox.LeftToRight
        hbox.addStretch()
        hbox.addSpacing(30)
        for btn_id, button in self.controls["bn"].items():
            btn = SS.set_button_style(QPushButton(button["a"]))
            self.controls["bn"][btn_id]["w"] = btn
            hbox.addWidget(btn)
        return(hbox)

    def define_button_actions(self):
        """Set actions for Service Controller buttons."""
        for key, act in {
                "start.btn": self.start_services,
                "stop.btn": self.stop_services,
                "show.btn": self.show_services,
                "test.btn": self.test_services}.items():
            self.controls["bn"][key]["w"].clicked.connect(act)

    def make_status_lbl(self):
        """Create a status label widget."""
        status_wdg = SS.set_status_style(
            QLabel(self.controls["status.txt"]["b"]))
        self.controls["status.txt"]["w"] = status_wdg
        return(status_wdg)

    def make_controls_widget(self):
        """Define components of the Service Controller widget."""
        self.setGeometry(20, 40, 600, 300)
        ctl_layout = QVBoxLayout()
        self.setLayout(ctl_layout)
        ctl_layout.addWidget(self.make_title_lbl())
        ctl_layout.addWidget(self.make_display_wdg())
        ctl_layout.addLayout(self.make_controls_buttons())
        self.define_button_actions()
        ctl_layout.addWidget(self.make_status_lbl())
        self.hide()
        self.controls["w"] = self

    # Service Controls slot and helper methods
    # ==============================================================
    def set_status_text(self, p_text: str):
        """Set text in the Services Controller status bar."""
        self.controls["status.txt"]["w"].setText(p_text)

    def start_services(self):
        """Slot for Start Services action"""
        btn = self.controls["bn"]["start.btn"]
        self.set_status_text(btn["c"])
        status, msg = CS.start_services(p_service_nm='redis')
        self.controls["disp.txt"]["w"].setText(msg)

    def stop_services(self):
        """Slot for Stop Services action"""
        btn = self.controls["bn"]["stop.btn"]
        self.set_status_text(btn["c"])
        status, msg = CS.stop_running_services(p_service_nm='redis')
        self.controls["disp.txt"]["w"].setText(msg)

    def show_services(self):
        """Slot for Show Services action"""
        btn = self.controls["bn"]["show.btn"]
        self.set_status_text(btn["c"])
        status, msg = CS.check_running_services(p_service_nm='redis')
        self.controls["disp.txt"]["w"].setText(msg)

    def test_services(self):
        """Slot for Test Services action"""
        btn = self.controls["bn"]["test.btn"]
        self.set_status_text(btn["c"])
        self.controls["disp.txt"]["w"].setText("")
