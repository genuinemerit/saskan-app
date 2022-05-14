#!python
"""
:module:    saskan_eyes.py
:author:    GM (genuinemerit @ pm.me)
BoW Saskan App Admin GUI.  wx version."""

import argparse
import json
import platform
import wx

from pprint import pprint as pp     # noqa: F401

from io_boot import BootTexts       # type: ignore
from io_file import FileIO          # type: ignore
from io_redis import RedisIO        # type: ignore
# from io_wiretap import WireTap      # type: ignore

BT = BootTexts()
FI = FileIO()
RI = RedisIO()
# WT = WireTap()


class SaskanEyes(wx.Frame):
    """Combo GUI for Admin, Monitor, Controller and Test GUIs.

    Args:
        (object): wx Frame object
    """

    def __init__(self, *args, **kwargs):
        """wx refers to the base parent window object as the frame.
        """
        super(SaskanEyes, self).__init__(*args, **kwargs)
        # WT.log_module(__file__, __name__, self)
        # Put the initialization code in a discrete class?
        # self.ARGS = self.init_configs()
        # self.WDG = self.load_meta("widget")
        self.initialize_gui()

    # GUI / Main App handlers
    # ==============================================================
    def initialize_gui(self):
        """_Set window size and name. Show the window.
        """
        pnl = wx.Panel(self)
        py_version = "Python: " + platform.python_version()
        wx_version = "wxPython: " + wx.version()
        os_version = "OS: " + platform.platform()
        st = wx.StaticText(pnl, label=BT.txt.desc_saskan_eyes)
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
        # self.SetStatusText(BT.txt.desc_saskan_eyes)

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

    # Command line argument handlers
    # ==============================================================
    def init_configs(self):
        """Handle command-line arguments."""

        def set_arguments():
            """Define command-line arguments."""
            parser = argparse.ArgumentParser(description=BT.txt.app_desc)
            parser.add_argument(
                '--force-refresh', action='store_true',
                help=BT.txt.refresh_desc)
            parser.add_argument(
                '--info', action='store_true', help=BT.txt.info_desc)
            parser.add_argument(
                '--warn', action='store_true', help=BT.txt.warn_desc)
            parser.add_argument(
                '--tracef', action='store_true', help=BT.txt.tracef_desc)
            parser.add_argument(
                '--traced', action='store_true', help=BT.txt.traced_desc)
            parser.add_argument(
                '--debug', action='store_true', help=BT.txt.debug_desc)
            args = parser.parse_args()
            return args

        def set_defaults():
            """Set default config file values if not already set."""
            ok, _, _ = FI.get_file(BT.log_level)
            if not ok:
                ok, err = FI.write_file(BT.log_level, BT.txt.error_val)
            if ok:
                ok, _, _ = FI.get_file(BT.trace_level)
                if not ok:
                    ok, err = FI.write_file(BT.trace_level, BT.txt.notrace_val)
            if ok:
                ok, _, _ = FI.get_file(BT.debug_level)
                if not ok:
                    ok, err = FI.write_file(BT.debug_level, BT.txt.nodebug_val)
            if not ok:
                print(err)
                exit(1)

        def handle_arguments(args):
            """Get current settings, then assign actions based on arguments."""
            ok = True
            if args.traced:
                ok, err = FI.write_file(BT.trace_level, BT.txt.traced_val)
            elif args.tracef:
                ok, err = FI.write_file(BT.trace_level, BT.txt.tracef_val)
            if args.warn:
                ok, err = FI.write_file(BT.log_level, BT.txt.warn_val)
            elif args.info:
                ok, err = FI.write_file(BT.log_level, BT.txt.info_val)
            if args.debug:
                ok, err = FI.write_file(BT.debug_level, BT.txt.debug_val)
            if not(ok):
                print(err)
                exit(1)

            if args.force_refresh:
                self.refresh_configs()

        args = set_arguments()
        set_defaults()
        handle_arguments(args)
        WT.log_function(self.init_configs, self)
        return args

    def refresh_configs(self):
        """Refresh Basement DB texts, configs from JSON config file."""

        def load_cfg_file(p_config_file_path: str):
            """Read data from config file."""
            WT.log_function(load_cfg_file, self, 24, self.refresh_configs)
            ok, err, configs = FI.get_file(p_config_file_path)
            if not ok:
                print(f"{BT.txt.err_file} {err}")
                exit(1)
            elif configs is None:
                print(f"{BT.txt.no_file}{p_config_file_path}")
                exit(1)
            config_data = json.loads(configs)
            return(config_data)

        def set_configs(p_config_data: dict,
                        p_catg: str):
            """Set text and widget metadata records on Basement DB."""
            WT.log_function(set_configs, self, 24, self.refresh_configs)
            db = "basement"
            for k, values in p_config_data.items():
                key = RI.clean_redis_key(f"{p_catg}:{k}")
                record = {db: {"name": key} | values}
                record, update = \
                    RI.set_audit_values(record, p_include_hash=True)
                key = record["name"]
                if update:
                    RI.do_update(db, record)
                else:
                    RI.do_insert(db, record)

        WT.log_function(self.refresh_configs, self)
        set_configs(load_cfg_file(BT.file_widgets), "widget")

    # Load and save texts and widget metadata
    # ==============================================================
    def load_meta(self, p_catg):
        """Load configuration data from db to memory."""
        WT.log_function(self.load_meta, self)
        db = "basement"
        keys: list = RI.find_keys(db, f"{p_catg}:*")
        data: dict = {}
        for k in keys:
            key = k.decode('utf-8').replace(f"{p_catg}:", "")
            record = RI.get_values(RI.get_record(db, k))
            data[key] = record
        return(data)

    def save_meta(self,
                  p_wdg_catg: str,
                  p_qt_wdg):
        """Update Basement DB with modified widget record."""
        WT.log_function(self.save_meta, self)
        db = "basement"
        self.WDG[p_wdg_catg]["w"]["name"] = p_qt_wdg.objectName()
        record = {"basement":
                  {"name": f"widget:{p_wdg_catg}"} | self.WDG[p_wdg_catg]}
        record, _ = \
            RI.set_audit_values(record, p_include_hash=True)
        RI.do_update(db, record)
        self.WDG[p_wdg_catg]["w"]["object"] = p_qt_wdg


# Run program
if __name__ == '__main__':
    """Run program."""
    app = wx.App()
    SE = SaskanEyes(None, title="Saskan Eyes", size=(800, 600))
    app.MainLoop()
