#!python3.9

"""Wire Tap Logging and Monitoring utilities and services.

module:    wire_tap.py
class:     WireTap/0
author:    GM <genuinemerit @ pm.me>
"""

from redis_io import RedisIO                    # type: ignore

RI = RedisIO()


class WireTap(object):
    """Interface to Log and Monitor Redis databases.

    For now, call this class to write to Log or Monitor.
    For now, assume we'll use regular redis_io calls for reads.

    Eventually, create services (maybe) instead of direct calls.
    """

    def __init__(self):
        """Initialize WireTap object."""
        pass

    def write_to_log(self,
                     p_log_rec: dict,
                     p_expire: int = 0):
        """Log records have a specific format.

        Write a record to DB 3 "Log".

        Name: key.
        Value: values use the log record type.
        Audit: values use the audit record type.

        Expire is optional. See notes.
        """
        pass

    def write_to_mon(self,
                     p_mon_rec: dict,
                     p_expire: int = 0):
        """Monitor records have a specific format.

        Write a record to DB 4 "Monitor".

        Name: key.
        Value: values use the monitor record type.
        Audit: values use the audit record type.

        Expire is optional. See notes.
        """
        pass
