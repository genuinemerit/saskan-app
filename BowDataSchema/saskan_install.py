#!python
"""Saskan Eyes file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes a file to /usr/local/bin
Launch it by running sudo /bash/saskan_install from the project venv directory,
e.g. (saskan) ~/../BowDataSchema/bash/saskan_install
"""

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
        self.t = MI.get_text_meta()
        self.d = MI.get_dirs_meta()
        self.verify_bash_bin_dir()
        self.a = self.set_app_path()
        self.set_app_sub_paths()
        self.set_shared_mem_paths()
        self.init_log_configs()
        self.copy_resource_files()
        self.copy_python_files()
        self.copy_bash_files()

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

    # Directory, file, record set-up
    # ==============================================================
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
        for sub_dir in self.d['SUBDIRS']:
            sdir = path.join(self.a, sub_dir)
            ok, err, _ = FI.get_dir(sdir)
            if not (ok):
                ok, err = FI.make_dir(sdir)
            ok, err = FI.make_executable(sdir)
            if sub_dir == "save":
                ok, err = FI.make_writable(sdir)
            if not ok:
                raise Exception(f"{self.t['err_file']} {sdir} {err}")

    def set_shared_mem_paths(self):
        """Set namespace / data paths in shared memory.
        """
        for name_space in \
                [ns[3:] for ns in self.t.keys() if ns.startswith("ns_")]:
            ns_path = path.join(self.d["MEM"], name_space)
            ok, err, _ = FI.get_dir(ns_path)
            if not ok:
                ok, err = FI.make_dir(ns_path)
            if not ok:
                raise Exception(f"{self.t['err_file']} {ns_path} {err}")

    def init_log_configs(self):
        """Write default settings for logging and monitoring to /data.
        - debug, trace, info, warn, error
        """
        log_cfg_vals = dict()
        log_cfg_path = path.join(self.d["MEM"], "log", "log_cfg.pickle")
        for log_type in self.d["LOG"]:
            log_cfg_vals[log_type] = self.t[f"val_{log_type}"]
        pp(("Debug", log_cfg_vals))
        ok, msg = FI.pickle_object(log_cfg_path, log_cfg_vals)
        if not ok:
            raise Exception(f"{self.t['err_file']} {log_cfg_path} {msg}")

    def copy_resource_files(self):
        """Copy from [SRC] to [TGT]/saskan
            - python files --> /python
            - /data --> /data
            - /html --> /html
            - /images --> /images
            - /bash --> /usr/local/bin
        """
        for adir in self.d["COPY"]:
            src_dir = path.join(self.d['SRC'], adir)
            ok, err, files = FI.get_dir(src_dir)
            if not ok:
                raise Exception(f"{self.t['err_file']} {src_dir} {err}")
            tgt_dir = path.join(self.a, adir)
            for f in files:
                if Path(f).is_file():
                    file_name = str(f).split("/")[-1]
                    tgt_file = path.join(tgt_dir, file_name)
                    ok, err = FI.copy_file(str(f), tgt_file)
                    if not ok:
                        raise Exception(
                            f"{self.t['err_file']} {tgt_file} {err}")

    def copy_python_files(self):
        """Copy from [SRC] to [TGT]/saskan
            - python files --> /python
        """
        src_dir = path.join(self.d['SRC'])
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{self.t['err_file']} {src_dir} {err}")
        py_files = [f for f in files if str(f).endswith(".py")]
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
        """Copy from [SRC]/BowDataSchema/bash
        to /usr/local/bin:

        Set up the command-line exectuables for saskan.
        Modify before copying to correctly locate the
        - python files in the saskan app directory
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


if __name__ == '__main__':
    SI = SaskanInstall()
