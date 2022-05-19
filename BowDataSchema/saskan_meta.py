#!python
"""Saskan Eyes metadata configuration set-up and management.
:module:    saskan_meta.py
:class:     SaskanMeta/0
:author:    GM <genuinemerit @ pm.me>
"""
import json

from os import path
from pprint import pprint as pp   # noqa: F401

from io_config import ConfigIO    # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore

CI = ConfigIO()
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
        RI.write_redis_config("info", CI.txt.val_noinfo)

    def set_info_on():
        """Do write informational messages to log namespace."""
        RI.write_redis_config("info", CI.txt.val_info)

    def set_warn_off():
        """Do not write non-fatal warning messages to log namespace."""
        RI.write_redis_config("warn", CI.txt.val_nowarn)

    def set_warn_on():
        """Do write non-fatal warning messages to log namespace."""
        RI.write_redis_config("warn", CI.txt.val_warn)

    def set_error_off():
        """Do not write fatal error messages to log namespace."""
        RI.write_redis_config("error", CI.txt.val_noerror)

    def set_error_on():
        """Do write fatal error messages to log namespace."""
        RI.write_redis_config("error", CI.txt.val_error)

    def set_debug_off():
        """Do not write debug messages to log namespace."""
        RI.write_redis_config("debug", CI.txt.val_nodebug)

    def set_debug_on():
        """Write debug messages to log namespace."""
        RI.write_redis_config("debug", CI.txt.val_debug)

    def set_trace_off():
        """Do not write trace messages to log namespace."""
        RI.write_redis_config("trace", CI.txt.val_notrace)

    def set_trace_functions_on():
        """Write trace messages to log namespace, naming functions.
        But not writing the docstrings to the log.
        """
        RI.write_redis_config("trace", CI.txt.val_tracef)

    def set_trace_functions_and_docs_on():
        """Write trace messages to log namespace, naming functions.
        And also writing the docstrings to the log.
        """
        RI.write_redis_config("trace", CI.txt.val_traced)

    # Manage GUI widget metadata
    # ==============================================================
    def refresh_gui_meta(self):
        """Refresh Basement DB GUI metadata from JSON config file.
        - Read GUI metadata from the JSON file.
        - Write it to the Namespace 0 'Basement' Redis DB.
        """
        config_file_path = path.join(RI.get_app_path(), CI.gui_metadata)
        ok, err, configs = FI.get_file(config_file_path)
        if not ok:
            print(f"{CI.txt.file_error} {config_file_path} {err}")
            return False
        elif configs is None:
            print(f"{CI.txt.not_found} {config_file_path}")
        RI.write_redis_meta(json.loads(configs))
        return True

    def dump_configs_and_meta(self):
        """Dump records to console.

        @DEV
        - Other types of reports may be added.
        - List summary of records available.
        - Show follow-on commands to drill down.
        - List record keys or file names.
        - List record values or file contents.
        - Probably create separate method for each report/view.
        """
        print("Configs...\n===============\n\n")
        pp((self.get_all_configs()))
        print("GUI Metadata...\n===============\n\n")
        pp((self.get_all_gui_meta()))


if __name__ == '__main__':
    """When executed directly, returns a fixed report."""
    CM = SaskanMeta()
    CM.dump_configs_and_meta()
