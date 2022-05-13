#!python

"""File IO utilities.

module:    io_file.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>

Add a file delete function.
Use os.remove() to delete a file.
"""
# from os import path
from os import system
from pathlib import Path


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        pass

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
            return (False, "directory creation failed.")

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
                   p_data,
                   p_file_type: str = "w+") -> tuple:
        """Write or overwrite text to specified file.

        Create file if it does not already exist.
        Overwrite file if it does already exist.

        Args:
            p_path (str): Legit path to a file location.
            p_data (str): Text to append to the file.
            p_file_type (str): default = "w+"
        Return:
            (tuple): (Status (bool), Message (str or None))

        Hmmm... doesn't seem to be overwriting... Not sure why.
        Make need to check for existing file, then delete it?
        """

        try:
            f = open(p_path, p_file_type)
            f.write(p_data)
            f.close()
        except Exception as err:
            return (False, err)
        return (True, None)

    def get_dir(self,
                p_path: str) -> tuple:
        """Read a directory and return its contents.

        Args:
            p_path (str): Legit path to directory location.
        Return
            (Tuple): (Status (bool), Message (text or None),
                      Directory content (List or None))
        """
        try:
            if Path(p_path).exists() and Path(p_path).is_dir():
                files = [f for f in Path(p_path).iterdir()]
                return (True, None, files)
            else:
                return (False, "not found", None)
        except Exception as err:
            return (False, err, None)

    def get_file(self,
                 p_path: str,
                 p_file_type: str = "r") -> tuple:
        """Read in an entire file and return its contents.

        Args:
            p_path (str): Legit path to file location.
            p_file_type (str): default = "r"
        Return
            (Tuple): (Status (bool), Message (text or None),
                      File content (Text, Bytes or None))
        """
        content = None
        try:
            if Path(p_path).exists():
                with open(p_path, p_file_type) as f:
                    content = f.read().strip()
                f.close()
                return (True, None, content)
            else:
                return (False, "not found", None)
        except Exception as err:
            return (False, err, None)
