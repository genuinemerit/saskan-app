#!python

"""File IO utilities.

module:    io_file.py
class:     FileIO/0
author:    GM <genuinemerit @ pm.me>
"""
import json
import pickle
import shutil

from os import path, remove, system
from pathlib import Path
# from pprint import pprint as pp

from io_shell import ShellIO       # type: ignore

SI = ShellIO()


class FileIO(object):
    """File IO utilities."""

    def __init__(self):
        """Initialize FileIO object."""
        self.d = self.get_app_and_data_dirs()
        self.c = self.get_context()
        self.t = self.get_static_text()
        self.g = dict()
        g = self.get_gui_frame()
        self.g["frame"] = g["frame"]
        g = self.get_gui_menus()
        self.g["menus"] = g["menus"]

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
                        f"{self.t['err_file']} {tgt_file} {err}")

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

    def get_metadata(self,
                     p_meta_nm: str) -> dict:
        """"Read metadata...
        - from shared memory pickle if it exists (hard-coded path)
        - else from app JSON file if it exists.  (relative path)
        - else from git project JSON file.       (relative path)

        Returns: (dict) Directory values or exception.
        """
        pk_file = path.join("/dev/shm/saskan/data/config",
                            f"{p_meta_nm}.pickle")
        ok, msg, meta = self.unpickle_object(pk_file)
        if not ok:
            ok, msg, meta = self.get_file(
                    path.join("../data/config", f"{p_meta_nm}.json"))
            if ok:
                meta = json.loads(meta)
            else:
                ok, msg, meta =\
                    self.get_file(path.join("config", f"{p_meta_nm}.json"))
                if ok:
                    meta = json.loads(meta)
                else:
                    raise Exception(f"Error reading metadata: {msg}")
        return(meta)

    def get_app_and_data_dirs(self):
        """Read app and data directoriess metadata.
        Returns: (dict) Directory values or exception.
        """
        meta = self.get_metadata("m_directories")
        return(meta)

    def get_context(self):
        """"Read context metadata. For example, application language.
        Returns: (dict) Directory values or exception.
        """
        meta = self.get_metadata("m_context")
        return(meta)

    def get_log_settings(self):
        """Read log settings metadata.
        Returns: (dict) Directory values or exception.
        """
        meta = self.get_metadata("m_log")
        return(meta)

    def get_gui_frame(self):
        """Read GUI frame metadata.
        Returns: (dict) Directory values or exception.
        """
        meta = self.get_metadata("m_gui_frame")
        return(meta)

    def get_gui_menus(self):
        """Read GUI menus metadata.
        Returns: (dict) Directory values or exception.
        """
        meta = self.get_metadata("m_gui_menus")
        return(meta)

    def get_static_text(self):
        """Read static text metadata..
        - from shared memory pickle if it exists (hard-coded path)
        - else from app JSON file if it exists.  (relative path)
        - else from git project JSON file.       (relative path)

        Args: (str) p_lang: Language code.
        Returns: (dict) Text values or exception.
        """
        context = self.get_context()
        meta = self.get_metadata(f"m_texts_{context['lang']}")
        return(meta)

    def pickle_saskan(self):
        """Set up shared memory directories for saskan app and pickle...
        - configs

        @DEV
        Will need to work on how to handle permissions for shared memory
        write and delete.

        Args:
            p_mem (str): Legit path to shared memory location.
        """

        def create_mem_dirs():
            """Wipe out shared memory data dirs if they exist.
            Create shared memory directories for saskan app.
            - shared mem parent dir
            - shared mem app sub dirs, includes 'data' dir
            - shared mem data sub dirs
            """
            app_d = path.join(self.d["MEM"], "saskan")
            ok, _, _ = self.get_dir(app_d)
            if ok:
                app_files = app_d + "/*"
                ok, result = SI.run_cmd([f"rm -rf {app_files}"])
                if not ok:
                    raise Exception(result)
                ok, result = SI.run_cmd([f"rmdir {app_d}"])
                if not ok:
                    raise Exception(result)
            ok, msg = self.make_dir(app_d)
            if not ok:
                raise Exception(f"{self.t['err_file']} {app_d} {msg}")
            ok, result = SI.run_cmd(f"chmod u=rwx,g=rwx,o=rwx {app_d}")
            if not ok:
                raise Exception(f"{self.t['err_file']} {app_d} {result}")
            for sd in self.d["APPDIRS"]:
                app_sd = path.join(app_d, sd)
                ok, msg = self.make_dir(app_sd)
                if not ok:
                    raise Exception(f"{self.t['err_file']} {app_sd} {msg}")
                ok, result = SI.run_cmd(f"chmod u=rwx,g=rwx,o=rwx {app_sd}")
                if not ok:
                    raise Exception(f"{self.t['err_file']} {app_sd} {result}")
            for dd in self.d["DATADIRS"]:
                data_d = path.join(app_d, "data", dd)
                ok, msg = self.make_dir(data_d)
                if not ok:
                    raise Exception(f"Failed to create dir: {data_d} {msg}")
                ok, result = SI.run_cmd(f"chmod u=rwx,g=rwx,o=rwx {data_d}")
                if not ok:
                    raise Exception(f"{self.t['err_file']} {data_d} {result}")

        def pickle_config_objects():
            """Pickle dict versions of config json files.
            """
            src_dir = path.join(self.d['TGT'], self.d['APP'], "data/config")
            ok, err, files = self.get_dir(src_dir)
            if not ok:
                raise Exception(f"{self.t['err_file']} {src_dir} {err}")
            for f in files:
                if Path(f).is_file():
                    file_nm = str(f).split("/")[-1]
                    if file_nm.endswith(".json"):
                        mem_file = path.join(
                            self.d['MEM'], self.d['APP'], "data/config",
                            file_nm.replace(".json", ".pickle"))
                        _, _, cfg_data = self.get_file(f)
                        ok, err = self.pickle_object(mem_file,
                                                     json.loads(cfg_data))
                        if not ok:
                            raise Exception(
                                f"{self.t['err_file']} {mem_file} {err}")
        # pickle_saskan() main
        # ====================
        create_mem_dirs()
        pickle_config_objects()
