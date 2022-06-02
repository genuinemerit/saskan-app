#!python
"""Saskan Eyes file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes a file to /usr/local/bin
"""

import argparse as ap

from os import path
from pathlib import Path
from pprint import pprint as pp   # noqa: F401

from io_config import ConfigIO      # type: ignore
from io_file import FileIO          # type: ignore
from io_redis import RedisIO        # type: ignore
from saskan_meta import SaskanMeta  # type: ignore

CI = ConfigIO()
FI = FileIO()
RI = RedisIO()
SM = SaskanMeta()


class SaskanInstall(object):
    """Configure file set-up for Saskan_Eyes.
    """
    def __init__(self):
        """Initialize directories and files for saskan_eyes.
        """
        self.SRC_DIR, self.TGT_DIR, self.SRC_FILES = self.get_arguments()
        ok = self.verify_bash_bin_dir()
        if ok and self.SRC_FILES is not None:
            ok = self.set_app_dirs()
        if ok:
            ok = self.set_log_configs()
        if ok:
            ok = self.copy_app_files()
        if ok:
            ok = SM.refresh_gui_meta()
        if ok:
            ok = self.copy_bash_files()
        else:
            print(f"{CI.txt.err_process} file deployment")
        """
        if ok:
            ok = self.copy_html_files()
        if ok:
            ok = self.copy_jpg_files()
        if ok:
            ok = self.copy_config_files()
        if ok:
            ok = self.copy_python_files()
        """

    def get_arguments(self):
        """Handle command-line arguments."""
        src_files = None
        parser = ap.ArgumentParser(description=CI.txt.desc_cfg_files)
        # Parent directory for source files:
        parser.add_argument('source_dir', metavar='FROM', type=str,
                            help=CI.txt.desc_source)
        # Parent directory for target files:
        parser.add_argument('target_dir', metavar='TO', type=str,
                            help=CI.txt.desc_target)
        args = parser.parse_args()
        if "BowDataSchema" not in args.source_dir:
            args.source_dir = args.source_dir + "/BowDataSchema"
        ok, err, src_files = FI.get_dir(args.source_dir)
        if not(ok):
            print(f"{CI.txt.err_file} {args.source_dir} {err}")
        return(args.source_dir, args.target_dir, src_files)

    # Helpers
    # ==============================================================
    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        ok, err, _ = FI.get_dir(CI.path_usr_bin)
        if ok:
            print(f"{CI.txt.val_ok} {CI.path_usr_bin}")
        else:
            print(f"{CI.txt.err_file} {CI.path_usr_bin} {err}")
        return ok

    # Configuration file and record setters
    # ==============================================================
    def set_app_dirs(self):
        """Create saskan app directories if they don't already exist.
           Save settings as Redis config records.
        - [TGT]/saskan..
            - /bin
            - /cfg
            - /res
            - /sav
        """
        def set_app_path():
            app_dir = path.join(self.TGT_DIR, CI.dir_app)
            ok, err, _ = FI.get_dir(app_dir)
            if not(ok):
                ok, err = FI.make_dir(app_dir)
            ok, err = FI.make_executable(app_dir)
            if ok:
                RI.write_redis_config(CI.app_path_key, app_dir)
                print(f"{CI.txt.val_ok} {app_dir}")
                return app_dir
            else:
                print(f"{CI.txt.err_file} {app_dir} {err}")
                return False

        def set_sub_paths(p_app_dir: str):
            for sub_dir in CI.app_subdirs:
                sdir = path.join(p_app_dir, sub_dir)
                ok, err, _ = FI.get_dir(sdir)
                if not(ok):
                    ok, err = FI.make_dir(sdir)
                ok, err = FI.make_executable(sdir)
                if sub_dir == "save":
                    ok, err = FI.make_writable(sdir)
                if ok:
                    RI.write_redis_config(sub_dir + "_path", sub_dir)
                    print(f"{CI.txt.val_ok} {sdir}")
                else:
                    print(f"{CI.txt.err_file} {sdir} {err}")
                    return False
            return True

        # set_app_dirs main
        # ==================================================================
        app_dir = set_app_path()
        if app_dir is not False:
            set_sub_paths(app_dir)
            return True
        else:
            return False

    def set_log_configs(self):
        """Write default configs for logging and monitoring.
            to Redis Config records
        - debug, trace, info, warn, error
        """
        for log_type, log_default in CI.log_configs.items():
            RI.write_redis_config(log_type, log_default)
        return True

    def copy_app_files(self):
        """Copy from [SRC] to [TGT]/saskan
            - python files --> /saskan
            - /html --> /html
            - /images --> /images
            - /config --> /config
        """
        app_dir = path.join(self.TGT_DIR, CI.dir_app)
        for src_dir, dst_dir in CI.copy_files.items():
            src_dir = path.join(self.SRC_DIR, src_dir)
            dst_dir = path.join(app_dir, dst_dir)
            ok, err, files = FI.get_dir(src_dir)
            if not(ok):
                print(f"{CI.txt.err_file} {src_dir} {err}")
                return False
            for f in files:
                if Path(f).is_file():
                    file_name = str(f).split("/")[-1]
                    dst_file = path.join(dst_dir, file_name)
                    ok, err = FI.copy_file(str(f), dst_file)
                    if ok:
                        ok, err = FI.make_readable(dst_file)
                        print(f"{CI.txt.val_ok} {dst_file}")
                    else:
                        print(f"{CI.txt.err_file} {dst_file} {err}")
                        return False
        return True

    def copy_bash_files(self):
        """Copy from [SRC]/BowDataSchema/bash
        - /saskan_eyes
        - /saskan_install
        - /saskan_config
        - /saskan_log
        to /usr/local/bin:

        These are the command-line exectuables for saskan.
        Each script has to be modified to correctly locate:
        - python files in the saskan app directory
        For the saskan_installer script, also need to modify:
        - SRC_DIR and TGT_DIR
        """
        bash_dir = path.join(self.SRC_DIR, "bash")
        app_dir = path.join(self.TGT_DIR, CI.dir_app)
        ok, err, files = FI.get_dir(bash_dir)
        if not(ok):
            print(f"{CI.txt.err_file} {bash_dir} {err}")
        else:
            for bf in files:
                bf_name = str(bf).split("/")[-1]
                bash_file_to = path.join(CI.path_usr_bin, bf_name)
                ok, err, bash_file_data = FI.get_file(str(bf))
                if ok:
                    bash_file_data =\
                        bash_file_data.replace("~APP_DIR~", app_dir)
                    if bf_name == "saskan_install":
                        bash_file_data =\
                            bash_file_data.replace("~SRC_DIR~", self.SRC_DIR)
                        bash_file_data =\
                            bash_file_data.replace("~TGT_DIR~", self.TGT_DIR)
                    ok, err = FI.write_file(p_path=bash_file_to,
                                            p_data=bash_file_data)
                    ok, err = FI.make_executable(bash_file_to)
                    print(f"{CI.txt.val_ok} {bash_file_to}")
                else:
                    print(f"{CI.txt.err_file} {bash_file_to} {err}")
        return ok

    # ==================== obsolete ==========================

    def copy_html_files(self):
        """Copy to [TGT]/saskan/res:
        - [SRC]BowDataSchema/html/*.html
        """
        html_dir = path.join(self.SRC_DIR, "html")
        ok, err, ht_files = FI.get_dir(html_dir)
        if not(ok):
            print(f"{CI.txt.err_file} {html_dir} {err}")
        else:
            for hf in ht_files:
                if str(hf)[-5:] == ".html":
                    ht_name = str(hf).split("/")[-1]
                    res_file = path.join(self.TGT_DIR, CI.path_res, ht_name)
                    ok, err = FI.copy_file(p_path_from=str(hf),
                                           p_path_to=res_file)
                    if ok:
                        ok, err = FI.make_readable(res_file)
                        print(f"{CI.txt.val_ok} {res_file}")
                    else:
                        print(f"{CI.txt.err_file} {res_file} {err}")
        return ok

    def copy_jpg_files(self):
        """Copy to [TGT]/saskan/res:
        - [SRC]BowDataSchema/images/*.jpg
        """
        img_dir = path.join(self.SRC_DIR, "images")
        ok, err, files = FI.get_dir(img_dir)
        if not(ok):
            print(f"{CI.txt.err_file} {img_dir} {err}")
        else:
            for jf in files:
                if str(jf)[-4:] == ".jpg":
                    jf_name = str(jf).split("/")[-1]
                    res_file = path.join(self.TGT_DIR, CI.path_res, jf_name)
                    ok, err = FI.copy_file(p_path_from=str(jf),
                                           p_path_to=res_file)
                    if ok:
                        ok, err = FI.make_readable(res_file)
                        print(f"{CI.txt.val_ok} {res_file}")
                    else:
                        print(f"{CI.txt.err_file} {res_file} {err}")
        return ok

    def copy_config_files(self):
        """Copy to [TGT]/saskan/cfg:
        - [SRC]BowDataSchema/config_widgets.json
        - [SRC]BowDataSchema/saskan_ontology_xml.owl
        """
        cfg_dir = path.join(self.SRC_DIR, "config")
        ok, err, files = FI.get_dir(cfg_dir)
        if not(ok):
            print(f"{CI.txt.err_file} {cfg_dir} {err}")
        else:
            for cf in files:
                cf_name = str(cf).split("/")[-1]
                cfg_file_to = path.join(self.TGT_DIR, CI.path_cfg, cf_name)
                ok, err = FI.copy_file(p_path_from=str(cf),
                                       p_path_to=cfg_file_to)
                if ok:
                    ok, err = FI.make_readable(cfg_file_to)
                    print(f"{CI.txt.val_ok} {cfg_file_to}")
                else:
                    print(f"{CI.txt.err_file} {cfg_file_to} {err}")
        return ok

    def copy_python_files(self):
        """Copy to [TGT]/saskan/python:
        - [SRC]BowDataSchema/*.py
        """
        ok, err, files = FI.get_dir(self.SRC_DIR)
        if not(ok):
            print(f"{CI.txt.err_file} {self.SRC_DIR} {err}")
        else:
            for pf in files:
                if str(pf)[-3:] == ".py":
                    py_name = str(pf).split("/")[-1]
                    bin_file = path.join(self.TGT_DIR, CI.path_bin, py_name)
                    ok, err = FI.copy_file(p_path_from=str(pf),
                                           p_path_to=bin_file)
                    if ok:
                        ok, err = FI.make_executable(bin_file)
                        print(f"{CI.txt.val_ok} {bin_file}")
                    else:
                        print(f"{CI.txt.err_file} {bin_file} {err}")
        return ok


if __name__ == '__main__':
    SI = SaskanInstall()
