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

from io_shell import ShellIO

SI = ShellIO()


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        self.D = self.get_config("d_dirs")
        self.C = self.get_config("c_context")
        self.T = self.get_config(f"t_texts_{self.C['lang']}")
        self.G = self.get_config("g_frame")
        self.G = self.G | self.get_config("g_menus")
        self.G = self.G | self.get_config("g_windows")
        self.G = self.G | self.get_config("g_uri")
        self.S = self.get_schema("svc_schema")
        self.S = self.S | self.get_schema("saskan_geo")
        self.S = self.S | self.get_schema("saskan_astro")
        self.S = self.S | self.get_schema("saskan_time")

    # Read methods
    # ==============================================================
    @classmethod
    def get_dir(cls, p_path: str):
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

    @classmethod
    def get_file(self, p_path: str):
        """Read in an entire file and return its contents.

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

    @classmethod
    def get_json_file(cls,
                      p_path: str):
        """Read in an entire JSON file and return its contents as dict.

        Args:
            p_path (str): Legit path to JSON file location.
        Return
            File content (Dict or None)
        """
        content = None
        try:
            content = json.loads(cls.get_file(p_path))
            return content
        except Exception as err:
            raise (err)

    @classmethod
    def get_pickle(cls,
                   p_path: str):
        """Unpickle an object.
        Args:
            p_path: Legit path to pickled object location.
        Return:
            Unpickled Object or None
        """
        obj = None
        try:
            with open(p_path, "rb") as f:
                obj = pickle.load(f)
        except Exception as err:
            raise (err)
        return obj

    def get_config(self, p_cfg_nm: str):
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

    # Write methods
    # ==============================================================
    @classmethod
    def make_dir(cls, p_path: str):
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

    @classmethod
    def delete_file(cls, p_path: str):
        """Remove a file.

        Args:
            p_path: Valid path to file to be removed.
        """
        try:
            remove(p_path)
        except OSError as err:
            raise(err)

    @classmethod
    def copy_one_file(cls,
                      p_path_from: str,
                      p_path_to: str):
        """Copy one file from source to target.

        Args:
            p_path_from (str): full path of file to be moved
            p_path_to (str): destination path
        """
        try:
            shutil.copy2(p_path_from, p_path_to)
        except OSError as err:
            raise (err)

    @classmethod
    def copy_all_files(cls,
                       p_path_from: str,
                       p_path_to: str):
        """Copy all files in dir from source to target.

        Args:
            p_path_from (str): full path of a dir with files to be moved
            p_path_to (str): destination path
        """
        try:
            cmd = f"cp -rf {p_path_from}/* {p_path_to}"
            ok, msg = SI.run_cmd(cmd)
            if not ok:
                raise (msg)
        except Exception as err:
            raise (err)

    @classmethod
    def make_link(cls,
                  p_link_from: str,
                  p_link_to: str):
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

    @classmethod
    def append_file(cls,
                    p_path: str,
                    p_text: str):
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

    @classmethod
    def write_file(cls,
                   p_path: str,
                   p_data,
                   p_file_type: str = "w+"):
        """Write or overwrite data to specified file.
        Create file if it does not already exist.

        Args:
            p_path: Legit path to a file location.
            p_data: Text to append to the file.
            p_file_type (str): default = "w+"
        """
        try:
            f = open(p_path, p_file_type)
            f.write(p_data)
            f.close()
        except Exception as err:
            raise(err)

    @classmethod
    def write_pickle(cls,
                     p_path: str,
                     p_obj):
        """Pickle an object.

        Args:
            p_path: Legit path to pickled object/file location.
            p_obj (obj): Object to be pickled."""
        try:
            with open(p_path, "wb") as obj_file:
                pickle.dump(p_obj, obj_file)
        except Exception as err:
            raise(err)

    # CHMOD methods
    # ==============================================================
    @classmethod
    def make_readable(cls, p_path: str):
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

    @classmethod
    def make_writable(cls, p_path: str):
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

    @classmethod
    def make_executable(cls, p_path: str):
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

    # Analysis methods
    # ==============================================================
    @classmethod
    def diff_files(cls,
                   p_file_a: str,
                   p_file_b: str) -> str:
        """Diff two files and return the result.
        :args:
        - p_file_a (str): full path to file A
        - p_file_b (str): full path to file B
        """
        try:
            cmd = f"diff {p_file_a} {p_file_b}"
            ok, msg = SI.run_cmd(cmd)
            if not ok:
                raise (msg)
            return msg
        except Exception as err:
            raise (err)

    # Special-purpose methods (maybe move to an io_data class?)
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
