#!/usr/bin/python3.9
"""
:module:    io_shell.py
:author:    GM (genuinemerit @ pm.me)

Shell services and utilities.
Service Activator / Deactivator class for Data Schema services.
Generic system command runner.
"""
import hashlib      # generate hash keys
import inspect      # getdoc
import pendulum
import secrets
import subprocess as shl

from os import environ, path, system
from pathlib import Path

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
    def get_datetime(cls) -> object:
        """Get a datetime object in pendulum format, with timezone
           set to US Eastern, for current date/time.
        See: https://pendulum.eustace.io/
        :returns: (str): pendulum datetime object for US East.
        """
        return pendulum.now('America/New_York')

    @classmethod
    def get_iso_time_stamp(cls) -> str:
        """Get a timestamp in ISO 8601 format, with timezone
           set to US Eastern, for current date/time.
        See: https://en.wikipedia.org/wiki/ISO_8601
        e.g. 2023-10-20T11:08:35-04:00
        :returns: (str): Timestamp in ISO 8601 format for US East.
        """
        return pendulum.now('America/New_York').to_iso8601_string()

    @classmethod
    def get_date_string(cls,
                        p_date,
                        p_date_format: str = '') -> str:
        """Get a date string in YYYY-MM-DD format.

        Convert to pendulum date-time object if p_date is a string,
        then strip out date only to get a date string in format YYYY-MM-DD.
        Return only the string.

        :args:
        - p_date (str or pendulum object): Date string to convert, or
          pendulum date object.
        - p_date_format (str): Optional. Format of incoming string,
          eg. "MM/DD/YYYY"  If None, p_date must be pendulum date object.
        :returns:
        - (str): date string in YYYY-MM-DD format.
        """
        if p_date_format not in ('', None):
            p_date = pendulum.from_format(p_date, p_date_format)
        return p_date.to_date_string()

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
    def run_cmd(cls,
                cmd: str) -> tuple:
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
            # trunk-ignore(bandit/B602)
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

    @classmethod
    def run_nohup_py(cls,
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
            # trunk-ignore(bandit/B605)
            system(cmd)
        except Exception as err:
            raise Exception(f"{err} {cmd}")

    @classmethod
    def get_os_home(cls) -> str:
        """Get the home directory.
        This returns the home directory of the user running the program.
        If process is running under sudo, return the root home directory.

        :returns:
            str: home directory
        """
        return environ['HOME']

    @classmethod
    def get_cwd_home(cls) -> str:
        """Derive the home directory from the current working directory.
        For example, if current working directory is: /home/david/homefinance
        then home directory is returned as: /home/david
        even if the program is running under sudo.

        :returns:
            str: home directory
        """
        return path.join("/home", Path.cwd().parts[2])

    @classmethod
    def help(cls,
             p_class_obj: object,
             p_command: str):
        """
        Display docstring for a specific method within a class.

        :args:
        - p_class_obj: An instantiated class object.
        - p_command: The command for which to display help.
        """
        method = getattr(p_class_obj, p_command, None)
        if method:
            print(inspect.getdoc(method))
        else:
            print(f"Command '{p_command}' not found.")

    @classmethod
    def continue_prompt(cls):
        """Prompt user to continue or stop.
        :returns:
        - response (str) User response to prompt.
        """
        response = ''
        while response not in ('y', 'n'):
            response = input('Continue? (y/n): ')
        return response

    def rpt_running_jobs(self,
                         p_job_nm: str):
        """Return display of running jobs matching grep param."""
        ok, result = self.run_cmd(f"ps -ef | grep {p_job_nm}")
        if not ok:
            raise Exception(f"{result}")
        running_jobs = result.split("\n")
        return (result, running_jobs)

    def kill_jobs(self,
                  p_job_nm: str):
        """Kill jobs matching job name param.
        """
        _, running_jobs = SR.rpt_running_jobs(p_job_nm.strip())
        for job in running_jobs:
            job_pid = job.split()[1].strip()
            _, _ = self.run_cmd(f"kill -9 {job_pid}")
