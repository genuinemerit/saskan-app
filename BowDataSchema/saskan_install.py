#!python
"""Saskan Eyes file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes a file to /usr/local/bin
Launch it by running sudo /bash/saskan_install from the git project directory,
e.g. (saskan) ~/../BowDataSchema/saskan_install

@DEV
- Wipe previous install before copying new files.
"""
import json

from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401

from io_file import FileIO          # type: ignore
from io_meta import MetaIO          # type: ignore

FI = FileIO()
MI = MetaIO()


class SaskanInstall(object):
    """Configure and install set-up for Saskan app.
    """
    def __init__(self):
        """Initialize directories and files.
        """
        self.app_lang = "en"
        self.d = self.get_dirs_setup()
        self.t = MI.get_text_meta(self.d, self.app_lang)
        self.verify_bash_bin_dir()
        self.a = self.set_app_path()
        self.set_app_sub_paths()
        self.set_data_sub_paths()
        self.init_log_configs()
        self.copy_config_files()
        self.copy_schema_files()
        self.copy_html_files()
        self.copy_images_files()
        self.copy_python_files()
        self.copy_bash_files()
        self.pickle_texts_and_configs()

    # Helpers
    # ==============================================================

    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        bash_bin = self.d["BIN"]
        ok, err, _ = FI.get_dir(bash_bin)
        if not ok:
            raise Exception(f"{self.t['err_file']} {bash_bin} {err}")

    def copy_files(self,
                   p_tgt_dir: str,
                   p_files):
        """Copy from [SRC] to [TGT]/saskan"""
        for f in p_files:
            if Path(f).is_file():
                file_name = str(f).split("/")[-1]
                tgt_file = path.join(p_tgt_dir, file_name)
                ok, err = FI.copy_file(str(f), tgt_file)
                if not ok:
                    raise Exception(
                        f"{self.t['err_file']} {tgt_file} {err}")

    # Directory, file, record set-up
    # ==============================================================

    def get_dirs_setup(self):
        """Read app set-up metadata regarding directories from git project JSON file.
        Returns: (dict) Directory values or exception.
        """
        ok, msg, dirs =\
            FI.get_file(path.join("config", "m_directories.json"))
        if not ok:
            raise Exception(f"Error reading directories metadata: {msg}")
        return(json.loads(dirs))

    def set_app_path(self):
        """Create sakan app directory if it doesn't already exist.
        """
        app_dir = path.join(self.d['TGT'], self.d['APP'])
        ok, err, _ = FI.get_dir(app_dir)
        if not ok:
            ok, err = FI.make_dir(app_dir)
        ok, err = FI.make_executable(app_dir)
        if not ok:
            raise Exception(err)
        return app_dir

    def set_app_sub_paths(self):
        """Create sakan app sub-directories if they don't already exist.
        """
        for sub_dir in self.d['APPDIRS']:
            sdir = path.join(self.a, sub_dir)
            ok, err, _ = FI.get_dir(sdir)
            if not ok:
                ok, err = FI.make_dir(sdir)
            ok, err = FI.make_executable(sdir)
            if sub_dir == "save":
                ok, err = FI.make_writable(sdir)
            if not ok:
                raise Exception(f"{self.t['err_file']} {sdir} {err}")

    def set_data_sub_paths(self):
        """Set data sub paths.
        """
        for sub_dir in self.d['DATADIRS']:
            sdir = path.join(self.a, "data", sub_dir)
            ok, err, _ = FI.get_dir(sdir)
            if not ok:
                ok, err = FI.make_dir(sdir)
            if not ok:
                raise Exception(f"{self.t['err_file']} {sdir} {err}")

    def init_log_configs(self):
        """Write JSON config file for default logging and monitoring.
        """
        self.log_cfg_vals = dict()
        for log_type in self.d["LOGCFG"]:
            self.log_cfg_vals[log_type] = self.t[f"val_{log_type}"]
        ok, msg = FI.write_file(
            path.join(self.a, "data/config/log_cfg.json"),
            json.dumps(self.log_cfg_vals))
        if not ok:
            raise Exception(f"{self.t['err_file']} {msg}")

    def copy_config_files(self):
        """Copy /config --> /data/config
        """
        src_dir = path.join(self.d['SRC'], "config")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        self.copy_files(path.join(self.a, "data/config"), files)

    def copy_schema_files(self):
        """Copy /schema --> /data/schema
        """
        src_dir = path.join(self.d['SRC'], "schema")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        self.copy_files(path.join(self.a, "data/schema"), files)

    def copy_html_files(self):
        """Copy /html --> /html
        """
        src_dir = path.join(self.d['SRC'], "html")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        self.copy_files(path.join(self.a, "html"), files)

    def copy_images_files(self):
        """Copy /images --> /images
        """
        src_dir = path.join(self.d['SRC'], "images")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        self.copy_files(path.join(self.a, "images"), files)

    def copy_python_files(self):
        """Copy - python (*.py) files --> /python
        Except for the installer script.
        """
        src_dir = path.join(self.d['SRC'])
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        py_files = [f for f in files if str(f).endswith(".py") and
                    str(f) != "saskan_install.py"]
        tgt_dir = path.join(self.a, "python")
        for f in py_files:
            if Path(f).is_file():
                file_name = str(f).split("/")[-1]
                tgt_file = path.join(tgt_dir, file_name)
                ok, err = FI.copy_file(str(f), tgt_file)
                if not ok:
                    raise Exception(
                        f"{self.t['err_file']} {tgt_file} {err}")

    def copy_bash_files(self):
        """Copy /bash to /usr/local/bin

        Set up the command-line exectuables for saskan.
        Modify before copying to correctly locate the
        python files in the saskan app directory.
        """
        bash_dir = path.join(self.d['SRC'], "bash")
        py_dir = path.join(self.a, "python")
        ok, err, files = FI.get_dir(bash_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {bash_dir} {err}")
        for bf in files:
            bf_name = str(bf).split("/")[-1]
            tgt_file = path.join(self.d['BIN'], bf_name)
            ok, err, bf_code = FI.get_file(str(bf))
            if not ok:
                raise Exception(f"{self.t['err_file']} {bf} {err}")
            bf_code = bf_code.replace("~APP_DIR~", py_dir)
            ok, err = FI.write_file(tgt_file, bf_code)
            if not ok:
                raise Exception(f"{self.t['err_file']} {tgt_file} {err}")
            ok, err = FI.make_executable(tgt_file)
            if not ok:
                raise Exception(f"{self.t['err_file']} {tgt_file} {err}")

    def pickle_texts_and_configs(self):
        """Pickle text dict and log config dict.
        """
        mdir = FI.set_shared_mem_dirs(
            self.d["MEM"], self.d["APPDIRS"], self.d["DATADIRS"])
        file_nm = f"m_texts_{self.app_lang}"
        ok, msg = FI.pickle_object(
            path.join(mdir["config"], f"{file_nm}.pickle"), self.t)
        if not ok:
            raise Exception(f"{self.t['err_file']} {file_nm} {msg}")
        file_nm = "log_cfg"
        ok, msg = FI.pickle_object(
            path.join(mdir["config"], f"{file_nm}.pickle"), self.log_cfg_vals)
        if not ok:
            raise Exception(f"{self.t['err_file']} {file_nm} {msg}")


if __name__ == '__main__':
    SI = SaskanInstall()
