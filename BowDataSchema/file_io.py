#!python3.9

"""File IO utilities.

module:    file_io.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>
"""
from dataclasses import dataclass
from os import path
from os import system
from pathlib import Path


class FileIOUtils(object):
    """File system utilities."""

    def get_home(self) -> str:
        """Get name of the user's home directory.

        Move this to redis_io.py

        Instead of hardcoding to user's $HOME, use a Redis Basement
        config setting to store location of  app "Home" directory.

        Returns:
            str: path to $HOME
        """
        # result = self.run_cmd("echo $HOME")
        # return result[1]
        pass


class FileIOTexts(object):
    """Texts used in FileIO"""

    @dataclass
    class path:
        """File and database names and location.

        Use Redis Basement to load constants and texts.
        """
        app_dir: str = 'saskan'  # expected to reside in home directory
        log_dir: str = 'log'
        db_status_file: str = 'db_status'

    @dataclass
    class ew:
        """Error and warning messages."""
        bad_path: str = "Path could not be reached: "


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        self.FI = FileIOTexts()
        self.UT = FileIOUtils()
        self.APP = path.join(self.UT.get_home(), self.FI.path.app_dir)

    def make_dir(self,
                 p_path: str) -> tuple:
        """Create directory at specified location.

        Success if directory already exists.

        Args:
            p_path (str): Legit path to create dir.
        Return:
            (tuple): (Status (bool), Message (str or None))
        """

        if not Path(p_path).exists():
            system(f"mkdir {p_path}")
        if Path(p_path).exists():
            return (True, None)
        else:
            return (False, "{}{}".format(self.FI.ew.bad_path, p_path))

    def append_file(self,
                    p_path: str,
                    p_text: str) -> tuple:
        """Append text to specified file.

        Create file if it does not already exist.

        Args:
            p_path (str): Legit path to a file location.
            p_text (str): Text to append to the file.
        Return:
            (tuple): (Status (bool), Message (str or None))
        """

        try:
            f = open(p_path, 'a+')
            f.write(p_text)
            f.close()
        except Exception as err:
            return (False, err)
        return (True, None)

    def write_file(self,
                   p_path: str,
                   p_text: str) -> tuple:
        """Write or overwrite text to specified file.

        Create file if it does not already exist.
        Overwrite file if it does already exist.

        Args:
            p_path (str): Legit path to a file location.
            p_text (str): Text to append to the file.
        Return:
            (tuple): (Status (bool), Message (str or None))
        """

        try:
            f = open(p_path, 'w+')
            f.write(p_text)
            f.close()
        except Exception as err:
            return (False, err)
        return (True, None)

    def get_file(self,
                 p_path: str) -> tuple:
        """Read in an entire file and return ites contents.

        Args:
            p_path (str): Legit path to file location.
        Return
            (Tuple): (Status (bool), Message (text or None),
                      File content (Text, Bytes or None))
        """
        content = None
        try:
            if Path(p_path).exists():
                with open(p_path, "r") as f:
                    content = f.read().strip()
                f.close()
                return (True, None, content)
            else:
                return (False, None, None)
        except Exception as err:
            return (False, err, None)

    def get_db_status(self) -> tuple:
        """Check token regarding persisted db status.

        Remove token file or set it to 'INCOMPLETE' to force
            rebuild of the database file.
        Move this function to redis_io.py

        Return:
            tuple (Status, Message, db_status_value)
        """
        file_path = path.join(
            self.APP, self.FI.path.log_dir, self.FI.path.db_status_file)
        ok, msg, db_status = self.get_file(file_path)
        if ok:
            return(ok, None, db_status)
        else:
            return(ok, msg, "INCOMPLETE")

    def set_db_status(self,
                      p_status: str) -> tuple:
        """Overwrite token holding persisted db status.
        Move this function to redis_io.py

        Args:
            p_status (str): Status value to write to token file.

        Return:
            tuple (Status, Message)
        """
        ok, msg = self.write_file(
            path.join(
                self.APP, self.FI.path.log_dir, self.FI.path.db_status_file),
            p_status)
        if ok:
            return(ok, None)
        else:
            return(ok, msg)
