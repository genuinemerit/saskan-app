#!/usr/bin/python3.9
"""
:module:    se_controls_wdg.py

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


class ControlsWidget(QWidget):
    """Build container for the Service Controller components.

    For layouts, the trick seems to be to define a generic widget,
    then have the layouts inside of that.
    Give a geometry of the widget relative to the MainWindow.
    Use hide() and show() for the widget, not move().

    Define/enable the service control functions widget.
    Include functions for running pre-defined test suites.
    Define the buttons and actions for:
    - Control: Start, Stop, Show, Test
    """
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.acts: dict = dict()
        self.set_control_actions()
        self.make_controls_widget()

    def set_control_actions(self):
        """Define metadata for Service Controller actions."""
        acts_template = {
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        acts = {"Start":
                {"title": "Start Services",
                 "caption": "Start up (Run) Saskan services"},
                "Stop":
                {"title": "Stop Services",
                 "caption": "Kill all running Saskan services"},
                "Show":
                {"title": "Show Services Status",
                 "caption": "Show current status of Saskan services"},
                "Test":
                {"title": "Test Services",
                 "caption": "Run preset test suites on Saskan services"}}
        for key in acts.keys():
            self.acts[key] = acts_template.copy()
            for this, do_it in acts[key].items():
                self.acts[key][this] = do_it

    def make_controls_widget(self):
        """Define components of the Service Controller widget."""
        # Controls container
        self.setGeometry(20, 40, 600, 300)
        ctl_layout = QVBoxLayout()
        self.setLayout(ctl_layout)
        # Title
        # Ideally, this would be set based on modes metadata "Title"
        title = QLabel("Service Controls")
        title.setStyleSheet(SS.get_style('title'))
        ctl_layout.addWidget(title)
        # Display area
        self.ctl_display = QTextEdit()
        self.ctl_display.setReadOnly(True)
        self.ctl_display.setStyleSheet(SS.get_style('active_editor'))
        ctl_layout.addWidget(self.ctl_display)
        # Service Control buttons
        ctl_btn_hbox = QHBoxLayout()
        for btn_id in self.acts.keys():
            btn = SS.set_button_style(QPushButton(btn_id))
            self.acts[btn_id]["widget"] = btn
            ctl_btn_hbox.addWidget(btn)
        ctl_layout.addLayout(ctl_btn_hbox)
