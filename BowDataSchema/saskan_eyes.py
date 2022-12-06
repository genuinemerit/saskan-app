#!python
"""
:module:    saskan_eyes.py
:author:    GM (genuinemerit @ pm.me)
BoW Saskan App Admin GUI.  wx version."""

import platform
import pygame

from pprint import pprint as pp     # noqa: F401

from sandbox.io_config import ConfigIO      # type: ignore
from BowDataSchema.io_file import FileIO          # type: ignore
from sandbox.xxx_io_db_redis import RedisIO     # type: ignore
from BowDataSchema.io_meta import MetaIO          # type: ignore
from BowDataSchema.io_wiretap import WireTap      # type: ignore

CI = ConfigIO()
FI = FileIO()
SM = MetaIO()
RI = RedisIO()
WT = WireTap()


class SaskanEyes(wx.Frame):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    Args:
        (object): wx Frame object

    @DEV:
    - Provide menu item to modify the log/mon config files.
    - Provide menu item to refresh the redis metadata from JSON file.
    - This class just focuses on GUI-related code translated from Qt to wx.
    - Go thru systematically, using both previous Qt code and design
      documents as guides, and translate to wx.
    - Use menus instead of big buttons. Add toolbar buttons later if desired.
    - It is doable to define menus first, but might want to wait until all
      panels have been defined so that menu events can be associated with 'em.
    """
    def __init__(self, *args, **kwargs):
        """The base GUI object in wx is the frame.

        The syntax for setting frame attributes is to use another __init__
        on the inherited frame object. Default style is resizabe, with
        min, max and close buttons.
        """
        WT.log_module(__file__, __name__, self)
        self.M = SM.load_meta()
        # Set Frame
        super(SaskanEyes, self).__init__(
            None,
            title=self.M["frame"]["a"],
            size=wx.Size(self.M["frame"]["s"]["w_px"],
                         self.M["frame"]["s"]["h_px"]),
            name=self.M["frame"]["n"])
        self.set_windows()
        self.set_menus()
        self.Show()

    # GUI / Main App handlers
    # ==============================================================

    def set_windows(self):
        """Define status bar, panels, boxes, widgets.

        Panels are described as "windows".
        Let's see what happens if I have more than one.

        Boxes (called "BoxSizer") work like in Qt.
        They have an orientation = HORIZONTAL or VERTICAL
        Can add spacers.
        """
        # Some test texts
        py_version = "Python: " + platform.python_version()
        wx_version = "wxPython: " + wx.version()
        os_version = "OS: " + platform.platform()

        pnl = wx.Panel(self)

        # What I think of as a "panel" may be a "dialog" in wx?

        # Looks like all StaticTexts have to be associated to pnl.
        # This is the big header item.
        st = wx.StaticText(pnl, label=CI.txt.desc_saskan_eyes)
        font = st.GetFont()
        font.PointSize += 10
        font.Weight = wx.FONTWEIGHT_BOLD
        # or.. font = font.Bold()
        st.SetFont(font)

        vbox = wx.BoxSizer(wx.VERTICAL)
        # the big header
        # This seems to be a way of positioning the text in the box.
        # Not sure why they wouldn't just use pos.
        # The "Add" method does not seem to be well documented.
        # For vertical boxes, the 2nd attribute of Add is "size"?
        # For horizontal boxes, the 1st attribute of Add is "size"?
        # So... that last number is border size.
        # .Add(object--like a StaticText,
        #      horizontally-strechable-or-not (wx.EXPAND),
        #      make-a-border-all-around (wx.ALL),
        #      border-size (in px))
        # )
        # .Add(
        #   window, spacer or another sizer,
        #   proportion, (0 --> child is not resizable),
        #   flag --> OR combination of flags,
        #   border (int) if not handled by flags,
        #   userData (object) for more complex controls
        # )
        # Common to add a horization to a vertical, e.g, for a line of buttons.
        # See:
        # https://docs.wxpython.org/sizers_overview.html#programming-with-boxsizer
        # wx.SizerFlags is a kind of (confusing) shortcut for configuring
        # items in a box. Freaking C++ programmers gone nutzo with "flags".

        vbox.Add(st, wx.SizerFlags().Center().Border(wx.TOP | wx.LEFT, 25))
        # the 3 text texts...
        vbox.Add(wx.StaticText(pnl, label=py_version), 0, wx.ALL, 5)
        vbox.Add(wx.StaticText(pnl, label=wx_version), 0, wx.ALL, 5)
        vbox.Add(wx.StaticText(pnl, label=os_version), 0, wx.ALL, 5)
        pnl.SetSizer(vbox)

        # stat = wx.StaticText(pnl, label=self.M["frame"]["c"], pos=(10, 300))
        # Here is a text item I'd use as a status bar.
        # Crap. These sizers are just all over the place.
        stat = wx.StaticText(pnl, label=self.M["frame"]["c"])
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st, wx.SizerFlags().Center().Border(wx.TOP | wx.LEFT, 25))
        hbox.Add(stat, 0, wx.ALL, 50)
        pnl.SetSizer(hbox)

        # Another un-boxed text
        # Like this, it ends up above the firsst unboxed text.
        # st = wx.StaticText(pnl, label=self.M["frame"]["c"])

        # This approach does not seem to work at all on Linux:
        # self.CreateSatatusBar(
        #    1, style=wx.STB_DEFAULT_STYLE, name="frame_status_bar")

        # This creates a status bar but not at the bottom of the frame.
        # Basically, seems to be just another panel.
        # status_bar = wx.StatusBar(
        #    self, wx.ID_ANY,
        #    style=wx.SB_NORMAL,
        #    name="frame_status_bar")
        # status_bar.SetStatusText(self.META["about"]["app"]["c"])

        # This returns None
        # pp(self.GetStatusBar())

        # When I try it this way, nothing at all shows up.
        # status_bar = wx.Panel(self, wx.ID_ANY, pos=wx.Point(0, 500))
        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # hbox.Add(
        #    wx.StaticText(status_bar,
        #                  label=self.M["frame"]["c"]), 0, wx.ALL, 5)
        # status_bar.SetSizer(hbox)

    def set_menus(self):
        """Define menu_bar, menus, menu_items, menu_actions.
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
    SE = SaskanEyes()
    app.MainLoop()
