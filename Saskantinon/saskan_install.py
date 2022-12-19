#!python
"""Saskan Apps file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes bash files to /usr/local/bin
Launch it by running sudo ./saskan_install from the git project directory,
e.g. (saskan) ~/../Saskantinon/saskan_install

@DEV:
- Consider using a get_cwd() method to get current working directory when
  installing from the git project directory. Then pull the name of the
  home directory from that path to derive the target directory.

@FIX:
- Note simplications for handling of log and monitor info.
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

    Bootstrap dirs configuration metadata from project directory.
    Use current working directory (git project) to derive home directory.
    """
    def __init__(self):
        """Initialize directories and files.
        """
        self.verify_bash_bin_dir()
        self.APP = path.join("/home", Path.cwd().parts[2], FI.D['APP'])
        self.create_app_space()
        self.install_app_files()
        self.copy_python_scripts()
        self.copy_bash_files()
        FI.pickle_saskan(self.APP)

    # Helpers
    # ==============================================================

    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        ok, err, _ = FI.get_dir(FI.D["BIN"])
        if not ok:
            raise Exception(f"{FI.T['err_file']} {FI.D['BIN']} {err}")

    # Directory, file, record set-up
    # ==============================================================

    def create_app_space(self):
        """If app dir already exists, delete everything.
        Create sakan app directory.
        Create sakan app sub-dirs.
        Create namesapce sub-dirs.
        """
        # App dir
        ok, err, _ = FI.get_dir(self.APP)
        if ok:
            # Delete everything in app dir
            app_files = self.APP + "/*"
            ok, result = SI.run_cmd([f"sudo rm -rf {app_files}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
            ok, result = SI.run_cmd([f"sudo rmdir {self.APP}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
        ok, err = FI.make_dir(self.APP)
        if ok:
            ok, err = FI.make_executable(self.APP)
        if not ok:
            raise Exception(f"{FI.T['err_process']} {err}")
        # App sub-dirs
        for _, sub_dir in FI.D['ADIRS'].items():
            sdir = path.join(self.APP, sub_dir)
            ok, err = FI.make_dir(sdir)
            if ok:
                ok, err = FI.make_executable(sdir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {sdir} {err}")
        # Namespace sub-dirs
        for _,  sub_dir in FI.D['NSDIRS'].items():
            sdir = path.join(self.APP, FI.D['ADIRS']['SAV'], sub_dir)
            ok, err = FI.make_dir(sdir)
            if ok:
                ok, err = FI.make_executable(sdir)
                if ok:
                    ok, err = FI.make_writable(sdir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {sdir} {err}")

    def install_app_files(self):
        """Copy config, image and schema/ontology files"""
        for sdir in (FI.D['ADIRS']['CFG'],
                     FI.D['ADIRS']['IMG'],
                     FI.D['ADIRS']['ONT']):
            src_dir = path.join(Path.cwd(), sdir)
            ok, err, files = FI.get_dir(src_dir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {src_dir} {err}")
            FI.copy_files(path.join(self.APP, sdir), files)

    def copy_python_scripts(self):
        """Copy - python (*.py) files --> /python
        Excluding installer scripts.
        """
        ok, err, files = FI.get_dir(Path.cwd())
        if not ok:
            raise Exception(f"{FI.t['err_file']} {Path.cwd()} {err}")
        py_files = [f for f in files if str(f).endswith(".py") and
                    "_install" not in str(f)]
        tgt_dir = path.join(self.APP, FI.D['ADIRS']['PY'])
        for f in py_files:
            if Path(f).is_file():
                tgt_file = path.join(tgt_dir, str(f).split("/")[-1])
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
        src_dir = path.join(Path.cwd(), "bash")
        py_dir = path.join(self.APP, FI.D['ADIRS']['PY'])
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.t['err_file']} {src_dir} {err}")
        for bf in files:
            bf_name = str(bf).split("/")[-1]
            tgt_file = path.join(FI.D['BIN'], bf_name)
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
