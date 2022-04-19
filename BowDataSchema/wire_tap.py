#!python3.9
"""Wire Tap Logging and Monitoring utilities and services.
:module:    wire_tap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""
import sys

from pprint import pprint as pp  # noqa: F401
from redis_io import RedisIO                    # type: ignore

RI = RedisIO()


class WireTap(object):
    """Interface to Log and Monitor Redis databases.
    Call this class to write and read Log or Monitor DBs.
    Eventually, probably create services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object."""
        pass

    def write_log(self,
                     p_log_msg: str,
                     p_expire: int = 0):
        """Log records have a specific format.

        Write a record to DB 3 "log".

        Name: key.
        Value: values use the log record type.
        Audit: values use the audit record type.

        Expire is optional.
        See notes elsewhere regarding expirations.
        
        meta-record definition:
        "rec": {
            "keys": {
                "hash": {
                    "title": "Hash ID",
                    "hint": "🔐",
                    "ed": ["auto"]}},
            "vals": {
                "val": {
                    "title": "Trace Value",
                    "hint": "🔏",
                    "ed": ["auto"]}}
        }
        1. value_in: str or JSON containing the message to log
           It can be just a string but might be better if in a JSON format.
        2. Call redis_io.get_timestamp() to get the timestamp.
        3. Pass timestmp and value_in to redis_io.get_hash(),
             retrieving the hash_id.
        4. Prefix value_in with timestamp value as string and 
        5.   make it a dict w/ format like:
            log_rec = {"name": hash_id, "ts": timestamp, "msg": value_in}
        6. Call redis_io.do_insert("log", log_rec)
        """
        ts = RI.get_timestamp()
        log_rec = {"name": f"log:{ts}", "msg": p_log_msg}
        RI.do_insert("log", log_rec)

    def write_to_mon(self,
                     p_mon_rec: dict,
                     p_expire: int = 0):
        """Monitor records have a specific format.

        Write a record to DB 4 "monitor".

        Name: key.
        Value: values use the monitor record type.
        Audit: values use the audit record type.

        Expire is optional. See notes.
        """
        pass
    
    # Logger functions
    # ==============================================================
    def log_module(self, 
                   p_file: object,
                   p_name: object,
                   p_class: object,
                   p_self: object):
        """Log module name, class name and docstrings to DB."""
        log_msg = "============================================"
        log_msg += f"\nfile:\n{p_file} --> "      # type: ignore
        log_msg += f"\n{sys.modules[p_name].__doc__}"      # type: ignore
        log_msg += f"\nclass: {p_class.__name__}() --> {p_self.__doc__}"   # type: ignore
        self.write_log(log_msg)

    def log_function(self,
                     p_func: object,
                     p_is_sub: bool = False,
                     p_class: object = None):
        """Log function and docstring to DB."""
        clspfx = "" if p_class is None else f"{p_class.__name__}."         # type: ignore
        subpfx = "sub" if p_is_sub else ""
        log_msg = f"{subpfx}function: {clspfx}{p_func.__name__}()"        # type: ignore
        log_msg += f" --> {p_func.__doc__}"                               # type: ignore
        self.write_log(log_msg)

    def log_msg(self,
                p_msg: str,
                p_debug: bool = False):
        """Log a message."""
        msgpfx = "DEBUG " if p_debug else "INFO "
        log_msg = f"\t{msgpfx} msg: {p_msg}"
        self.write_log(log_msg)

    def dump_log(self):
        """Dump all log records to console."""
        pass
        log_keys = RI.find_keys("log", "log:*")
        for k in sorted(log_keys):
            rec = RI.get_record("log", k)
            msg = rec['name'].replace('log:', '')
            msg += f"\n\t{rec['msg']}"
            pfx = "\n\n" if "file:" in rec['msg'] else ""
            print(f"{pfx}{msg}")
