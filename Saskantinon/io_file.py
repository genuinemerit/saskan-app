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

from os import path, remove, symlink, system
from pathlib import Path
from pprint import pprint as pp  # noqa: F401

from io_shell import ShellIO  # type: ignore

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
        self.S = self.get_schema("svc_schema")
        self.S = self.S | self.get_schema("saskan_geo")
        self.S = self.S | self.get_schema("saskan_space")
        self.S = self.S | self.get_schema("saskan_time")

    # Read-only methods
    # ==============================================================
    def get_dir(self, p_path: str):
        """Read a directory and return its contents.

        Args:
            p_path: Legit path to directory location.
        Return:
            Directory content (List or None))
        """
        files = None
        try:
            if Path(p_path).exists() and Path(p_path).is_dir():
                files = [f for f in Path(p_path).iterdir()]
            return files
        except Exception as err:
            raise(err)

    def get_file(self, p_path: str):
        """Read in an entire file and return its contents.

        @DEV:
        - Try changing to aiofiles
        - Remove return() logic and make this an async function.
        - Verify success elsewhere.

        Args:
            p_path: Legit path to file location.
        Return:
            File content (Text, Bytes or None))
        """
        content = None
        try:
            if Path(p_path).exists():
                with open(p_path, "r") as f:
                    content = f.read().strip()
                f.close()
            return content
        except Exception as err:
            raise (err)

    def get_configs(self, p_cfg_nm: str):
        """Read configuration data...
        - from shared memory pickle if it exists (full path)
        - else from app space if it exists (path relative to app PY)
        - else from git project JSON file  (path relative to git project)

        Returns: (dict) Config file values or None.
        """
        cfg = None
        try:
            self.D
            self.C
            self.T
            self.G["frame"]
            self.G["windows"]
            self.G["menus"]
            self.G["uri"]
            pk_file = path.join(
                f"{self.D['MEM']}",
                f"{self.D['APP']}",
                f"{self.D['ADIRS']['NS']}",
                f"{self.D['NSDIRS']['CFG']}",
                f"{p_cfg_nm}.pickle",
            )
            cfg = self.unpickle_object(pk_file)
        except (AttributeError, KeyError):
            cfg_file_nm = f"{p_cfg_nm}.json"
            cfg_j = self.get_file(path.join("../config", cfg_file_nm))
            if cfg_j is None:
                cfg_j = self.get_file(path.join("config", cfg_file_nm))
            if cfg_j is not None:
                cfg = json.loads(cfg_j)
        return cfg

    def get_schema(self, p_sch_nm: str):
        """Read schema JSON data...
        - from shared memory pickle if it exists (full path)
        - else from app space if it exists (path relative to app PY)
        - else from git project JSON file  (path relative to git project)

        Returns: (dict) Schema file values or None.
        """
        sch = None
        try:
            self.S
            pk_file = path.join(
                f"{self.D['MEM']}",
                f"{self.D['APP']}",
                f"{self.D['ADIRS']['NS']}",
                f"{self.D['NSDIRS']['ONT']}",
                f"{p_sch_nm}.pickle",
            )
            sch = self.unpickle_object(pk_file)
        except (AttributeError, KeyError):
            sch_file_nm = f"{p_sch_nm}.json"
            sch_j = self.get_file(path.join("../schema", sch_file_nm))
            if sch_j is None:
                sch_j = self.get_file(path.join("schema", sch_file_nm))
            if sch_j is not None:
                sch = json.loads(sch_j)
        return sch

    # CHMOD methods
    # ==============================================================
    def make_readable(self, p_path: str):
        """Make file at path readable for all.

        Args:
            p_path: File to make readable.
        """
        try:
            cmd = f"chmod u=rw,g=r,o=r {p_path}"
            ok, msg = SI.run_cmd(cmd)
            if not ok:
                raise(msg)
        except Exception as err:
            raise(err)

    def make_writable(self, p_path: str):
        """Make file at path writable for all.

        Args:
            p_path: File to make writable.
        """
        try:
            cmd = f"chmod u=rwx,g=rwx,o=rwx {p_path}"
            ok, msg = SI.run_cmd(cmd)
            if not ok:
                raise(msg)
        except Exception as err:
            raise(err)

    def make_executable(self, p_path: str):
        """Make file at path executable for all.

        Args:
            p_path: File to make executable.
        """
        try:
            cmd = f"chmod u=rwx,g=rx,o=rx {p_path}"
            ok, msg = SI.run_cmd(cmd)
            if not ok:
                raise(msg)
        except Exception as err:
            raise(err)

    # Write methods
    # ==============================================================
    def make_dir(self, p_path: str):
        """Create directory at specified location.

        Success if directory already exists.

        Args:
            p_path: Legit path to create dir.
        """
        if not Path(p_path).exists():
            try:
                system(f"mkdir {p_path}")
            except Exception as err:
                raise(err)
        if not Path(p_path).exists():
            raise Exception(f"{p_path} directory creation failed.")

    def delete_file(self, p_path: str):
        """Remove a file.

        Args:
            p_path: Valid path to file to be removed.
        Returns:
            (Status (bool), Message (str or None))
        """
        try:
            remove(p_path)
        except OSError as err:
            raise(err)

    def copy_file(self, p_path_from: str, p_path_to: str):
        """Copy a file to a different location.

        Args:
            p_path_from: path of file to be moved
            p_path_to: destination path
        """
        try:
            shutil.copy(p_path_from, p_path_to)
        except OSError as err:
            raise(err)

    def make_link(self, p_link_from: str, p_link_to: str):
        """Make a symbolic link from the designated file
           at the requested destination.

        Args:
            p_link_from: path of file to be linked from
            p_link_to: destination path of the link
        """
        try:
            symlink(p_link_from, p_link_to)
        except OSError as err:
            raise(err)

    def copy_files(self, p_tgt_dir: str, p_files):
        """Copy from [SRC] to [TGT]/saskan

        Args:
            p_tgt_dir: Legit path to a directory.
            p_files: (Path iterdir object) files to copy.
        """
        for f in p_files:
            if Path(f).is_file():
                file_name = str(f).split("/")[-1]
                tgt_file = path.join(p_tgt_dir, file_name)
                self.copy_file(str(f), tgt_file)

    def append_file(self, p_path: str, p_text: str):
        """Append text to specified text file.

        Create file if it does not already exist.

        Args:
            p_path: Legit path to a text file location.
            p_text: Text to append to the file.
        """

        try:
            f = open(p_path, "a+")
            f.write(p_text)
            f.close()
        except Exception as err:
            raise(err)

    def write_file(self, p_path: str, p_data):
        """Write or overwrite data to specified file.

        Create file if it does not already exist.

        @DEV:
        - Do away with return and make this an async function.
        - Use a separate function to check if file exists.

        Args:
            p_path: Legit path to a file location.
            p_data: Text to append to the file.
        Return:
            (Status (bool), Message (str or None))
        """
        try:
            f = open(p_path, "w+")
            f.write(p_data)
            f.close()
        except Exception as err:
            raise(err)

    def pickle_object(self, p_path: str, p_obj):
        """Pickle an object.

        Args:
            p_path: Legit path to pickled object/file location.
            p_obj (obj): Object to be pickled."""
        try:
            with open(p_path, "wb") as obj_file:
                pickle.dump(p_obj, obj_file)
        except Exception as err:
            raise(err)

    def unpickle_object(self, p_path: str):
        """Unpickle an object.
        Args:
            p_path: Legit path to pickled object location.
        Return:
            Unpickled Object or None"""
        obj = None
        try:
            with open(p_path, "rb") as f:
                obj = pickle.load(f)
        except Exception as err:
            raise(err)
        return obj

    # Special-purpose methods
    # ==============================================================
    def pickle_saskan(self, p_app_dir):
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
