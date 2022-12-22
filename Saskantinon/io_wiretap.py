#!python
"""Wire Tap Logging and Monitoring utilities and services.
:module:    io_wiretap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""

import hashlib
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

    @DEV:
    - Use services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Default settings for log, trace, debug configs are set
        as part of saskan_install. See config/t_texts_*.json,
        """
        self.mon_ns = path.join(FI.D["MEM"], FI.D["APP"],
                                FI.D['ADIRS']["SAV"],
                                FI.D['NSDIRS']["MON"])
        self.llvl = {
            "CRITICAL": 50,
            "FATAL": 50,
            "ERROR": 40,
            "ERR": 40,
            "WARNING": 30,
            "WARN": 30,
            "INFO": 20,
            "DEBUG": 10,
            "NOTSET": 0}
        self.CRITICAL: int = 50
        self.ERROR: int = 40
        self.WARNING: int = 30
        self.INFO: int = 20
        self.DEBUG: int = 10
        self.NOTSET: int = 0
        self.log_level = self.llvl[FI.D["LOGCFG"]]
        self.log_dir_nm = path.join(FI.D["MEM"], FI.D["APP"],
                                    FI.D['ADIRS']["SAV"],
                                    FI.D['NSDIRS']["LOG"])
        self.mon_dir_nm = path.join(FI.D["MEM"], FI.D["APP"],
                                    FI.D['ADIRS']["SAV"],
                                    FI.D['NSDIRS']["MON"])

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
    def get_token(cls,
                  p_len = 32) -> str:
        """Generate a cryptographically strong unique ID.
        """
        token = (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))
        if p_len > 10 and p_len < 32:
            token = token[:p_len]
        return token

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
            expire_dt = datetime.utcnow() + timedelta(days=60)
        else:
            expire_dt = datetime.utcnow() + timedelta(hours=int(p_expire))
        exp_dt = WireTap.get_iso_timestamp(expire_dt)
        return exp_dt

    def write_log(self,
                  p_lvl: str,
                  p_msg: str,
                  p_expire: int = 0):
        """Write a record to Log namespace.

        Log record format:
        - name: `log:` + {level}: + {expire_timestamp} is the key
        - content: the log message"""
        log_dt = WireTap.get_iso_timestamp(datetime.utcnow())
        expire_dt = WireTap.set_expire_dt(p_expire)
        uuid = WireTap.get_token(16)
        rec_nm = (f"log~{p_lvl}~{log_dt}~{expire_dt}~{uuid}")
        msg = p_lvl + "~" + p_msg
        FI.write_file(path.join(self.log_dir_nm, rec_nm), msg)

    def write_trace(self,
                    p_lvl: str,
                    p_rec: str,
                    p_expire: int = 0):
        """Trace records have a specific format and are written
        to the monitoring namespace.

        Trace record format:
        - name: `mon:` + {level}: + {expire_timestamp} is the key
        - content: the trace record"""
        mon_dt = WireTap.get_iso_timestamp(datetime.utcnow())
        expire_dt = WireTap.set_expire_dt(p_expire)
        uuid = WireTap.get_token(16)
        rec_nm = (f"trace~{p_lvl}~{mon_dt}~{expire_dt}~{uuid}")
        rec = p_lvl + "~" + p_rec
        FI.write_file(path.join(self.mon_dir_nm, rec_nm), rec)

    # Logger functions
    # ==============================================================

    def trace_code(self,
                   p_file,
                   p_name,
                   p_self,
                   p_c_or_f="class",
                   p_expire=24,
                   p_parnt_f=None):
        """Trace code name for functions and classes.
        Traces are logged only if TRCCFG is set to "NODOCS" or "DOCS",
        which is to say it NOT set to "NOTRACE".
        If "DOCS", then inline documentation is included in the trace.

        @DEV: Needs work...
        """
        is_cls = True if p_c_or_f.lower() in ("class", "cls", "c") else False
        is_fnc = True if p_c_or_f.lower() in\
            ("function", "func", "f") else False
        if FI.D["TRCCFG"] != "NOTRACE":
            if is_cls:
                trc_msg = (p_file +
                           f"\t{p_self.__class__.__name__}()")
            elif is_fnc:
                par_nm = "" if p_parnt_f is None else p_parnt_f.__name__
                trc_msg = (p_self.__class__.__name__ + "." + par_nm)
            if FI.D["TRCCFG"] == "DOCS":
                if is_cls:
                    trc_msg += f"\n{sys.modules[p_name].__doc__}"
                    trc_msg += f"\n{p_self.__doc__}"
                elif is_fnc:
                    trc_msg += f"\n\t{p_file.__doc__}"
            msg = str(trc_msg).strip()
            self.write_trace(p_c_or_f.upper(), msg, p_expire)

    def log_msg(self,
                p_lvl,
                p_msg: str,
                p_expire: int = 24):
        """Write a log message to log namespace.

        Args:
        - p_lvl: standard string index to log level
        - p_msg: message to be logged
        - p_expire: int number of hours in which to expire the log record.
          If < 1, empty, or null, default is set per set_expire_dt() method.
        """
        if self.log_level > self.llvl["NOTSET"]:
            msg = str(p_msg).strip()
            msg_lvl = self.llvl[p_lvl.upper()]
            if (msg_lvl == self.llvl["CRITICAL"] or
                    p_msg.upper() in ("FATAL", "CRITICAL")):
                self.write_log('FATAL', msg, p_expire)
            elif ((msg_lvl == self.llvl["ERROR"] or
                    p_msg.upper() == "ERROR") and
                    self.log_level <= self.llvl["ERROR"]):
                self.write_log('ERROR', msg, p_expire)
            elif ((msg_lvl == self.llvl["WARNING"] or
                    p_msg.upper() == 'WARNING') and
                    self.log_level <= self.llvl["WARNING"]):
                self.write_log('WARNING', msg, p_expire)
            elif ((msg_lvl == self.llvl["INFO"] or
                    p_msg.upper() == 'INFO') and
                    self.log_level <= self.llvl["INFO"]):
                self.write_log('INFO', msg, p_expire)
            elif ((msg_lvl == self.llvl["DEBUG"] or
                    p_msg.upper() == 'DDEBUG') and
                    self.log_level <= self.llvl["DEBUG"]):
                self.write_log('DEBUG', msg, p_expire)

    # Generic DDL functions
    # =========================================================================
    @classmethod
    def find_keys(cls,
                  p_ns: str,
                  p_key_pattern: str):
        """Return keys of records that match search pattern."""
        dir_nm = path.join(FI.D["MEM"], FI.D["APP"], "data", p_ns)
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
