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
    """Interface to Log and Monitor name spaces.
    Write and read Log or Monitor data.
    These are proprietary logger functions,
    not standard Python Logging module.

    @DEV:
    - Eventually, create services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Default settings for log, trace, debug configs are set
        as part of saskan_install.

        Modify them manually or using options in saskan_eye.py.
        """
        self.loglv = FI.get_log_settings()

    # Helper functions
    # =========================================================================
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
                          p_dt: datetime) -> str:
        """Return current timestamp w/ microseconds in ISO format as string"""
        ts = p_dt.replace(tzinfo=timezone.utc).isoformat()
        return ts

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
    def get_token(cls) -> str:
        """Generate a cryptographically strong unique ID.
        """
        return (str(uuid.UUID(bytes=secrets.token_bytes(16)).hex) +
                str(uuid.UUID(bytes=secrets.token_bytes(16)).hex))

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
    def get_expire_dt(cls,
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

    @classmethod
    def do_insert(cls,
                  p_ns: str,
                  p_rec: dict,
                  p_expire: int = 0):
        """Insert a pickled record to shared memory.
           Set its expiration time.
           For now, assuming it is in hours.

        @DEV: Consider...
        - Using a hash instead of a pickle?
        - Methods for handling overwrites?

        Args:
        - p_ns: str - Namespace to write to
        - p_rec: dict - Record to write
        - p_expire: int - Expiration time in full hours
        """
        expire_dt = WireTap.get_expire_dt(p_expire)
        dir_nm = path.join(FI.d["MEM"], FI.d["APP"], "data", p_ns)
        uuid = WireTap.get_token()
        rec_nm = p_rec["name"] + "~" + expire_dt + "~" + uuid
        path_nm = path.join(dir_nm, rec_nm)
        ok, msg = FI.pickle_object(path_nm, p_rec)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {path_nm} {msg}")

    @classmethod
    def write_log(cls,
                  p_log_msg: str,
                  p_expire: int = 0):
        """Write a record to "log" namespace.
        Log record format:
        - `name`: `log:` + {expire_timestamp} is the key
        - `msg`: the log message / content
        Default expiration is never."""
        log_dt = WireTap.get_iso_timestamp(datetime.utcnow())
        log_rec = {"name": f"log:{log_dt}", "msg": p_log_msg}
        WireTap.do_insert("log", log_rec, p_expire)

    def write_to_mon(self,
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
        """Trace module name, class name on log ns."""
        if self.loglv["traced"] != "NOTRACE":
            log_msg = f"TRACED: {p_file}"
            if self.loglv["traced"] == "DOCS":
                log_msg += f"\n{sys.modules[p_name].__doc__}"
            log_msg +=\
                f"\nclass: {p_self.__class__.__name__}()"
            if self.loglv["traced"] == "DOCS":
                log_msg += f"\n{p_self.__doc__}"
            WireTap.write_log(log_msg, p_expire)

    def log_function(self,
                     p_func,
                     p_self,
                     p_expire: int = 24,
                     p_parent_func=None):
        """Trace function or subfunction on log db."""
        if self.loglv["tracef"] != "NOTRACE":
            cpfx = f"TRACEF: {p_self.__class__.__name__}."
            ppfx = "" if p_parent_func is None\
                else f"{p_parent_func.__name__}."
            log_msg = f"{cpfx}{ppfx}{p_func.__name__}()"
            if self.loglv["tracef"] == "DOCS":
                log_msg += f"\n\t{p_func.__doc__}"
            WireTap.write_log(log_msg, p_expire)

    def log_msg(self,
                p_msg_lvl: str,
                p_msg: str,
                p_expire: int = 24):
        """Write a regular log message or a debug message to log db.

        @DEV
        - Not entirely sure what rule I am going for here.
        - Work on documenting that more carefully.

        Args:
        - p_msg_lvl: str in ("info", "debug", "error", "warn")
        - p_msg: str is the message to write to log db
        - p_expire: int is the number of hours to expire the log record
          (default = 24). If < 1, the record will never expire.l.
        """
        if ((p_msg_lvl.lower() == "debug" and
             self.loglv["debug"] == FI.t["val_debug"])
            or (p_msg_lvl.lower() == "info" and
                self.loglv["info"] == FI.t["val_info"])
            or (p_msg_lvl.lower() == "warn" and
                self.loglv["info"] == FI.t["val_warn"])
            or (p_msg_lvl.lower() == "error" and
                self.loglv["info"] == FI.t["val_error"])):
            log_msg = f"\t{p_msg_lvl.upper()}: {p_msg}"
            WireTap.write_log(log_msg, p_expire)

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
        """
        log_recs = WireTap.get_records("log", "log:")
        for rec in log_recs:
            print("\n========================================")
            print(rec["name"])
            pp(rec["msg"])


if __name__ == '__main__':
    WT = WireTap()
