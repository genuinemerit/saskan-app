#!python
"""
:module:    saskan_report.py
:author:    GM (genuinemerit @ pm.me)
Saskan Admin Report Generator

@DEV:
- Consider whether it makes sense to move Analysis
  reporting functions to this module.
"""

# import sys
import subprocess as shl

# from dataclasses import dataclass
# from os import path
# from pathlib import Path
from pprint import pprint as pp     # noqa: F401

# from io_file import FileIO          # type: ignore
# from io_shell import ShellIO        # type: ignore
# from io_wiretap import WireTap      # type: ignore

# FI = FileIO()
# SI = ShellIO()
# WT = WireTap()


# ====================================================
#  SASKAN REPORT
# ====================================================
class SaskanReport(object):
    """Provide report and monitoring methods for Saskan Admin.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        """
        pass

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

    def rpt_ufw_status(self):
        """Get UFW status.
        """
        ok, result = self.run_cmd("ufw status numbered")
        if ok:
            return result

    def rpt_jobs(self,
                 p_job_nm: str):
        """Return display of running jobs matching grep param."""
        ok, result = self.run_cmd(f"ps -ef | grep {p_job_nm}")
        if not ok:
            raise Exception(f"{result}")
        running_jobs = result.split("\n")
        return (result, running_jobs)
