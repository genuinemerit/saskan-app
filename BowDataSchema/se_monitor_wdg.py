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
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.acts: dict = dict()
        self.set_monitor_actions()
        self.make_monitor_widget()

    def set_monitor_actions(self):
        """Define metadata for Service Monitor actions.
        """
        acts_template = {
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        acts = {"Summary":
                {"title": "Services Summary",
                 "caption": "Show summary info for running " +
                            "and registered services"},
                "Top":
                {"title": "Show top of Services log",
                 "caption": "Display oldest entries in the services log"},
                "Tail":
                {"title": "Show tail of Services log",
                 "caption": "Display newest entries in the services log"},
                "Full":
                {"title": "Show full Services log",
                 "caption": "Display all entries in the services log"},
                "Requests":
                {"title": "Show active Requests",
                 "caption": "Display requests currently in the queue" +
                            " or in progress"},
                "Fails":
                {"title": "Show failed Requests",
                 "caption": "Display requests which failed or were refused"},
                "Pressure":
                {"title": "Show Services Pressure",
                 "caption": "Display current load on each service"}}
        for key in acts.keys():
            self.acts[key] = acts_template.copy()
            for this, do_it in acts[key].items():
                self.acts[key][this] = do_it

    def make_monitor_widget(self):
        """Define components of the Service Monitor widget."""
        # Controls container
        self.setGeometry(20, 330, 600, 300)
        mon_layout = QVBoxLayout()
        self.setLayout(mon_layout)
        # Title
        # Ideally, this would be set based on modes metadata "Title"
        title = QLabel("Service Monitor")
        title.setStyleSheet(SS.get_style('title'))
        mon_layout.addWidget(title)
        # Display area
        self.mon_display = QTextEdit()
        self.mon_display.setReadOnly(True)
        self.mon_display.setStyleSheet(SS.get_style('active_editor'))
        mon_layout.addWidget(self.mon_display)
        # Service Control buttons
        mon_btn_hbox = QHBoxLayout()
        for btn_id in self.acts.keys():
            btn = SS.set_button_style(QPushButton(btn_id))
            self.acts[btn_id]["widget"] = btn
            mon_btn_hbox.addWidget(btn)
        mon_layout.addLayout(mon_btn_hbox)
