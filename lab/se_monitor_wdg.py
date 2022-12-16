#!/usr/bin/python3.9
"""
:module:    se_monitor_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts
"""

from pprint import pprint as pp     # noqa: F401
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

SS = SaskanStyles()
TX = SaskanTexts()


class MonitorWidget(QWidget):
    """Build container for the Service Monitor components.

    Define/enable the service monitor functions widget.
    Define the buttons and actions for filtering or assembling
    log data.
    - Summary, Top, Tail, Full, Requests, Fails, Pressure
    """
    def __init__(self,
                 parent: QWidget,
                 wdg_meta: dict):
        """super() call is required."""
        super().__init__(parent)
        self.monitor = wdg_meta
        self.acts: dict = dict()
        self.make_monitor_widget()

    def get_tools(self):
        """Return modified metadata"""
        return(self.monitor)

    def make_title_lbl(self):
        """Create a status text widget."""
        title = QLabel(self.monitor["a"])
        title.setStyleSheet(SS.get_style('title'))
        return(title)

    def make_display_wdg(self):
        """Create the main monitor display window."""
        mon = QTextEdit()
        mon.setReadOnly(True)
        mon.setStyleSheet(SS.get_style('active_editor'))
        self.monitor["disp.txt"]["w"] = mon
        return(mon)

    def make_mon_buttons(self):
        """Create the buttons associated with Service Monitor."""
        hbox = QHBoxLayout()
        hbox.LeftToRight
        hbox.addStretch()
        hbox.addSpacing(30)
        for btn_id, button in self.monitor["bn"].items():
            btn = SS.set_button_style(QPushButton(button["a"]))
            self.monitor["bn"][btn_id]["s"] = "active"
            self.monitor["bn"][btn_id]["w"] = btn
            hbox.addWidget(btn)
        return(hbox)

    def define_button_actions(self):
        """Set actions associated with Service Monitor buttons."""
        for key, act in {
                "summary.btn": self.mon_summary,
                "top.btn": self.mon_top,
                "tail.btn": self.mon_tail,
                "full.btn": self.mon_full,
                "requests.btn": self.mon_requests,
                "fails.btn": self.mon_fails,
                "pressure.btn": self.mon_pressure}.items():
            self.monitor["bn"][key]["w"].clicked.connect(act)

    def make_status_lbl(self):
        """Create a status label widget."""
        status_wdg = SS.set_status_style(
            QLabel(self.monitor["status.txt"]["b"]))
        self.monitor["status.txt"]["w"] = status_wdg
        return(status_wdg)

    def make_monitor_widget(self):
        """Define components of the Service Monitor widget."""
        # Controls container
        self.setGeometry(20, 330, 600, 300)
        mon_layout = QVBoxLayout()
        self.setLayout(mon_layout)
        mon_layout.addWidget(self.make_title_lbl())
        mon_layout.addWidget(self.make_display_wdg())
        mon_layout.addLayout(self.make_mon_buttons())
        self.define_button_actions()
        mon_layout.addWidget(self.make_status_lbl())
        self.hide()
        self.monitor["w"] = self

    # Service Monitor slot and helper methods
    # ==============================================================
    def set_status_text(self, p_text: str):
        """Set text in the Services Monitor status bar."""
        self.monitor["status.txt"]["w"].setText(p_text)

    def mon_summary(self):
        """Slot for Monitor Summary button click action"""
        btn = self.monitor["bn"]["summary.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_top(self):
        """Slot for Monitor Top button click action"""
        btn = self.monitor["bn"]["top.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_tail(self):
        """Slot for Monitor Tail button click action"""
        btn = self.monitor["bn"]["tail.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_full(self):
        """Slot for Monitor Full button click action"""
        btn = self.monitor["bn"]["full.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_requests(self):
        """Slot for Monitor Requests button click action"""
        btn = self.monitor["bn"]["requests.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_fails(self):
        """Slot for Monitor Fails button click action"""
        btn = self.monitor["bn"]["fails.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])

    def mon_pressure(self):
        """Slot for Monitor Pressure button click action"""
        btn = self.monitor["bn"]["pressure.btn"]
        if btn["s"] == "active":
            self.set_status_text(btn["c"])
