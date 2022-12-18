#!python
"""Wire Tap Logging and Monitoring utilities and services.
:module:    io_wiretap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""

import hashlib
import logging
import json
import secrets
import sys
import uuid
import zlib

from datetime import datetime, timedelta, timezone
from os import path
from pprint import pprint as pp   # noqa: F401

from io_file import FileIO    # type: ignore

FI = FileIO()


class WireTap(object):
    """Interface for writing to Log and Monitor name spaces.

    Logging occurs based on what value logging level is set to.
    These are standard values.

    The log levels work in a hierarchy. If DEBUG is set, then all
        levels above it are "on" too. If INFO is set, all levels above are "on"
        but level below (i.e., DEBUG) is off.

    All messages likewise have a log level, also standard.
    When a message is logged, it is written to the log namespace _only_
        if the message level is "within" the currently-configured log level.

    We also have these two special settings, which are for tracing.
        - traced = "DOCS" | "NODOCS" | "NOTRACE"
        - tracef = "DOCS" | "NODOCS" | "NOTRACE"
    Trace settings are off ("NOTRACE") or set to verbose ("DOCS")
        or non-verbose ("NODOCS").
    traced is for tracing what module was executed.
    tracef is for tracing what function was executed.

    @DEV:
    - Use services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Default settings for log, trace, debug configs are set
        as part of saskan_install. See config/t_texts_*.json,
        """
        self.mon_ns = path.join(FI.d["MEM"], FI.d["monitor"])
        self.llvl = {
            "CRITICAL": 50,
            "ERROR": 40,
            "WARNING": 30,
            "INFO": 20,
            "DEBUG": 10,
            "NOTSET": 0}
        self.CRITICAL: int = 50
        self.ERROR: int = 40
        self.WARNING: int = 30
        self.INFO: int = 20
        self.DEBUG: int = 10
        self.NOTSET: int = 0
        self.set_log()
        self.set_mon()

    def set_log(self) -> None:
        """Define logging settings.

        @DEV:
        - Need to do anything to check if log has already been set?
        """
        self.log = logging.getLogger("wiretap")
        self.log_level = self.llvl[FI.d["LOGCFG"]]
        self.log.setLevel(self.log_level)
        self.log_dir_nm = path.join(FI.d["MEM"], FI.d["APP"], FI.d["log"])
        self.log_file_nm = (FI.d["log_file"] + "_" +
                            self.get_iso_timestamp() + ".log")
        logFile = logging.FileHandler(
            path.join(self.log_dir_nm, self.log_file_nm))
        logFile.setLevel(self.llvl[FI.d["LOGCFG"]])
        self.log.addHandler(logFile)

    def set_mon(self) -> None:
        """Define monitoring settings."""
        self.mon_file = path.join(self.mon_ns, FI.d["monitor_file"] + "_" +
                                  self.get_iso_timestamp() + ".mon")

    # Helper functions
    # =========================================================================
    @classmethod
    def bump_underbars(cls, text) -> str:
        """Remove stray underbars

        - Remove leading or trailing underbars
        - Reduce multiple underbars to single underbars
        """
        r_str = text
        while "__" in r_str:
            r_str = r_str.replace("__", "_")
        while r_str[-1:] == "_":
            r_str = r_str[:-1]
        while r_str[:1] == "_":
            r_str = r_str[1:]
        return r_str

    @classmethod
    def convert_dict_to_bytes(self,
                              p_msg: dict) -> object:
        """Convert Python dict to compressed JSON bytes."""
        msg_json: str = json.dumps(p_msg)
        return zlib.compress(bytes(msg_json, 'utf-8'))

    @classmethod
    def convert_bytes_to_dict(self,
                              p_msg: bytes) -> dict:
        """Convert compressed JSON bytes to Python dict."""
        msg_dict = zlib.decompress(p_msg)
        return json.loads(msg_dict)

    @classmethod
    def get_hash(cls,
                 p_data_in: str) -> str:
        """Create hash of input string, returning UTF-8 hex-string.
           Use SHA-512 by default.
        """
        v_hash = hashlib.sha512()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

    @classmethod
    def get_iso_timestamp(cls,
                          p_dt: datetime = None) -> str:
        """Return current timestamp w/ microseconds in ISO format as string"""
        p_dt = datetime.now() if p_dt is None else p_dt
        ts = p_dt.replace(tzinfo=timezone.utc).isoformat()
        return ts

    @classmethod
    def get_token(cls) -> str:
        """Generate a cryptographically strong unique ID.
        """
        return (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))

    @classmethod
    def set_version(cls,
                    p_ver: str,
                    p_bump: str) -> str:
        """Return version string with specified counter bumped.

        :Args:
            p_ver: str - Current version string
            p_bump: str - Counter to bump

        If current_version = 1.1.1, then
        - set_version(p_ver, "major") -> 2.0.0
        - set_version(p_ver, "minor") -> 1.2.0
        - set_version(p_ver, "fix") -> 1.1.2
        """
        r_ver = p_ver.split(".")
        if p_bump == "major":
            r_ver[0] = str(int(r_ver[0]) + 1)
            r_ver[1] = "0"
            r_ver[2] = "0"
        elif p_bump == "minor":
            r_ver[1] = str(int(r_ver[1]) + 1)
        elif p_bump == "fix":
            r_ver[2] = str(int(r_ver[2]) + 1)
        m_ver = r_ver[0] + "." + r_ver[1] + "." + r_ver[2]
        return m_ver

    @classmethod
    def set_expire_dt(cls,
                      p_expire: int = 0) -> str:
        """Compute expiration date-time.
        Default is 60 days from now.

        Arg: p_expire: int - Expiration time in hours
        Return: expiration date-time as a string
        """
        if p_expire == 0 or p_expire is None:
            expire_dt = datetime.utcnow() + timedelta(days=+60)
        else:
            expire_dt = datetime.utcnow() + timedelta(hours=+p_expire)
        exp_dt = WireTap.get_iso_timestamp(expire_dt)
        return exp_dt

    def write_log(self,
                  p_log_msg: str,
                  p_expire: int = 0):
        """Write a record to Log namespace.

        @DEV:
        - Can this be an async function?

        Log record format:
        - `name`: `log:` + {expire_timestamp} is the key
        - `msg`: the log message / content"""
        log_dt = WireTap.get_iso_timestamp(datetime.utcnow())
        expire_dt = WireTap.set_expire_dt(p_expire)
        uuid = WireTap.get_token()
        rec_nm = (f"log~{log_dt}~{expire_dt}~{uuid}")
        FI.write_file(path.join(self.log_dir_nm, rec_nm), p_log_msg)

    def write_mon(self,
                  p_mon_rec: dict,
                  p_expire: int = 0):
        """Monitor records have a specific format."""
        pass

    # Logger functions
    # ==============================================================
    def log_module(self,
                   p_file,
                   p_name,
                   p_self,
                   p_expire: int = 24):
        """Trace module name, class name on log ns.

        @FIX:
        - trace request will be called seaprately from log request
        - indicate module or fucntion in request param instead of
          calling two different methods.
        - why "TRACED" instead of "TRACEM"?
        """
        if self.log_levels["traced"] != "NOTRACE":
            log_msg = f"TRACED: {p_file}"
            if self.log_levels["traced"] == "DOCS":
                log_msg += f"\n{sys.modules[p_name].__doc__}"
            log_msg +=\
                f"\nclass: {p_self.__class__.__name__}()"
            if self.log_levels["traced"] == "DOCS":
                log_msg += f"\n{p_self.__doc__}"
            WireTap.write_log(log_msg, p_expire)

    def log_function(self,
                     p_func,
                     p_self,
                     p_expire: int = 24,
                     p_parent_func=None):
        """Trace function or subfunction on log db."""
        if self.log_levels["tracef"] != "NOTRACE":
            cpfx = f"TRACEF: {p_self.__class__.__name__}."
            ppfx = "" if p_parent_func is None\
                else f"{p_parent_func.__name__}."
            log_msg = f"{cpfx}{ppfx}{p_func.__name__}()"
            if self.log_levels["tracef"] == "DOCS":
                log_msg += f"\n\t{p_func.__doc__}"
            WireTap.write_log(log_msg, p_expire)

    def log_msg(self,
                p_msg_lvl: str,
                p_msg: str,
                p_expire: int = 24):
        """Write a log message to log namespace.

        Args:
        - p_msg_lvl: standard string index to log level
        - p_msg: message to be logged
        - p_expire: int number of hours in which to expire the log record.
          If < 1, empty, or null, default is set per set_expire_dt() method.
        """
        if self.log_level > self.llvl["NOTSET"]:
            msg = (p_msg_lvl.upper() + ":" +
                   self.get_iso_timestamp() + ":" +
                   str(p_msg).strip())
            msg_lvl = self.llvl[p_msg_lvl.upper()]
            if msg_lvl <= self.llvl["CRITICAL"]:
                logging.fatal(msg)
            elif msg_lvl <= self.llvl["ERROR"] and\
                    self.log_level <= self.llvl["ERROR"]:
                logging.error(msg)
            elif msg_lvl <= self.llvl["WARNING"] and\
                    self.log_level <= self.llvl["WARNING"]:
                logging.warning(msg)
            elif msg_lvl <= self.llvl["INFO"] and\
                    self.log_level <= self.llvl["INFO"]:
                logging.info(msg)
            elif msg_lvl <= self.llvl["DEBUG"] and\
                    self.log_level <= self.llvl["DEBUG"]:
                logging.debug(msg)

        # Alternatively... write each record as a file...
        # May want to keep this method for monitoring and if the logger
        # slows things down too much.

        # WireTap.write_log(log_msg, p_expire)

    # Generic DDL functions
    # =========================================================================
    @classmethod
    def find_keys(cls,
                  p_ns: str,
                  p_key_pattern: str):
        """Return keys of records that match search pattern."""
        dir_nm = path.join(FI.d["MEM"], FI.d["APP"], "data", p_ns)
        _, _, keys = FI.get_dir(dir_nm)
        keys = [f for f in keys if p_key_pattern in str(f)]
        return sorted(keys)

    @classmethod
    def count_keys(cls,
                   p_ns: str,
                   p_key_pattern: str):
        """Return number of keys that match search pattern."""
        keys = WireTap.find_keys(p_ns, p_key_pattern)
        return len(keys)

    @classmethod
    def get_records(cls,
                    p_ns: str,
                    p_key_pattern: str):
        """Return existing record if one exists for a specified key.

        :Args:
        - p_ns (str) name of the data namespace
        - p_key_pattern (str) key value or pattern of rec(s) to retrieve
        :Returns:
        - recs (list) - list of (record data dicts)
        """
        recs = list()
        keys = WireTap.find_keys(p_ns, p_key_pattern)
        for key in keys:
            _, _, rec = FI.unpickle_object(key)
            recs.append(rec)
        return recs

    # Reporting functions
    # =========================================================================
    def dump_log(self):
        """Dump all log records to console.
        Move this to a reporting module.
        """
        log_recs = WireTap.get_records("log", "log:")
        for rec in log_recs:
            print("\n========================================")
            print(rec["name"])
            pp(rec["msg"])


if __name__ == '__main__':
    WT = WireTap()
