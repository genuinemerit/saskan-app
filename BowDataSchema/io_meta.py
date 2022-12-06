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
    """Class to manage metadata configuration and loading.

    @DEV
    - Implement calls to specific functions from saskan_eyes.
    """
    def __init__(self):
        """Initialize MetaIO object.
        """
        self.config_dir = "config"
        self.shared_mem_dir = "/dev/shm"

    # Get setup metadata
    # ==============================================================

    def get_text_meta(self,
                      p_lang: str = "en"):
        """If pickle does not exist then..
        - Read static text values from JSON file.
        - Store it in a class and pickle it in shared memory.

        Args: (str) p_lang: Language code.
        Returns: (dict) Text values or exception.
        """
        file_nm = f"m_texts_{p_lang}"
        pk_file_path = path.join(self.shared_mem_dir, f"{file_nm}.pickle")
        cfg_file_path = path.join(self.config_dir, f"{file_nm}.json")
        ok, msg, txts = FI.unpickle_object(pk_file_path)
        if not ok:
            ok, msg, txts_j = FI.get_file(cfg_file_path)
            txts = json.loads(txts_j)
            if ok:
                ok, msg = FI.pickle_object(pk_file_path, txts)
                if not ok:
                    raise Exception(
                        f"Error pickling <{p_lang}> text metadata: {msg}")
            else:
                raise Exception(
                    f"Error reading <{p_lang}> texts metadata: {msg}")
        return txts

    def get_dirs_meta(self):
        """Read app set-up metadata regarding directories from JSON file.
        Returns: (dict) Directory values or exception.
        """
        ok, msg, dirs =\
            FI.get_file(path.join(self.config_dir, "m_directories.json"))
        if not ok:
            raise Exception(f"Error reading directories metadata: {msg}")
        return(json.loads(dirs))

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
