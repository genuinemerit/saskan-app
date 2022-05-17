#!python
"""Wire Tap Logging and Monitoring utilities and services.
:module:    io_wiretap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""
import sys

from pprint import pprint as pp   # noqa: F401
from io_boot import BootIO        # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore

BI = BootIO()
FI = FileIO()
RI = RedisIO()


class WireTap(object):
    """Interface to Log and Monitor Redis databases.
    Call this class to write and read Log or Monitor DBs.
    These are proprietary logger functions using Redis,
    not the standard Python Logging module.

    @DEV:
    - Eventually, create services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Default settings for log, trace, debug configs are set
        as part of saskan_install. Will crash if config files
        have not been created properly.

        Modify them using options in config_meta.py.
        @DEV:
        - Provide a menu item to saskan_eyes do the same.
        """
        rec = RI.get_record("basement", BI.app_path_key)
        self.APP_PATH = rec['values']['app_path']
        with open(f"{self.APP_PATH}/cfg/debug_level.cfg") as f:
            self.debug_level: str = f.read
        with open(f"{self.APP_PATH}/cfg/info_level.cfg") as f:
            self.info_level: str = f.read
        with open(f"{self.APP_PATH}/cfg/warn_level.cfg") as f:
            self.warn_level: str = f.read
        with open(f"{self.APP_PATH}/cfg/error_level.cfg") as f:
            self.error_level: str = f.read
        with open(f"{self.APP_PATH}/cfg/trace_level.cfg") as f:
            self.trace_level: str = f.read

    def write_log(self,
                  p_log_msg: str,
                  p_expire: int = 0):
        """Write a record to DB 3 "log" namespace.
        Log record format:
        - `name`: `log:` + {timestamp} is the key
        - `msg`: labels the log message
        Default expiration is never."""
        ts = RI.get_timestamp()
        log_rec = {"name": f"log:{ts}", "msg": p_log_msg}
        RI.do_insert("log", log_rec, p_expire)

    def write_to_mon(self,
                     p_mon_rec: dict,
                     p_expire: int = 0):
        """Monitor records have a specific format."""
        pass

    # Logger functions
    # ==============================================================
    def log_module(self,
                   p_file: object,
                   p_name: object,
                   p_self: object,
                   p_expire: int = 24):
        """Trace module name, class name on log db."""
        if self.trace_level != "NOTRACE":
            log_msg = f"{p_file}"                              # type: ignore
            if self.trace_level == "DOCS":
                log_msg += f"\n{sys.modules[p_name].__doc__}"  # type: ignore
            log_msg +=\
                f"\nclass: {p_self.__class__.__name__}()"      # type: ignore
            if self.trace_level == "DOCS":
                log_msg += f"\n{p_self.__doc__}"               # type: ignore
            self.write_log(log_msg, p_expire)

    def log_function(self,
                     p_func: object,
                     p_self: object,
                     p_expire: int = 24,
                     p_parent_func: object = None):
        """Trace function or subfunction on log db."""
        if self.trace_level != "NOTRACE":
            cpfx = f"{p_self.__class__.__name__}."            # type: ignore
            ppfx = "" if p_parent_func is None\
                else f"{p_parent_func.__name__}."             # type: ignore
            log_msg = f"{cpfx}{ppfx}{p_func.__name__}()"      # type: ignore
            if self.trace_level == "DOCS":
                log_msg += f"\n\t{p_func.__doc__}"            # type: ignore
            self.write_log(log_msg, p_expire)

    def log_msg(self,
                p_msg_lvl: str,
                p_msg: str,
                p_expire: int = 24):
        """Write a regular log message or a debug message to log db.
        :attrs:
        - p_msg_lvl: str in ("info", "debug", "error", "warn")
        - p_msg: str is the message to write to log db
        - p_expire: int is the number of hours to expire the log record
          (default = 24). If < 1, the record will never expire.l.
        """
        if ((p_msg_lvl.lower() == "debug" and
             self.debug_level == BI.txt.val_debug)
            or (p_msg_lvl.lower() == "info" and
                self.info_level == BI.txt.val_info)
            or (p_msg_lvl.lower() == "warn" and
                self.info_level == BI.txt.val_warn)
            or (p_msg_lvl.lower() == "error" and
                self.info_level == BI.txt.val_error)):
            log_msg = f"\t{self.p_msg_lvl.upper()}: {p_msg}"
            self.write_log(log_msg, p_expire)

    def dump_log(self):
        """Dump all log records to console."""
        pass
        log_keys = RI.find_keys("log", "log:*")
        if len(log_keys) > 0:
            for k in sorted(log_keys):
                rec = RI.get_record("log", k)
                ts = rec['name'].replace('log:', '')
                # return ts + body of msg
                if "/home/" in rec['msg']:
                    msg = f"\n\n{ts}\n{rec['msg']}"
                else:
                    msg = f"{ts}\t{rec['msg']}"
                print(msg)
        else:
            print(BI.txt.not_found)


if __name__ == '__main__':
    WT = WireTap()
    WT.dump_log()
