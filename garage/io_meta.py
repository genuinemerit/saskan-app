#!python
"""Metadata / configuration data set-up, storage, management.
:module:    io_meta.py
:class:     MetaIO/0
:author:    GM <genuinemerit @ pm.me>

@DEV
- Add a separate reports/monitoring class.
"""
import json

from os import path
from pprint import pprint as pp

from io_file import FileIO

FI = FileIO()


class MetaIO(object):
    """Class to modify metadata configuration and loading.

    @DEV
    - Implement calls to specific functions from saskan_eyes.
    - May want to move all this to io_file
    """
    def __init__(self):
        """Initialize MetaIO object.
        """
        pass

    # Set configuration values
    # ==============================================================
    def set_info_off(self):
        """Do not write informational messages to log namespace."""
        RI.write_redis_config("info", CI.txt.val_noinfo)

    def set_info_on(self):
        """Do write informational messages to log namespace."""
        RI.write_redis_config("info", CI.txt.val_info)

    def set_warn_off(self):
        """Do not write non-fatal warning messages to log namespace."""
        RI.write_redis_config("warn", CI.txt.val_nowarn)

    def set_warn_on(self):
        """Do write non-fatal warning messages to log namespace."""
        RI.write_redis_config("warn", CI.txt.val_warn)

    def set_error_off(self):
        """Do not write fatal error messages to log namespace."""
        RI.write_redis_config("error", CI.txt.val_noerror)

    def set_error_on(self):
        """Do write fatal error messages to log namespace."""
        RI.write_redis_config("error", CI.txt.val_error)

    def set_debug_off(self):
        """Do not write debug messages to log namespace."""
        RI.write_redis_config("debug", CI.txt.val_nodebug)

    def set_debug_on(self):
        """Write debug messages to log namespace."""
        RI.write_redis_config("debug", CI.txt.val_debug)

    def set_trace_off(self):
        """Do not write trace messages to log namespace."""
        RI.write_redis_config("trace", CI.txt.val_notrace)

    def set_trace_functions_on(self):
        """Write trace messages to log namespace, naming functions.
        But not writing the docstrings to the log.
        """
        RI.write_redis_config("trace", CI.txt.val_tracef)

    def set_trace_functions_and_docs_on(self):
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

        """
        print("Configs...\n===============\n\n")
        pp((self.get_all_configs()))
        print("GUI Metadata...\n===============\n\n")
        pp((self.get_all_gui_meta()))


"""
if __name__ == '__main__':
    # When executed directly, returns a fixed report.
    CM = MetaIO()
    # CM.dump_configs_and_meta()
"""
