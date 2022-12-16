#!/usr/bin/python3.9
"""
:module:    se_menus.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI.
Build the menu widgets.
"""

from pprint import pprint as pp     # noqa: F401

from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QMenuBar
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QWidget

from se_qt_styles import SaskanStyles          # type: ignore

SS = SaskanStyles()


class MenusWidget(QWidget):      # noqa: F821
    """Customized Qt class create menus for main app."""
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.make_menus()

    def make_menus(self):
        """Initialize actions metadata for the toolbox.
           When I try to do this in a sub-class, the main
           menu bar shows up, but not the actual menus.
           Now the same thing happens in the main app.
        """
        mbar = QMenuBar(self)
        mbar.setGeometry(0, 0, 100, 25)
        mbar.setStyleSheet(SS.get_style('menu'))
        # File Menu
        menu_file = mbar.addMenu("File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.exit_main)
        menu_file.addAction(quit_action)
        mbar.addMenu(menu_file)
        # Help Menu
        menu_help = mbar.addMenu("Help")
        about_action = QAction("About Sasan Eyes", self)
        about_action.triggered.connect(self.show_about)
        menu_help.addAction(about_action)
        about_qt_action = QAction("About Qt", self)
        about_qt_action.triggered.connect(self.show_about_qt)
        menu_help.addAction(about_qt_action)
        mbar.addMenu(menu_help)

    # Menu actions and helper methods
    # ==============================================================
    def exit_main(self):
        """Slot for Exit action"""
        self.close()

    def show_about(self):
        """Display a message box."""
        msg = "Control, Monitor, Test and Edit the Saskan Services.\n\n" + \
            "Version: 0.0.1"
        mbox = QMessageBox()
        mbox.about(self, "About Saskan Eyes", msg)

    def show_about_qt(self):
        """Display a message box about Qt."""
        QMessageBox.aboutQt(self, "About Qt")
