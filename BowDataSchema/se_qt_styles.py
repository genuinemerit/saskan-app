"""
:module:    se_qt_styles.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan QCC style sheets for Qt.
"""

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QRadioButton


class SaskanStyles(object):
    """Define style sheets for QT app"""

    def __init__(self):
        """Define stylesheets for the app."""
        pass

    @classmethod
    def _base_style(cls):
        """Set default style."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: white;"
        return ss

    @classmethod
    def _button_active_style(cls):
        """Set style for activated buttons"""
        ss = "background-color: white; " + \
             "border-width: 0px 2px 2px 0px; " + \
             "border-style: solid; " + \
             "border-color: darkgreen;" + \
             "color: black;" + \
             "border-radius: 5px;" + \
             "margin: 2px;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _button_press_style(cls):
        """Set style for pressed buttons"""
        ss = "background-color: white; " + \
             "border-width: 2px 0px 0px 2px; " + \
             "border-style: solid; " + \
             "border-color: green;" + \
             "color: black;" + \
             "border-radius: 5px;" + \
             "margin: 2px;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _button_inactive_style(cls):
        """Set style for deactivated buttons"""
        ss = "background-color: white; " + \
             "border-width: 0px 0px 0px 0px; " + \
             "color: lavender;" + \
             "border-radius: 5px;" + \
             "margin: 2px;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _canvas_style(cls):
        """Set canvas style."""
        ss = "border: 1px solid; " + \
             "border-color: white; "
        return ss

    @classmethod
    def _checkbox_active_style(cls):
        """Set style for active checkbox."""
        ss = "background-color: white; " + \
             "border: 1px solid; " + \
             "border-color: darkgreen; " + \
             "color: black;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _checkbox_inactive_style(cls):
        """Set style for active checkbox."""
        ss = "background-color: gray; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _editor_active_style(cls):
        """Set style for active editors."""
        ss = "background-color: white; " + \
             "border: 1px solid; " + \
             "border-color: darkgreen; " + \
             "color: black;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _editor_inactive_style(cls):
        """Set style for deactivated editors."""
        ss = "background-color: gray; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _info_style(cls):
        """Set style for an informational text."""
        ss = "background-color: black; " + \
             "border: 5px solid; " + \
             "border-color: blue; " + \
             "color: white;"
        return ss

    @classmethod
    def _menu_style(cls):
        """Set style for menus."""
        ss = "background-color: white; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: black;"
        return ss

    @classmethod
    def _radiobtn_active_style(cls):
        """Set style for active radio button."""
        ss = "background-color: white; " + \
             "border: 1px solid; " + \
             "border-color: darkgreen; " + \
             "color: black;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _radiobtn_inactive_style(cls):
        """Set style for inactive radio button."""
        ss = "background-color: gray; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _status_style(cls):
        """Set default style."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;"
        return ss

    @classmethod
    def _subtitle_style(cls):
        """Set style for smaller / sub-title text."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: cyan;"
        return ss

    @classmethod
    def _title_style(cls):
        """Set style for title text."""
        ss = "background-color: black; " + \
             "border: 5px solid; " + \
             "border-color: black; " + \
             "color: cyan;"
        return ss

    @classmethod
    def _tool_active_style(cls):
        """Set style for activated toolbar buttons"""
        ss = "background-color: white; " + \
             "border-width: 1px 1px 1px 1px; " + \
             "border-style: solid; " + \
             "border-color: darkgreen;" + \
             "color: black;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def _tool_inactive_style(cls):
        """Set style for deactivated toolbar buttons"""
        ss = "background-color: white; " + \
             "border-width: 1px 1px 1px 1px; " + \
             "border-style: solid; " + \
             "border-color: lavender;" + \
             "color: lavender;" + \
             "padding: 2px;"
        return ss

    @classmethod
    def get_style(self,
                  p_widget: str = 'base'):
        """Set the style of a widget.

        :Args:
            p_widget: str
        """
        if p_widget in ('base'):
            ss = self._base_style()
        elif p_widget in ('checkbox', 'active_checkbox'):
            ss = self._checkbox_active_style()
        elif p_widget in ('inactive_checkbox'):
            ss = self._checkbox_inactive_style()
        elif p_widget in ('help', 'info'):
            ss = self._info_style()
        elif p_widget in ('editor', 'active_editor'):
            ss = self._editor_active_style()
        elif p_widget in ('inactive_editor'):
            ss = self._editor_inactive_style()
        elif p_widget in ('button', 'active_button'):
            ss = self._button_active_style()
        elif p_widget in ('inactive_button'):
            ss = self._button_inactive_style()
        elif p_widget in ('press_button'):
            ss = self._button_press_style()
        elif p_widget in ('canvas'):
            ss = self._canvas_style()
        elif p_widget in ('menu'):
            ss = self._menu_style()
        elif p_widget in ('radiobtn', 'active_radiobtn'):
            ss = self._radiobtn_active_style()
        elif p_widget in ('inactive_radiobtn'):
            ss = self._radiobtn_inactive_style()
        elif p_widget in ('status'):
            ss = self._status_style()
        elif p_widget in ('subtitle'):
            ss = self._subtitle_style()
        elif p_widget in ('title'):
            ss = self._title_style()
        elif p_widget in ('tool', 'active_tool'):
            ss = self._tool_active_style()
        elif p_widget in ('inactive_tool'):
            ss = self._tool_inactive_style()
        else:
            ss = self._base_style()
        return ss

    def set_button_style(self,
                         btn: QPushButton,
                         active: bool = True):      # type: ignore
        """Set push button style font size and style.

        :Args:
            btn: a QT push button object
            active: bool, optional. If False, make it inactive.
        :Returns:
            btn: the modified object
        """
        if active:
            btn.setStyleSheet(SaskanStyles.get_style('button'))
        else:
            btn.setStyleSheet(SaskanStyles.get_style('inactive_button'))
        btn.setFont(QFont('Arial', 11))
        return btn

    def set_line_edit_style(self,
                            edt: QLineEdit,
                            active: bool = True):      # type: ignore
        """Set line editor style font size and style.

        :Args:
            edt: a QT line editor object
            active: bool, optional. If False, make it inactive.
        :Returns:
            edt: the modified object
        """
        if active:
            edt.setStyleSheet(SaskanStyles.get_style('editor'))
        else:
            edt.setStyleSheet(SaskanStyles.get_style('inactive_editor'))
        edt.setFont(QFont('Arial', 9))
        return edt

    def set_radiobtn_style(self,
                           rdo: QRadioButton,
                           active: bool = True):      # type: ignore
        """Set radio button style font size and style.

        :Args:
            rdo: a QT radio button object
            active: bool, optional. If False, make it inactive.
        :Returns:
            rdo: the modified object
        """
        if active:
            rdo.setStyleSheet(SaskanStyles.get_style('radiobtn'))
        else:
            rdo.setStyleSheet(SaskanStyles.get_style('inactive_radiobtn'))
        rdo.setFont(QFont('Arial', 9))
        return rdo

    def set_subtitle_style(self, lbl: QLabel):      # type: ignore
        """Set subtitle style font size and style.

        :Args:
            lbl: a QT Label object
        :Returns:
            lbl: the modified object
        """
        lbl.setStyleSheet(SaskanStyles.get_style('subtitle'))
        lbl.setFont(QFont('Arial', 11))
        return lbl