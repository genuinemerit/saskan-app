#!python
"""Wire Tap Logging and Monitoring utilities and services.
:module:    io_wiretap.py
:class:     WireTap/0
:author:    GM <genuinemerit @ pm.me>
"""

import hashlib
import json
import secrets
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

    All messages likewise have a log level.
    When a message is logged, it is written as a discrete file to the log directory
        only if the message level is within scope of currently-configured log level.

    @DEV:
    - Consider using services instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object.

        Default settings for log, trace, debug configs are set
        as part of saskan_install. See config/t_texts_*.json.

        When loglevel is set to NOTSET, no logging occurs.

        To test, prototype, simulate without running the install
        module, set the following class variables manually after
        creating the appropriate directories.
        - log_level
        - log_dir_nm
        - mon_dir_nm (not used yet)
        """
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
        """
        self.mon_ns = path.join(FI.D["MEM"], FI.D["APP"],
                                FI.D['ADIRS']["SAV"],
                                FI.D['NSDIRS']["MON"])    # not used
        self.log_level = self.llvl[FI.D["LOGCFG"]]
        self.log_dir_nm = path.join(FI.D["MEM"], FI.D["APP"],
                                    FI.D['ADIRS']["SAV"],
                                    FI.D['NSDIRS']["LOG"])
        self.mon_dir_nm = path.join(FI.D["MEM"], FI.D["APP"],
                                    FI.D['ADIRS']["SAV"],
                                    FI.D['NSDIRS']["MON"])
        """
        self.log_dir_nm = "/dev/shm/saskan/cache/log"
        self.log_level = self.llvl["DEBUG"]
        # self.log_level = self.llvl["NOTSET"]
        self.mon_dir_nm = "/dev/shm/saskan/cache/mon"   # not used yet

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
                  p_len=32) -> str:
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

    # Logger function
    # ==============================================================
    def log(self,
            p_lvl: str,
            p_msg: str,
            p_file=None,
            p_name=None,
            p_self=None,
            p_frame=None):
        """Write a log message to log namespace.
        If file, name, self and frame objects provided, then trace the call.

        Args:
        - p_lvl: standard string index to log level
        - p_msg: message to be logged
        - p_file: __file__ object of calling function
        - p_name: __name__ object of calling function
        - p_self: self object of calling function
        - p_frame: sys._getframe() from calling function
        """
        def trace_msg(p_msg):
            if (p_file is not None and p_name is not None and
                    p_self is not None and p_frame is not None):
                p_msg += (f"\n{p_file} : {p_name}\n" +
                          f"{p_self.__class__.__name__} : " +
                          f"{p_frame.f_back.f_code.co_name} : " +
                          f"{p_frame.f_code.co_name} : " +
                          f"line {p_frame.f_lineno}\n")
            return p_msg

        def write_log(p_lvl, p_msg):
            """
            Since the log message is just a string, there does not
            appear to be any advantage in pickling the message file.
            No commpression savings, likely takes more time to pickle
            and unpickle than to write the string to a file.
            If I want to save space, then I should compress the log
            files. No point to it though, when writing to memory.
            Compress when archiving to disk.
            """
            log_dt = WireTap.get_iso_timestamp(datetime.utcnow())
            expire_dt = WireTap.set_expire_dt()
            uuid = WireTap.get_token(16)
            rec_nm = (f"log~{p_lvl}~{log_dt}~{expire_dt}~{uuid}")
            msg = p_lvl + "~" + p_msg
            FI.write_file(path.join(self.log_dir_nm, rec_nm), msg)
            # FI.pickle_object(path.join(self.log_dir_nm, rec_nm), msg)

        # log() MAIN
        # ==========================================================
        if self.log_level > self.llvl["NOTSET"]:
            msg = trace_msg(str(p_msg).strip() + "\n")
            msg_lvl = self.llvl[p_lvl.upper()]

            pp((p_msg, msg, p_lvl, msg_lvl))

            if (msg_lvl == self.llvl["CRITICAL"] or
                    p_lvl.upper() in ("FATAL", "CRITICAL")):
                write_log('FATAL', msg)
            elif ((msg_lvl == self.llvl["ERROR"] or
                    p_lvl.upper() == "ERROR") and
                    self.log_level <= self.llvl["ERROR"]):
                write_log('ERROR', msg)
            elif ((msg_lvl == self.llvl["WARNING"] or
                    p_lvl.upper() == 'WARNING') and
                    self.log_level <= self.llvl["WARNING"]):
                write_log('WARNING', msg)
            elif ((msg_lvl == self.llvl["INFO"] or
                    p_lvl.upper() == 'INFO') and
                    self.log_level <= self.llvl["INFO"]):
                write_log('INFO', msg)
            elif ((msg_lvl == self.llvl["DEBUG"] or
                    p_lvl.upper() == 'DEBUG') and
                    self.log_level <= self.llvl["DEBUG"]):
                write_log('DEBUG', msg)

    # Generic DDL functions
    # =========================================================================
    @classmethod
    def find_keys(cls,
                  p_ns: str,
                  p_key_pattern: str):
        """Return keys of records that match search pattern."""
        keys = FI.get_dir(p_ns)
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
            # _, _, rec = FI.unpickle_object(key)
            rec = FI.get_file(key)
            recs.append((key, rec))
        return recs

    # Reporting functions
    # =========================================================================
    def dump_log(self):
        """Dump all log records to console.
        Move this to a reporting module.
        """
        log_recs = WireTap.get_records(self.log_dir_nm, "log~")
        for rec in log_recs:
            print(rec)


if __name__ == '__main__':
    WT = WireTap()
