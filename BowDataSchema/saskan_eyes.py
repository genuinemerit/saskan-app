#!python
"""
:module:    saskan_eyes.py
:author:    GM (genuinemerit @ pm.me)
BoW Saskan App Admin GUI.  wx version."""

import platform
import wx

from pprint import pprint as pp     # noqa: F401

from io_boot import BootIO          # type: ignore
from io_file import FileIO          # type: ignore
from io_redis import RedisIO        # type: ignore
from io_wiretap import WireTap      # type: ignore
from saskan_meta import SaskanMeta  # type: ignore

BI = BootIO()
FI = FileIO()
RI = RedisIO()
WT = WireTap()
SM = SaskanMeta()


class SaskanEyes(wx.Frame):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    Args:
        (object): wx Frame object

    @DEV:
    - Provide menu item to modify the log/mon config files.
    - Provide menu item to refresh the redis metadata from JSON file.
    - This class just focuses on GUI-related code translated from Qt to wx.
    - Then go thru systematically, using both previous Qt code and design
      documents as guides, and translate to wx.  Add functionality as noted
      above.
    - Use menus instead of big buttons. Add toolbar buttons later if desired.
    """
    def __init__(self, *args, **kwargs):
        """wx refers to the base GUI object as the frame.
        We inherited frame's init values from __main__ so don't need to make
        an explicit call to it here other than in the super().
        The parent window size is set in the Frame constructor.
        """
        WT.log_module(__file__, __name__, self)
        super(SaskanEyes, self).__init__(*args, **kwargs)
        self.WDG = SM.load_meta()
        self.initialize_gui()

    # GUI / Main App handlers
    # ==============================================================
    def initialize_gui(self):
        """Define panels, boxes, widgets, menus.
        Show the frame.
        """
        pnl = wx.Panel(self)
        py_version = "Python: " + platform.python_version()
        wx_version = "wxPython: " + wx.version()
        os_version = "OS: " + platform.platform()
        st = wx.StaticText(pnl, label=BI.txt.desc_saskan_eyes)
        font = st.GetFont()
        font.PointSize += 10
        font.Weight = wx.FONTWEIGHT_BOLD
        # or.. font = font.Bold()
        st.SetFont(font)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, wx.SizerFlags().Center().Border(wx.TOP | wx.LEFT, 25))
        sizer.Add(wx.StaticText(pnl, label=py_version), 0, wx.ALL, 5)
        sizer.Add(wx.StaticText(pnl, label=wx_version), 0, wx.ALL, 5)
        sizer.Add(wx.StaticText(pnl, label=os_version), 0, wx.ALL, 5)
        pnl.SetSizer(sizer)

        self.make_menu_bar()

        # self.CreateSatatusBar()
        # self.SetStatusText(BI.txt.desc_saskan_eyes)

        self.Show()

    def make_menu_bar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        file_menu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        hello_item = file_menu.Append(-1, "&Hello...\tCtrl-H",
                                      "Help string shown in status bar " +
                                      "for this menu item")
        file_menu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exit_item = file_menu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menu_bar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.on_hello, hello_item)
        self.Bind(wx.EVT_MENU, self.on_exit,  exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        """Close the frame, terminating the application.
        The frame is the higest-level object.
        Objects contained in it also get closed.
        """
        self.Close(True)

    def on_hello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def on_about(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)


# Run program
if __name__ == '__main__':
    """Run program."""
    app = wx.App()
    SE = SaskanEyes(None, title="Saskan Eyes", size=(800, 600))
    app.MainLoop()
