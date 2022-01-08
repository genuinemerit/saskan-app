"""
:module:    saskan_styles.py

:author:    GM (genuinemerit @ pm.me)

BoW Saskan QCC style sheets for Qt.
"""


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
             "border-width: 1px 3px 3px 1px; " + \
             "border-style: solid; " + \
             "border-color: gray;" + \
             "color: black;" + \
             "border-radius: 5px;" + \
             "margin: 5px;" + \
             "padding: 5px;"
        return ss

    @classmethod
    def _button_inactive_style(cls):
        """Set style for deactivated buttons"""
        ss = "background-color: white; " + \
             "border-width: 1px 1px 1px 1px; " + \
             "border-style: solid; " + \
             "border-color: lavender;" + \
             "color: lavender;" + \
             "border-radius: 5px;" + \
             "margin: 5px;" + \
             "padding: 5px;"
        return ss

    @classmethod
    def _canvas_style(cls):
        """Set OpenGL canvas style."""
        ss = "border: 1px solid; " + \
             "border-color: whhite; "
        return ss

    @classmethod
    def _checkbox_active_style(cls):
        """Set style for active checkbox."""
        ss = "background-color: white; " + \
             "border: 2px solid; " + \
             "border-color: darkgreen; " + \
             "color: black;" + \
             "padding: 5px;"
        return ss

    @classmethod
    def _checkbox_inactive_style(cls):
        """Set style for active checkbox."""
        ss = "background-color: gray; " + \
             "border: 2px solid; " + \
             "border-color: black; " + \
             "color: gray;" + \
             "padding: 5px;"
        return ss

    @classmethod
    def _editor_active_style(cls):
        """Set style for active editors."""
        ss = "background-color: white; " + \
             "border: 2px solid; " + \
             "border-color: darkgreen; " + \
             "color: black;"
        return ss

    @classmethod
    def _editor_inactive_style(cls):
        """Set style for deactivated editors."""
        ss = "background-color: gray; " + \
             "border: 1px solid; " + \
             "border-color: black; " + \
             "color: gray;"
        return ss

    @classmethod
    def _menu_style(cls):
        """Set style for menus."""
        ss = "background-color: black; " + \
             "border: 1px solid; " + \
             "border-color: white; " + \
             "color: white;"
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
    def _tool_active_style(cls):
        """Set style for activated toolbar buttons"""
        ss = "background-color: white; " + \
             "border-width: 1px 1px 1px 1px; " + \
             "border-style: solid; " + \
             "border-color: black;" + \
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
        elif p_widget in ('editor', 'active_editor', 'help'):
            ss = self._editor_active_style()
        elif p_widget in ('inactive_editor'):
            ss = self._editor_inactive_style()
        elif p_widget in ('button', 'active_button'):
            ss = self._button_active_style()
        elif p_widget in ('inactive_button'):
            ss = self._button_inactive_style()
        elif p_widget in ('canvas'):
            ss = self._canvas_style()
        elif p_widget in ('menu'):
            ss = self._menu_style()
        elif p_widget in ('status'):
            ss = self._status_style()
        elif p_widget in ('tool', 'active_tool'):
            ss = self._tool_active_style()
        elif p_widget in ('inactive_tool'):
            ss = self._tool_inactive_style()
        else:
            ss = self._base_style()
        return ss
