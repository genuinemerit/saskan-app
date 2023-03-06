#!/usr/bin/python3.9
"""
:module:    io_shell.py
:author:    GM (genuinemerit @ pm.me)
Service Activator / Deactivator class for Data Schema services.
It also has a generic system command runner for cases when
we do want to get feedback from the shell and not use nohup.

Not sure if this will work anywhere but Linux. Probably not.
"""
import os
# import time

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
