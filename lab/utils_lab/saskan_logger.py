#!python3.9

"""Write log records to file using standard python logging methods.

module:     saskan_logger.py
class:      Logger/2
author:     GM <genuinemerit @ pm.me>
"""
import logging
from collections import namedtuple
from copy import copy
from dataclasses import dataclass
from pprint import pprint as pp  # noqa: F401

import arrow


class LoggerTexts(object):
    """Data classes for Logger"""

    @dataclass
    class ms:
        """Messages and Labels."""

        start_sess: str = "\n== Log Session started"
        unv_tm: str = "\n== Universal Time: "

    @dataclass
    class log:
        """Define valid logging levels."""

        CRITICAL: int = 50
        FATAL: int = 50
        ERROR: int = 40
        WARNING: int = 30
        NOTICE: int = 20
        INFO: int = 20
        DEBUG: int = 10
        NOTSET: int = 0

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

    @dataclass
    class tz:
        """Time zone values."""
        UTC: str = 'UTC'


class LoggerUtils(object):
    """Generic utilities cloned from Utils class"""

    @classmethod
    def get_dttm(cls):
        """Get date and time values.

        Returns:
            namedtuple
            - .curr_utc {string} UTC date time (YYYY-MM-DD HH:mm:ss.SSSSS ZZ)
            - .next_utc {string} UTC date time plus 1 day
            - .curr_ts  {string} UTC time stamp (YYYYMMDDHHmmssSSSSS)
        """
        long_format = 'YYYY-MM-DD HH:mm:ss.SSSSS ZZ'
        dttm = namedtuple("dttm", "curr_utc next_utc curr_ts")
        utc_dttm = arrow.utcnow()
        dttm.curr_utc = str(utc_dttm.format(long_format))
        dttm.next_utc = str(utc_dttm.shift(days=+1).format(long_format))
        dttm.curr_ts = dttm.curr_utc.strip()
        for rm in [' ', ':', '+', '.', '-']:
            dttm.curr_ts = dttm.curr_ts.replace(rm, '')
        dttm.curr_ts = dttm.curr_ts[0:-4]
        return dttm


class Logger(object):
    """Generic logging functions for use with logging module."""

    def __init__(self,
                 p_log_file: str,
                 p_log_level: int = 0):
        """Initialize the Logger class.

        Create a new log file if one does not already exist.

        Args:
            p_log_file (path): full path to log file location
            p_log_level (int, optional):
                A valid log level value. Defaults to NOTSET (= 0).
        """
        self.LOGLEVEL = p_log_level
        self.LOGFILE = p_log_file
        self.TX = LoggerTexts()
        self.UT = LoggerUtils()
        app_dttm = copy(self.UT.get_dttm())
        text = self.TX.ms.start_sess
        text += "\n{}{} ({})\n".format(
            self.TX.ms.unv_tm, app_dttm.curr_utc, self.TX.tz.UTC)
        try:
            f = open(self.LOGFILE, 'a+')
            f.write(text)
            f.close()
        except Exception as err:
            pp((False, str(err)))

    def set_log(self):
        """Set log level, log formatter and log outputs. Initiates log handling.

        Assumes that LOGLEVEL and LOGFILE have been set correctly.
        """
        self.log = logging.getLogger()
        self.log.setLevel(self.LOGLEVEL)
        # `asctime` pulls localhost timezone time.
        msg_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(msg_format)
        logF = logging.FileHandler(self.LOGFILE)
        logF.setLevel(self.LOGLEVEL)
        logF.setFormatter(formatter)
        self.log.addHandler(logF)

    def write_log(self,
                  p_msg_level: int,
                  p_msg_text: str):
        """Write message at designated level.

        Args:
            p_msg_level (self.TX.log -> int): Valid log level value
            p_msg_text (string): Content of the message to log
        """
        if p_msg_level in (self.TX.log.CRITICAL, self.TX.log.FATAL):
            logging.fatal(p_msg_text)
        elif p_msg_level == self.TX.log.ERROR:
            logging.error(p_msg_text)
        elif p_msg_level == self.TX.log.WARNING:
            logging.warning(p_msg_text)
        elif p_msg_level in (self.TX.log.NOTICE, self.TX.log.INFO):
            logging.info(p_msg_text)
        elif p_msg_level == self.TX.log.DEBUG:
            logging.debug(p_msg_text)
        else:
            logging.debug(p_msg_text)

    def close_log(self):
        """Close log handlers. Terminate log handling."""
        for handler in self.log.handlers:
            handler.close()
            self.log.removeFilter(handler)
