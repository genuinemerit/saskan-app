#!/usr/bin/python3.9
"""
:module:    se_modes_tbx.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (Qt prototype)
Experiment with distinct class modules for major GUI components.
"""

from os import path
from pprint import pprint as pp     # noqa: F401

from PySide2.QtCore import QRect
# from PySide2.QtCore import Qt
from PySide2.QtCore import QSize
# from PySide2.QtGui import QFont
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QToolButton

from boot_texts import BootTexts                # type: ignore
from se_qt_styles import SaskanStyles          # type: ignore

BT = BootTexts()
SS = SaskanStyles()


class ModesToolbox(QToolBar):      # noqa: F821
    """Customized Qt Toolbox class to change app states:
        "Control", "Monitor", "DB Edit", "Help"
    Create as a widget then add to a layout.
    """
    def __init__(self, parent: QToolBar, wdg_meta: dict):
        """super() call is required."""
        super().__init__(parent)
        self.tools = wdg_meta
        self.set_geometry()
        self.make_tools()

    def get_tools(self):
        """Return modified metadata"""
        return(self.tools)

    def set_geometry(self):
        """Size the toolbox based on size of largest icon.
        """
        self.setMovable(False)
        self.setStyleSheet(SS.get_style('inactive_tool'))
        icon_cnt = len(self.tools.keys())
        # The sizing of the toolbox is icon size adjusted
        # for estimated text size. Still seems a little wonky
        # but close enough.
        self.setGeometry(QRect(0, 0,
                               (16 * 3 * (icon_cnt + 1)),
                               (16 * 3)))

    def make_tools(self):
        """Construct the toolbox QAction widgets.
           None of the "action" attributes defined here are the
           slot actions.  They get defined later.
        """
        for tk, tool in self.tools.items():
            icon = QIcon(path.join(BT.path_res, tool['i']))
            self.tools[tk]["widget"] = QAction(icon, tool['a'], self)
            self.tools[tk]["widget"].setObjectName(tk)
            self.tools[tk]["widget"].setToolTip(tool['c'])
            self.tools[tk]["widget"].setShortcut(tool['cmd'])
            self.tools[tk]["state"] = "active"
            tool_btn = SS.set_tool_style(QToolButton(self))
            tool_btn.setDefaultAction(self.tools[tk]["widget"])
            self.addWidget(tool_btn)
