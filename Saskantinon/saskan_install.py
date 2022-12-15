#!python
"""Saskan Eyes file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes bash files to /usr/local/bin
Launch it by running sudo ./saskan_install from the git project directory,
e.g. (saskan) ~/../Saskantinon/saskan_install
"""
import json

from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401

from io_file import FileIO          # type: ignore
from io_shell import ShellIO        # type: ignore

FI = FileIO()
SI = ShellIO()


class SaskanInstall(object):
    """Configure and install set-up for Saskan apps.

    @DEV: Replace hard-coded home-directory path with
          an argument.
    """
    def __init__(self):
        """Initialize directories and files.
        """
        self.verify_bash_bin_dir()
        self.a = self.set_app_path()
        self.set_app_sub_paths()
        self.set_data_sub_paths()
        self.set_log_configs()
        self.copy_config_files()
        self.copy_schema_files()
        # self.copy_html_files()
        self.copy_images_files()
        self.copy_python_files()
        self.copy_bash_files()
        FI.pickle_saskan()

    # Helpers
    # ==============================================================

    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        bash_bin = FI.d["BIN"]
        ok, err, _ = FI.get_dir(bash_bin)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {bash_bin} {err}")

    # Directory, file, record set-up
    # ==============================================================

    def set_app_path(self):
        """If app already exists, delete everything.
        Create sakan app directory if it doesn't exist.
        """
        app_dir = path.join(FI.d['TGT'], FI.d['APP'])
        ok, err, _ = FI.get_dir(app_dir)
        if ok:
            app_files = app_dir + "/*"
            ok, result = SI.run_cmd([f"sudo rm -rf {app_files}"])
            if not ok:
                raise Exception(result)
            ok, result = SI.run_cmd([f"sudo rmdir {app_dir}"])
            if not ok:
                raise Exception(result)
        ok, err = FI.make_dir(app_dir)
        if not ok:
            raise Exception(err)
        ok, err = FI.make_executable(app_dir)
        if not ok:
            raise Exception(err)
        return app_dir

    def set_app_sub_paths(self):
        """Create sakan app sub-directories if they don't already exist.
        """
        for sub_dir in FI.d['APPDIRS']:
            sdir = path.join(self.a, sub_dir)
            ok, err, _ = FI.get_dir(sdir)
            if not ok:
                ok, err = FI.make_dir(sdir)
            ok, err = FI.make_executable(sdir)
            if sub_dir == "save":
                ok, err = FI.make_writable(sdir)
            if not ok:
                raise Exception(f"{FI.t['err_file']} {sdir} {err}")

    def set_data_sub_paths(self):
        """Set data sub paths.
        """
        for sub_dir in FI.d['DATADIRS']:
            sdir = path.join(self.a, "data", sub_dir)
            ok, err, _ = FI.get_dir(sdir)
            if not ok:
                ok, err = FI.make_dir(sdir)
            if not ok:
                raise Exception(f"{FI.t['err_file']} {sdir} {err}")

    def set_log_configs(self):
        """Write JSON config file for default logging and monitoring.
        """
        self.m_log_vals = dict()
        for log_type in FI.d["LOGCFG"]:
            self.m_log_vals[log_type] = FI.t[f"val_{log_type}"]
        ok, msg = FI.write_file(
            path.join(self.a, "data/config/m_log.json"),
            json.dumps(self.m_log_vals))
        if not ok:
            raise Exception(f"{FI.t['err_file']} {msg}")

    def copy_config_files(self):
        """Copy /config --> /data/config
        """
        src_dir = path.join(FI.d['SRC'], "config")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
        FI.copy_files(path.join(self.a, "data/config"), files)

    def copy_schema_files(self):
        """Copy /schema --> /data/schema
        """
        src_dir = path.join(FI.d['SRC'], "schema")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
        FI.copy_files(path.join(self.a, "data/schema"), files)

    def copy_html_files(self):
        """Copy /html --> /html
        """
        src_dir = path.join(FI.d['SRC'], "html")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
        FI.copy_files(path.join(self.a, "html"), files)

    def copy_images_files(self):
        """Copy /images --> /images
        """
        src_dir = path.join(FI.d['SRC'], "images")
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
        FI.copy_files(path.join(self.a, "images"), files)

    def copy_python_files(self):
        """Copy - python (*.py) files --> /python
        Except for the installer script.
        """
        src_dir = path.join(FI.d['SRC'])
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
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
                        f"{FI.t['err_file']} {tgt_file} {err}")

    def copy_bash_files(self):
        """Copy /bash to /usr/local/bin

        Set up the command-line exectuables for saskan.
        Modify before copying to correctly locate the
        python files in the saskan app directory.
        """
        bash_dir = path.join(FI.d['SRC'], "bash")
        py_dir = path.join(self.a, "python")
        ok, err, files = FI.get_dir(bash_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {bash_dir} {err}")
        for bf in files:
            bf_name = str(bf).split("/")[-1]
            tgt_file = path.join(FI.d['BIN'], bf_name)
            ok, err, bf_code = FI.get_file(str(bf))
            if not ok:
                raise Exception(f"{FI.t['err_file']} {bf} {err}")
            bf_code = bf_code.replace("~APP_DIR~", py_dir)
            ok, err = FI.write_file(tgt_file, bf_code)
            if not ok:
                raise Exception(f"{FI.t['err_file']} {tgt_file} {err}")
            ok, err = FI.make_executable(tgt_file)
            if not ok:
                raise Exception(f"{FI.t['err_file']} {tgt_file} {err}")


if __name__ == '__main__':
    SI = SaskanInstall()
