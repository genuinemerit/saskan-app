#!/usr/bin/python3.9
"""
:module:    modes_toolbox.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (Qt prototype)
Experiment with distinct class modules for major GUI components.
"""

from pprint import pprint as pp     # noqa: F401

from PySide2.QtCore import QRect
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QToolButton

from saskan_styles import SaskanStyles          # type: ignore

SS = SaskanStyles()


class ModesToolbox(QToolBar):      # noqa: F821
    """Customized Qt Toolbox class to change app states:
        "Control", "Monitor", "DB Edit"
    The three states are mutually exclusive.
    Inherit QToolBar. Add styles and actions.
    Create as a widget then add to a layout.
    """
    def __init__(self, parent: QToolBar):
        """super() call is required."""
        super().__init__(parent)
        self.d_icon = QIcon('images/favicon.jpg')
        d_icon_sz = self.d_icon.availableSizes(mode=QIcon.Normal)[0]
        self.setIconSize(d_icon_sz)
        # self.setMovable(False)
        self.setMovable(True)
        self.setGeometry(QRect(0, 0,
                         int(d_icon_sz.width() * (4 * 3)),
                         int(d_icon_sz.height() * 3)))
        self.setStyleSheet(SS.get_style('inactive_tool'))
        self.acts: dict = dict()
        self.set_actions()
        self.make_actions()
        self.make_buttons()

    def set_actions(self):
        """Initialize actions metadata for the toolbox."""
        acts_template = {
            "title": str(),
            "caption": str(),
            "keycmd": str(),
            "active": True,
            "widget": object}
        acts = {"Control":
                {"title": "Services Controller",
                    "caption": "Start, stop, manage services",
                    "keycmd": "Ctrl+Alt+C"},
                "Monitor":
                {"title": "Services Monitor",
                    "caption": "Monitor running servers and services",
                    "keycmd": "Ctrl+Alt+M"},
                "Edit DB":
                {"title": "Service Databases Editor",
                    "caption": "Edit the services databases",
                    "keycmd": "Ctrl+Alt+D"}}
        for key in acts.keys():
            self.acts[key] = acts_template.copy()
            for this, do_it in acts[key].items():
                self.acts[key][this] = do_it

    def make_actions(self):
        """Construct the toolbox QAction widgets.
            Assign actions to widget slots in parent class.

            @DEV:
            - Design unique icons for each tool
        """
        for key in self.acts.keys():
            self.acts[key]["widget"] = \
                QAction(self.d_icon, key, self)
            self.acts[key]["widget"].setToolTip(
                self.acts[key]["caption"])
            self.acts[key]["widget"].setShortcut(
                self.acts[key]["keycmd"])

    def make_buttons(self):
        """Construct the toolbox QToolButton widgets."""
        for key in self.acts.keys():
            btn = QToolButton(self)
            btn.setFont(QFont('Arial', 9))
            if self.acts[key]["active"]:
                btn.setStyleSheet(SS.get_style('active_tool'))
            else:
                btn.setStyleSheet(SS.get_style('inactive_tool'))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            # OK to do this. The actual action can still be assigned later.
            btn.setDefaultAction(self.acts[key]["widget"])
            self.addWidget(btn)
