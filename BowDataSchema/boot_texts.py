#!python3.9
"""Provision bootstrap text strings for the app.

For internationalization, swap in translated version
of this Class module.  All other texts are defined in
a JSON file and loaded into the Redis "Basement" (0)
database.

module:     boot_texts.py
class:      BootTexts/0
author:     GM <genuinemerit @ pm.me>
"""
import subprocess as shl

from dataclasses import dataclass
from os import path


class BootTexts(object):
    """Static text strings."""

    def __init__(self):
        """Initialize text strings."""
        self.io()

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

    def io(self):
        """Application files, directories, DBs """
        ok, home = self.run_cmd("echo $HOME")
        if not ok:
            print("Failed to find home directory")
            exit(1)

        self.dir_app: str = 'saskan'
        self.dir_home = home.strip()
        self.dir_log: str = 'log'
        self.dir_res: str = 'res'
        self.dir_settings: str = 'settings'

        self.path_app: str = path.join(self.dir_home, self.dir_app)
        self.path_log: str = path.join(self.path_app, self.dir_log)
        self.path_res: str = path.join(self.path_app, self.dir_res)
        self.path_settings: str = path.join(self.path_app, self.dir_settings)

        self.file_widgets: str = path.join(self.path_res, 'config_widgets.json')
        self.trace_level: str = path.join(self.path_settings, 'trace_level.cfg')
        self.log_level: str = path.join(self.path_settings, 'log_level.cfg')
        self.debug_level: str = path.join(self.path_settings, 'debug_level.cfg')

    @dataclass
    class txt:
        """Errors, warnings, help, captions, descriptions, config values"""
        app_desc: str = 'Saskan Eyes - Admin GUI for the whole Ball of Wax'
        no_file: str = 'File not found: '
        err_file: str = 'Error reading config file: '
        refresh_desc: str = 'Force refresh of Basement DB from config files'
        info_desc: str = 'Write info, warning, and error messages to log'
        warn_desc: str = 'Write warning and error messages to log, but not info msgs'
        tracef_desc: str = 'Write trace-level messages to log, without docstrings'
        traced_desc: str = 'Write trace-level messages to log, with docstrings'
        debug_desc: str = 'Write developer debug-level messages to log'
        info_val: str = 'INFO'
        warn_val: str = 'WARN'
        error_val: str = 'ERROR'
        debug_val: str = 'DEBUG'
        nodebug_val: str = 'NODEBUG'
        notrace_val: str = 'NOTRACE'
        tracef_val: str = 'NODOCS'
        traced_val: str = 'DOCS'
