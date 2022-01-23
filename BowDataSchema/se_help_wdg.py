#!/usr/bin/python3.9
"""
:module:    se_help_wdg.py

:author:    GM (genuinemerit @ pm.me)

@DEV
- Eventually move all text strings to SaskanTexts
"""

from os import path
from pprint import pprint as pp     # noqa: F401
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from BowQuiver.saskan_fileio import FileIO      # type: ignore
from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.saskan_utils import Utils        # type: ignore
from se_qt_styles import SaskanStyles           # type: ignore

FI = FileIO()
SS = SaskanStyles()
TX = SaskanTexts()
UT = Utils()


class HelpWidget(QWidget):
    """Build container for the Help components.

    Define/enable the help functions widget.
    For now, it has no actions or slots, just the display.
    """
    def __init__(self, parent: QWidget):
        """super() call is required."""
        super().__init__(parent)
        self.APP = path.join(UT.get_home(), 'saskan')
        self.RES = path.join(self.APP, 'res')
        self.make_help_widget()

    def set_content(self, p_html_file_nm: str):
        """Refresh the help page contents.

        Content in help-display are URL-loaded HTML files.
        - Published to home/saskan/res
        - Edited, versioned in git repo under app's /html sub-dir

        :Args:
            - p_html_file_nm: str -> name only of html file to display
        """
        html_path = path.join(self.RES, p_html_file_nm)
        ok, msg, _ = FI.get_file(html_path)
        if ok:
            self.help.setUrl(f"file://{html_path}")

    def make_help_widget(self):
        """Define components of the Help widget.
        """
        # Controls container
        self.setGeometry(20, 630, 600, 200)
        help_layout = QVBoxLayout()
        self.setLayout(help_layout)
        # Title
        # Ideally, this would be set based on modes metadata "Title"
        title = QLabel("Help")
        title.setStyleSheet(SS.get_style('title'))
        help_layout.addWidget(title)
        # Display area
        self.help = QWebEngineView()
        help_layout.addWidget(self.help)
