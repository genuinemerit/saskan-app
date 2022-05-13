#!python
"""Wire Tap Logging and Monitoring utilities and services.
:module:    io_wiretap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""
import sys

from pprint import pprint as pp   # noqa: F401
from io_boot import BootTexts     # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore

BT = BootTexts()
FI = FileIO()
RI = RedisIO()


class WireTap(object):
    """Interface to Log and Monitor Redis databases.
    Call this class to write and read Log or Monitor DBs.
    Eventually, maybe create services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Need to do a cleaner job of setting up the app.
        If files don't exist, create them.
        Move the init and config logic to a separate module.
        Take a look at bow_data for examples.
        """
        ok, msg, self.log_level = FI.get_file(BT.log_level)
        if ok:
            ok, msg, self.trace_level = FI.get_file(BT.trace_level)
        if ok:
            ok, msg, self.debug_level = FI.get_file(BT.debug_level)
        if not ok:
            print(msg)
            exit(1)

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
          (default = 24). If < 1, the record will never expire.
        """
        log_msg = None
        if p_msg_lvl.lower() == "debug" and self.debug_level == "DEBUG":
            log_msg = f"\tDEBUG: {p_msg}"
        elif (p_msg_lvl.lower() in ("info", "", None) and
                self.log_level in ("INFO", "WARN", "ERROR")) or \
             (p_msg_lvl.lower() == "warn" and
                self.log_level in ("WARN", "ERROR")) or \
             (p_msg_lvl.lower() == "error" and
                self.log_level == "ERROR"):
                    log_msg = f"\t{self.log_level}: {p_msg}"  # noqa: E117
        else:
            log_msg = f"\tINFO: {p_msg}"
        if log_msg is not None:
            self.write_log(log_msg, p_expire)

    def dump_log(self):
        """Dump all log records to console."""
        pass
        log_keys = RI.find_keys("log", "log:*")
        for k in sorted(log_keys):
            rec = RI.get_record("log", k)
            ts = rec['name'].replace('log:', '')
            if "/home/" in rec['msg']:
                msg = f"\n\n{ts}\n{rec['msg']}"
            else:
                msg = f"{ts}\t{rec['msg']}"               # ts + body of msg
            print(msg)


if __name__ == '__main__':
    WT = WireTap()
    WT.dump_log()
