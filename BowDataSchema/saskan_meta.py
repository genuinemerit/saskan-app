#!python
"""Saskan Eyes metadata configuration set-up and management.
:module:    saskan_meta.py
:class:     SaskanMeta/0
:author:    GM <genuinemerit @ pm.me>
"""
import json

from os import path
from pprint import pprint as pp   # noqa: F401

from io_boot import BootIO        # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore

BI = BootIO()
FI = FileIO()
RI = RedisIO()


class SaskanMeta(object):
    """Class to manage metadata configuration and loading.

    @DEV
    - Implement calls to specific functions from saskan_eyes.
    """
    def __init__(self):
        """Initialize SaskanMeta object.
        """
        pass

    # Configuration handlers
    # ==============================================================
    def set_info_off():
        """Do not write informational messages to log namespace."""
        ok, err = FI.write_file(BI.info_level, BI.txt.val_noinfo)
        if not(ok):
            print(err)
            exit(1)

    def set_info_on():
        """Do write informational messages to log namespace."""
        ok, err = FI.write_file(BI.info_level, BI.txt.val_info)
        if not(ok):
            print(err)
            exit(1)

    def set_warn_off():
        """Do not write non-fatal warning messages to log namespace."""
        ok, err = FI.write_file(BI.warn_level, BI.txt.val_nowarn)
        if not(ok):
            print(err)
            exit(1)

    def set_warn_on():
        """Do write non-fatal warning messages to log namespace."""
        ok, err = FI.write_file(BI.warn_level, BI.txt.val_warn)
        if not(ok):
            print(err)
            exit(1)

    def set_error_off():
        """Do not write fatal error messages to log namespace."""
        ok, err = FI.write_file(BI.error_level, BI.txt.val_noerror)
        if not(ok):
            print(err)
            exit(1)

    def set_error_on():
        """Do write fatal error messages to log namespace."""
        ok, err = FI.write_file(BI.error_level, BI.txt.val_error)
        if not(ok):
            print(err)
            exit(1)

    def set_debug_off():
        """Do not write debug messages to log namespace."""
        ok, err = FI.write_file(BI.debug_level, BI.txt.val_nodebug)
        if not(ok):
            print(err)
            exit(1)

    def set_debug_on():
        """Write debug messages to log namespace."""
        ok, err = FI.write_file(BI.debug_level, BI.txt.val_debug)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_off():
        """Do not write trace messages to log namespace."""
        ok, err = FI.write_file(BI.trace_level, BI.txt.val_notrace)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_functions_on():
        """Write trace messages to log namespace, naming functions.
        But not writing the docstrings to the log.
        """
        ok, err = FI.write_file(BI.trace_level, BI.txt.val_notracf)
        if not(ok):
            print(err)
            exit(1)

    def set_trace_functions_and_docs_on():
        """Write trace messages to log namespace, naming functions.
        And also writing the docstrings to the log.
        """
        ok, err = FI.write_file(BI.trace_level, BI.txt.val_notracd)
        if not(ok):
            print(err)
            exit(1)

    # Load and save texts and widget metadata
    # ==============================================================
    def load_meta(self):
        """Load configuration data from db to memory."""
        db = "basement"
        keys: list = RI.find_keys(db, "meta:*")
        data: dict = {}
        for k in keys:
            key = k.decode('utf-8').replace("meta:", "")
            record = RI.get_values(RI.get_record(db, k))
            data[key] = record
        return(data)

    def refresh_meta(self):
        """Refresh Basement DB texts, configs from JSON config file."""

        def load_cfg_file():
            """Read data from config file."""
            rec = RI.get_record("basement", BI.app_path_key)
            config_file_path =\
                path.join(rec["values"]["app_path"], BI.file_widgets)
            ok, err, configs = FI.get_file(config_file_path)
            if not ok:
                print(f"{BI.txt.file_error} {config_file_path} {err}")
                exit(1)
            elif configs is None:
                print(f"{BI.txt.not_found} {config_file_path}")
                exit(1)
            config_data = json.loads(configs)
            return(config_data)

        def set_meta(p_config_data: dict):
            """Set text and widget metadata records on Basement DB."""
            db = "basement"
            for k, values in p_config_data.items():
                key = RI.clean_redis_key(f"meta:{k}")
                record = {db: {"name": key} | values}
                record, update = \
                    RI.set_audit_values(record, p_include_hash=True)
                key = record["name"]
                if update:
                    RI.do_update(db, record)
                else:
                    RI.do_insert(db, record)

        set_meta(load_cfg_file())

    def modify_meta(self,
                    p_wdg_catg: str,
                    p_qt_wdg):
        """Update Basement DB with modified widget record.

        - Qt prototype saved a copy of or name of instantiated
          widget object with the metadata.
        - "meta" in this app refers to qualities of widgets and text.
        """
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
        print("Metadata...\n===============\n\n")
        pp((self.load_meta()))


if __name__ == '__main__':
    """When executed directly or from bash, it is a fixed report."""
    CM = SaskanMeta()
    CM.dump_meta()
