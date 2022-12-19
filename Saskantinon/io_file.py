#!python

"""File IO utilities.

module:    io_file.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>

@DEV:
- Use services instead of direct calls, as doable.
"""
import json
import pickle
import shutil

from os import path, remove, system
from pathlib import Path
from pprint import pprint as pp

from io_shell import ShellIO       # type: ignore

SI = ShellIO()


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        self.D = self.get_configs("d_dirs")
        self.C = self.get_configs("c_context")
        self.T = self.get_configs(f"t_texts_{self.C['lang']}")
        self.G = self.get_configs("g_frame")
        self.G = self.G | self.get_configs("g_menus")
        self.G = self.G | self.get_configs("g_windows")
        self.G = self.G | self.get_configs("g_uri")

    # Read-only methods
    # ==============================================================
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
                 p_path: str) -> tuple:
        """Read in an entire file and return its contents.

        @DEV:
        - Try changing to aiofiles
        - Remove return() logic and make this an async function.
        - Verify success elsewhere.

        Args:
            p_path (str): Legit path to file location.
        Return
            (Tuple): (Status (bool),
                      Message (text or None),
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
                return (False, "not found", None)
        except Exception as err:
            return (False, err, None)

    def get_configs(self,
                    p_cfg_nm: str) -> dict:
        """"Read configuration data...
        - from shared memory pickle if it exists (full path)
        - else from app space if it exists (path relative to app PY)
        - else from git project JSON file  (path relative to git project)

        Returns: (dict) Directory values or exception.
        """
        try:
            self.D
            self.C
            self.T
            self.G['frame']
            self.G['windows']
            self.G['menus']
            self.G['uri']
            pk_file = path.join(f"{self.D['MEM']}",
                                f"{self.D['APP']}",
                                f"{self.D['ADIRS']['NS']}",
                                f"{self.D['NSDIRS']['CFG']}",
                                f"{p_cfg_nm}.pickle")
            _, _, cfg = self.unpickle_object(pk_file)
        except (AttributeError, KeyError):
            cfg_file_nm = f"{p_cfg_nm}.json"
            ok, err, cfg_j =\
                self.get_file(path.join("../data/config", cfg_file_nm))
            if not ok:
                ok, err, cfg_j =\
                    self.get_file(path.join("config", cfg_file_nm))
                if not ok:
                    raise Exception(f"Error reading config file: {err}")
            cfg = json.loads(cfg_j)
        return (cfg)

    # CHMOD methods
    # ==============================================================
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

    # Write methods
    # ==============================================================
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
            return (True, None)
        except OSError as err:
            return (False, err)

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
            return (True, None)
        except OSError as err:
            return (False, err)

    def copy_files(self,
                   p_tgt_dir: str,
                   p_files):
        """Copy from [SRC] to [TGT]/saskan

        Args:
            p_tgt_dir (str): Legit path to a directory.
            p_files: List of files (from Path iterdir object) to copy.
        """
        for f in p_files:
            if Path(f).is_file():
                file_name = str(f).split("/")[-1]
                tgt_file = path.join(p_tgt_dir, file_name)
                ok, err = self.copy_file(str(f), tgt_file)
                if not ok:
                    raise Exception(
                        f"{self.T['err_file']} {tgt_file} {err}")

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
                   p_data) -> tuple:
        """Write or overwrite data to specified file.

        Create file if it does not already exist.

        @DEV:
        - Do away with return and make this an async function.
        - Use a separate function to check if file exists.

        Args:
            p_path (str): Legit path to a file location.
            p_data (str): Text to append to the file.
        Return:
            (tuple): (Status (bool), Message (str or None))
        """
        try:
            f = open(p_path, "w+")
            f.write(p_data)
            f.close()
        except Exception as err:
            return (False, err)
        return (True, None)

    def pickle_object(self,
                      p_path: str,
                      p_obj):
        """Pickle an object.

        Args:
            p_path (str): Legit path to pickled object location.
            p_obj (obj): Object to be pickled.
        Return:
            (tuple): (Status (bool),
                      Message (str or None))"""
        ok = True
        msg = None
        try:
            with open(p_path, 'wb') as obj_file:
                pickle.dump(p_obj, obj_file)
        except Exception as err:
            msg = err
            ok = False
        return (ok, msg)

    def unpickle_object(self,
                        p_path: str):
        """Unpickle an object.
        Args:
            p_path (str): Legit path to pickled object location.
        Return:
            (tuple): (Status (bool),
                      Message (str or None)),
                      Object (obj or None))"""
        ok = True
        msg = None
        obj = None
        try:
            with open(p_path, 'rb') as f:
                obj = pickle.load(f)
        except Exception as e:
            msg = e
            ok = False
        return (ok, msg, obj)

    # Special-purpose methods
    # ==============================================================
    def pickle_saskan(self,
                      p_app_dir):
        """Set up shared memory directories for saskan app.
        Pickle saskan files to shared memory.

        :Args:
        - p_app (path): Path to Saskan app directory
        """
        def create_sub_dir(sub_dir):
            """Create shared memory directories for saskan app.
            - shared mem app sub dirs
            - shared mem data sub dirs
            """
            ok, result = self.make_dir(sub_dir)
            if ok:
                ok, result = self.make_writable(sub_dir)
            if not ok:
                raise Exception(f"{self.T['err_file']} {sub_dir} {result}")

        def create_mem_dirs():
            """Wipe out shared memory data dirs if they exist.
            Create shared memory directories for saskan app.
            - shared mem parent dir
            - shared mem app sub dirs
            - shared mem data sub dirs
            """
            app_d = path.join(self.D["MEM"], self.D["APP"])
            ok, result, _ = self.get_dir(app_d)
            if ok:
                app_files = app_d + "/*"
                ok, result = SI.run_cmd([f"rm -rf {app_files}"])
                if ok:
                    ok, result = SI.run_cmd([f"rmdir {app_d}"])
                else:
                    raise Exception(f"{self.T['err_process']} {result}")
            ok, result = self.make_dir(app_d)
            if ok:
                ok, result = self.make_writable(app_d)
            if not ok:
                raise Exception(f"{self.T['err_file']} {app_d} {result}")
            for _, sd in self.D["ADIRS"].items():
                create_sub_dir(path.join(app_d, sd))
            for _, dd in self.D["NSDIRS"].items():
                create_sub_dir(path.join(app_d, self.D['ADIRS']['SAV'], dd))

        def pickle_config_and_schema_objects(p_app_dir):
            """Pickle dict versions of config and schema json files.

            @DEV:
            - Pickle or copy any other files to shared memory? images?
            """
            for j_dir in (self.D['ADIRS']['CFG'], self.D['ADIRS']['ONT']):
                src_dir = path.join(p_app_dir, j_dir)
                ok, err, files = self.get_dir(src_dir)
                if not ok:
                    raise Exception(f"{self.T['err_file']} {src_dir} {err}")
                for f in files:
                    if Path(f).is_file():
                        file_nm = str(f).split("/")[-1]
                        if file_nm.endswith(".json"):
                            mem_file = path.join(
                                self.D['MEM'], self.D['APP'], j_dir,
                                file_nm.replace(".json", ".pickle"))
                            _, _, j_data = self.get_file(f)
                            ok, err = self.pickle_object(
                                    mem_file, json.loads(j_data))
                            if not ok:
                                raise Exception(
                                    f"{self.T['err_file']} {mem_file} {err}")
        # pickle_saskan() main
        # ====================
        create_mem_dirs()
        pickle_config_and_schema_objects(p_app_dir)
