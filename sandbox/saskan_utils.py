#!python3.9
"""
:module:    saskan_utils.py
:class:     Utils

Global constants and generic helper functions.

:author:    GM <genuinemerit @ pm.me>
"""
import hashlib
import secrets
import subprocess as shl
from collections import namedtuple
from pprint import pprint as pp  # noqa: F401

import arrow


class Utils(object):
    """
    Generic static methods.
    Functions for common tasks.
    """

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

    @classmethod
    def get_hash(cls, p_str):
        """
        Create a hash of the input string, returning a UTF-8 hex-string.

        :Args:
            - {string} to be hashed

        :Return: {string} UTF-8-encoded, 64-byte hash of input argument
        """
        v_hash = str()
        # v_hash = hashlib.sha512() # <-- produces a 128-byte hash
        v_hash = hashlib.sha256()
        v_hash.update(p_str.encode("utf-8"))
        return v_hash.hexdigest()

    @classmethod
    def list_ports(cls, p_ports_config, p_class_name):
        """
        Return valid ports for selected class, based on config setting

        :Attr:
            - {string} like "ClassName:PortNum:PortNum ..(bis).."
              or "ClassName:PortNum .." if only one port
            - {string} class name to return ports for

        :Return: {list} of integers
        """
        ports = list()
        app_ports = list()
        if ' ' in p_ports_config:
            app_ports = p_ports_config.split(' ')
        else:
            app_ports.append(p_ports_config)
        for apport in app_ports:
            a_port = apport.split(':')
            if a_port[0] == p_class_name:
                if len(apport) == 2:
                    ports.append(a_port[1])
                else:
                    port_cnt = (int(a_port[2]) - int(a_port[1])) + 1
                    for pc in range(0, port_cnt):
                        ports.append(int(a_port[1]) + pc)
        return ports

    @classmethod
    def pluralize(cls, singular):
        """
        Return the plural form of the singular English word.

        :Args:  {string} singular English noun

        :Return:  {string} plural version of the noun
        """
        plural = singular
        if not singular or singular.strip() == ''\
            or singular[-2:] in ('es', 'ds', 'ts', 'ms', 'hs', 'ps')\
                or singular == 'stuff':
            pass
        elif singular[-1:] in ('s', 'x') or singular[-2:] in ('ch'):
            plural = singular + "es"
        elif singular[-2:] == 'ey':
            plural = singular[:-2] + "ies"
        elif singular[-1:] == 'y':
            plural = singular[:-1] + "ies"
        else:
            plural = singular + "s"
        return plural

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

    def exec_bash(self, cmd_list):
        """
        Run a series of (one or more) OS commands, displaying results to log

        :Args: {list} of strings formatted correctly as OS commands

        :Return: {string} decoded message from last command in list
        """
        for cmd in cmd_list:
            _, result = self.run_cmd(cmd)
        return result

    def get_var(self, p_varnm):
        """
        Retrieve value of an environment variable.

        :Args: {string} name of environment variable

        :Return: {tuple} (string, string)
            - (name of requested var, value of requested var or empty string)
        """
        retval = tuple()
        (rc, rslt) = self.run_cmd("echo $" + p_varnm)
        if rc:
            retval = (p_varnm, rslt.decode('UTF-8')[0:-1])
        else:
            retval = (p_varnm, '')
        return retval

    def get_uid(self, p_uid_length: int = None) -> str:
        """Generate a URL-safe, cryptographically strong random value.

        A unique ID for any purpose, such as unique PK for a data record.

        Args:
            p_uid_length (integer, optional): Desired length of the key.
                Default is 32. Minimum is 32.

        Returns:
            string: the unique ID value as a string
        """
        p_uid_length = 32 if p_uid_length is None else p_uid_length
        p_uid_length = 32 if p_uid_length < 32 else p_uid_length
        uid_val = secrets.token_urlsafe(p_uid_length)
        return uid_val

    def get_home(self) -> str:
        """Get name of the user's home directory.

        Returns:
            str: path to $HOME
        """
        result = self.run_cmd("echo $HOME")
        return result[1]
