#!python
"""Provision bootstrap text strings for the app.

For internationalization, swap in translated version
of this Class module.  All other texts are defined in
a JSON file and loaded into the Redis "Basement" (0)
database.

module:     io_boot.py
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
        self.dir_bin: str = 'bin'
        self.dir_cfg: str = 'cfg'
        self.dir_res: str = 'res'

        self.path_app: str = path.join(self.dir_home, self.dir_app)
        self.path_bin: str = path.join(self.path_app, self.dir_bin)
        self.path_cfg: str = path.join(self.path_app, self.dir_cfg)
        self.path_res: str = path.join(self.path_app, self.dir_res)
        self.path_usr_bin: str = '/usr/local/bin'

        self.file_widgets: str = path.join(
            self.path_res, 'config_widgets.json')
        self.trace_level: str = path.join(
            self.path_cfg, 'trace_level.cfg')
        self.log_level: str = path.join(
            self.path_cfg, 'log_level.cfg')
        self.debug_level: str = path.join(
            self.path_cfg, 'debug_level.cfg')

    @dataclass
    class txt:
        """Errors, warnings, help, captions, descriptions, config values"""
        desc_cfg_files: str = 'Configure BoW files, directories, binaries'
        desc_cfg_meta: str = 'Configure BoW metadata'
        desc_debug: str = 'Write developer debug-level messages to log'
        desc_info: str = 'Write info, warning, and error messages to log'
        desc_refresh: str = 'Force refresh of Basement DB from config files'
        desc_saskan_eyes: str = 'Saskan Eyes - Admin GUI for whole Ball of Wax'
        desc_source: str = 'Location of cloned bow-data-schema repo'
        desc_traced: str = 'Write trace-level msgs to log, w/ docstrings'
        desc_tracef: str = 'Write trace-level msgs to log, w/o docstrings'
        desc_warn: str = 'Write warning, error messages to log, not info msgs'
        file_error: str = 'Bad file or directory: '
        file_ok: str = 'File or directory exists: '
        process_error: str = 'Process aborted: '
        val_debug: str = 'DEBUG'
        val_error: str = 'ERROR'
        val_info: str = 'INFO'
        val_nodebug: str = 'NODEBUG'
        val_notrace: str = 'NOTRACE'
        val_traced: str = 'DOCS'
        val_tracef: str = 'NODOCS'
        val_warn: str = 'WARN'
