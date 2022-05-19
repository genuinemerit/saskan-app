#!python

"""File IO utilities.

module:    io_file.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>

Add a file delete function.
Use os.remove(path) to delete a file.

Add a file copy function.
Use shutil.copy(from_file, to_file) to copy a file.
"""
import shutil

from os import remove, system
from pathlib import Path

from io_shell import ShellIO       # type: ignore

SI = ShellIO()


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        pass

    def make_readable(self,
                      p_path: str) -> tuple:
        """Make file at path readable for all.

        Args:
            p_path (str): File to make readable.

        Returns:
            (Tuple): (Status (bool), Message (str or None))
        """
        try:
            cmd = f"chmod u=rw,g=r,o=r {p_path}"
            ok, result = SI.run_cmd(cmd)
            if ok:
                return (True, None)
            else:
                return (False, result)
        except Exception as err:
            return (False, err)

    def make_writable(self,
                      p_path: str) -> tuple:
        """Make file at path writable for all.

        Args:
            p_path (str): File to make writable.

        Returns:
            (Tuple): (Status (bool), Message (str or None))
        """
        try:
            cmd = f"chmod u=rwx,g=rwx,o=rwx {p_path}"
            ok, result = SI.run_cmd(cmd)
            if ok:
                return (True, None)
            else:
                return (False, result)
        except Exception as err:
            return (False, err)

    def make_executable(self,
                        p_path: str) -> tuple:
        """Make file at path executable for all.

        Args:
            p_path (str): File to make executable.

        Returns:
            (Tuple): (Status (bool), Message (str or None))
        """
        try:
            cmd = f"chmod u=rwx,g=rx,o=rx {p_path}"
            ok, result = SI.run_cmd(cmd)
            if ok:
                return (True, None)
            else:
                return (False, result)
        except Exception as err:
            return (False, err)

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

    def delete_file(self,
                    p_path: str):
        """Remove a file.

        Args:
            p_path (str): Valid path to file to be removed.
        Returns:
            (Tuple): (Status (bool), Message (str or None))
        """
        try:
            remove(p_path)
            return(True, None)
        except OSError as err:
            return(False, err)

    def copy_file(self,
                  p_path_from: str,
                  p_path_to: str):
        """Copy a file to a different location.

        Args:
            p_path_from (str): path of file to be moved
            p_path_to (str): destination path
        Returns:
            (Tuple): (Status (bool), Message (str or None))
        """
        try:
            shutil.copy(p_path_from, p_path_to)
            return(True, None)
        except OSError as err:
            return(False, err)

    def append_file(self,
                    p_path: str,
                    p_text: str) -> tuple:
        """Append text to specified text file.

        Create file if it does not already exist.

        Args:
            p_path (str): Legit path to a text file location.
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
        """Write or overwrite data to specified file.

        Create file if it does not already exist.

        Args:
            p_path (str): Legit path to a file location.
            p_data (str): Text to append to the file.
            p_file_type (str): default = "w+"
        Return:
            (tuple): (Status (bool), Message (str or None))
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
