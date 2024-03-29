#!python3.9

"""File system utilities.

module:    saskan_fileio.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>
"""
from dataclasses import dataclass
from os import path
from pathlib import Path
import subprocess as shl


class FileIOUtils(object):
    """File system utilities."""

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

    def get_home(self) -> str:
        """Get name of the user's home directory.

        Returns:
            str: path to $HOME
        """
        result = self.run_cmd("echo $HOME")
        return result[1]


class FileIOTexts(object):
    """Texts used in FileIO"""

    @dataclass
    class path:
        """File and database names and location."""
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
            self.UT.run_cmd("mkdir {}".format(p_path))
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

    # Special-purpose methods (maybe move to an io_data class?)
    # ==============================================================
    def pickle_saskan(self, p_app_dir):
        """Set up shared memory directories for saskan app.
        Pickle saskan files to shared memory.
        Don't worry about pickling or optimizing in memory for now.

        :Args:
        - p_app (path): Path to Saskan app directory
        """

        def create_sub_dir(sub_dir):
            """Create shared memory directories for saskan app.
            - shared mem app sub dirs
            - shared mem data sub dirs
            """
            self.make_dir(sub_dir)
            self.make_writable(sub_dir)

        def create_mem_dirs():
            """Wipe out shared memory data dirs if they exist.
            Create shared memory directories for saskan app.
            - shared mem parent dir
            - shared mem app sub dirs
            - shared mem data sub dirs
            """
            app_d = path.join(self.D["MEM"], self.D["APP"])
            files = self.get_dir(app_d)
            if files is not None:
                app_files = app_d + "/*"
                ok, result = SI.run_cmd([f"rm -rf {app_files}"])
                if ok:
                    ok, result = SI.run_cmd([f"rmdir {app_d}"])
                else:
                    raise Exception(f"{self.T['err_process']} {result}")
            self.make_dir(app_d)
            self.make_writable(app_d)
            for _, sd in self.D["ADIRS"].items():
                create_sub_dir(path.join(app_d, sd))
            for _, dd in self.D["NSDIRS"].items():
                create_sub_dir(path.join(app_d, self.D["ADIRS"]["SAV"], dd))

        def pickle_config_and_schema_objects(p_app_dir):
            """Pickle dict versions of config and schema json files.

            @DEV:
            - Pickle or copy any other files to shared memory? images?
            - Is it really necessary to pickle ontology/schema files?
            """
            for j_dir in (self.D["ADIRS"]["CFG"], self.D["ADIRS"]["ONT"]):
                the_dir = path.join(p_app_dir, j_dir)
                files = self.get_dir(the_dir)
                for f in files:
                    if Path(f).is_file():
                        file_nm = str(f).split("/")[-1]
                        if file_nm.endswith(".json"):
                            the_dir = path.join(
                                self.D["MEM"],
                                self.D["APP"],
                                j_dir,
                                file_nm.replace(".json", ".pickle"),
                            )
                            j_data = self.get_file(f)
                            self.pickle_object(
                                the_dir, json.loads(j_data)
                            )

        # pickle_saskan() main
        # ====================
        create_mem_dirs()
        pickle_config_and_schema_objects(p_app_dir)