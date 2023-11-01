#!/usr/bin/python3.9
"""
:module:    io_shell.py
:author:    GM (genuinemerit @ pm.me)
Service Activator / Deactivator class for Data Schema services.
It also has a generic system command runner for cases when
we do want to get feedback from the shell and not use nohup.

Not sure if this will work anywhere but Linux. Probably not.
"""
import hashlib      # generate hash keys
import os
import pendulum
import secrets

import subprocess as shl

from saskan_report import SaskanReport  # type: ignore

SR = SaskanReport()


class ShellIO(object):
    """Run Controller-related commands."""

    def __init__(self):
        """Initialize the object.
        """
        pass

    @classmethod
    def get_key(cls):
        """Generate a cryptographically strong key.
        """
        key = secrets.token_urlsafe(32)
        return key

    @classmethod
    def get_hash(cls,
                 p_data_in: str) -> str:
        """Create hash of input string, returning UTF-8 hex-string.
           Use SHA-512 by default.
        :args:
        - p_data_in: {str} data to hash
        :returns:
        - {str} hex-string hash key
        """
        v_hash = hashlib.sha512()
        v_hash.update(p_data_in.encode("utf-8"))
        return v_hash.hexdigest()

    @classmethod
    def get_standard_date(cls,
                          p_date_value: str,
                          p_date_format: str) -> tuple:
        """
        Convert to pendulum date-time object, then strip out date only to
        get a date string in format YYYY-MM-DD. Return both the string and
        the date object.

        :args:
        - p_date_value (str): Date string to convert.
        - p_date_format (str): Format of incoming string, eg. "MM/DD/YYYY"
        :returns:
        - (tuple): (Date string, pendulum date-time object)
        """
        pendulum_date = pendulum.from_format(p_date_value, p_date_format)
        string_date = pendulum_date.to_date_string()
        return (string_date, pendulum_date)

    @classmethod
    def run_cmd(cls, cmd):
        """
        Execute a shell command from Python.
        Best to execute scripts using `bash` not `touch`, `.` or `sh`

        :Args:  {list} shell command as a string in a list

        :Return: {tuple} ({boolean} success/failure, {bytes} result)
        """
        cmd_rc = False
        cmd_result = b''  # Stores bytes

        if cmd == "" or cmd is None:
            cmd_rc = False
        else:
            # shell=True means cmd param contains a regular cmd string
            shell = shl.Popen(cmd, shell=True,
                              stdin=shl.PIPE, stdout=shl.PIPE,
                              stderr=shl.STDOUT)
            cmd_result, _ = shell.communicate()
            if 'failure'.encode('utf-8') in cmd_result or\
                    'fatal'.encode('utf-8') in cmd_result:
                cmd_rc = False
            else:
                cmd_rc = True
        return (cmd_rc, cmd_result.decode('utf-8').strip())

    def kill_jobs(self,
                  p_job_nm: str):
        """Kill jobs matching job name param.
        """
        _, running_jobs = SR.rpt_running_jobs(p_job_nm.strip())
        for job in running_jobs:
            job_pid = job.split()[1].strip()
            _, _ = self.run_cmd(f"kill -9 {job_pid}")

    def run_nohup_py(self,
                     pypath,
                     logpath,
                     p1, p2, p3,
                     log_nm):
        """Run a python script in the background (no hangup),
        sending all output to a log file at logpath and named
        like logpath + p1, where p1 is the first param passed.

        p1, p2, p3 are the parameters to be passed to python script.
        This works for firing up a server module.
        May need tweaking to handle other cases.
        """
        cmd = ("nohup python -u " +
               f"{pypath} '{p1}' {p2} {p3} > " +
               f"{logpath}/{log_nm}_" +
               f"{p1.replace('/', '_').replace('__', '_')}.log 2>&1 &")
        try:
            os.system(cmd)
        except Exception as err:
            raise Exception(f"{err} {cmd}")
