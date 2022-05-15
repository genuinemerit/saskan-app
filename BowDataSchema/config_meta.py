#!python
"""Saskan Eyes metadata configuration set-up.
:module:    config_meta.py
:class:     ConfigMeta/0
:author:    GM <genuinemerit @ pm.me>
"""
import json

from pprint import pprint as pp   # noqa: F401
from io_boot import BootTexts     # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore
from io_wiretap import WireTap      # type: ignore

BT = BootTexts()
FI = FileIO()
RI = RedisIO()
WT = WireTap()


class ConfigMeta(object):
    """Class to manage metadata configuration and loading.

    @DEV
    - Implement calls to specific functions from saskan_eyes.
    - May want to set up bash files to call specific sets of
      functions, like resetting all options to defaults.
    """
    def __init__(self):
        """Initialize ConfigMeta object.
        """
        pass

    # Configuration handlers
    # ==============================================================
    def set_info_off():
        """Do not write informational messages to log namespace."""
        ok, err = FI.write_file(BT.info_level, BT.txt.val_noinfo)
        if not(ok):
            print(err)
            exit(1)

    def set_info_on():
        """Do write informational messages to log namespace."""
        ok, err = FI.write_file(BT.info_level, BT.txt.val_info)
        if not(ok):
            print(err)
            exit(1)

    def set_warn_off():
        """Do not write non-fatal warning messages to log namespace."""
        ok, err = FI.write_file(BT.warn_level, BT.txt.val_nowarn)
        if not(ok):
            print(err)
            exit(1)

    def set_warn_on():
        """Do write non-fatal warning messages to log namespace."""
        ok, err = FI.write_file(BT.warn_level, BT.txt.val_warn)
        if not(ok):
            print(err)
            exit(1)

    def set_error_off():
        """Do not write fatal error messages to log namespace."""
        ok, err = FI.write_file(BT.error_level, BT.txt.val_noerror)
        if not(ok):
            print(err)
            exit(1)

    def set_error_on():
        """Do write fatal error messages to log namespace."""
        ok, err = FI.write_file(BT.error_level, BT.txt.val_error)
        if not(ok):
            print(err)
            exit(1)

    def set_debug_off():
        """Do not write debug messages to log namespace."""
        ok, err = FI.write_file(BT.debug_level, BT.txt.val_nodebug)
        if not(ok):
            print(err)
            exit(1)

    def set_debug_on():
        """Write debug messages to log namespace."""
        ok, err = FI.write_file(BT.debug_level, BT.txt.val_debug)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_off():
        """Do not write trace messages to log namespace."""
        ok, err = FI.write_file(BT.trace_level, BT.txt.val_notrace)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_functions_on():
        """Write trace messages to log namespace, naming functions.
        But not writing the docstrings to the log.
        """
        ok, err = FI.write_file(BT.trace_level, BT.txt.val_notracf)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_functions_and_docs_on():
        """Write trace messages to log namespace, naming functions.
        And also writing the docstrings to the log.
        """
        ok, err = FI.write_file(BT.trace_level, BT.txt.val_notracd)
        if not(ok):
            print(err)
            exit(1)

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

    def refresh_meta(self):
        """Refresh Basement DB texts, configs from JSON config file."""

        def load_cfg_file(p_config_file_path: str):
            """Read data from config file."""
            WT.log_function(load_cfg_file, self, 24, self.refresh_meta)
            ok, err, configs = FI.get_file(p_config_file_path)
            if not ok:
                print(f"{BT.txt.err_file} {err}")
                exit(1)
            elif configs is None:
                print(f"{BT.txt.no_file}{p_config_file_path}")
                exit(1)
            config_data = json.loads(configs)
            return(config_data)

        def set_meta(p_config_data: dict,
                     p_catg: str):
            """Set text and widget metadata records on Basement DB."""
            WT.log_function(set_meta, self, 24, self.refresh_meta)
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

        WT.log_function(self.refresh_meta, self)
        set_meta(load_cfg_file(BT.file_widgets), "widget")

    def modify_meta(self,
                    p_wdg_catg: str,
                    p_qt_wdg):
        """Update Basement DB with modified widget record.
        - In Qt, this was helpful for saving a copy of or name of
          the instantiated widget object with the metadata.  Not sure
          if this is doable/desireable with wx. But I hope so.
        - It is really extending meta more so than updating existing
          values. Though I suppose that could change with more dynamic
          options.
        - When I talk about "meta" I almost always mean stuff that
          describes qualities of widgets. But we also store text
          strings in the basement, which are a bit more abstract
          than a specific widget.
        """
        WT.log_function(self.modify_meta, self)
        db = "basement"
        self.WDG[p_wdg_catg]["w"]["name"] = p_qt_wdg.objectName()
        record = {"basement":
                  {"name": f"widget:{p_wdg_catg}"} | self.WDG[p_wdg_catg]}
        record, _ = \
            RI.set_audit_values(record, p_include_hash=True)
        RI.do_update(db, record)
        self.WDG[p_wdg_catg]["w"]["object"] = p_qt_wdg

    def dump_meta(self):
        """Dump records to console.
        A simpler version of the dbeditor.
        - All (?) records in Redis DB 0 "basement" namespace.
        - All (?) records in Redis DB 1 "schema" (meta) namespace.
        - All (?) records in app_dir "config" directory.

        @DEV
        - List summary of records available.
        - Show follow-on commands to drill down.
        - List record keys or file names
        - List record values or file contents
        - Maybe create separate method for each option?
        """
        print("DEBUG: Dumping metadata to console...")


if __name__ == '__main__':
    """When executed directly or from bash, it is a fixed report."""
    CM = ConfigMeta()
    CM.dump_meta()
