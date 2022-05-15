#!python
"""Saskan Eyes file configuration set-up.
:module:    config_files.py
:class:     ConfigFiles/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes a file to /usr/local/bin
"""

import argparse as ap

from os import path
from pprint import pprint as pp   # noqa: F401

from io_boot import BootTexts     # type: ignore
from io_file import FileIO        # type: ignore
from io_redis import RedisIO      # type: ignore

BT = BootTexts()
FI = FileIO()
RI = RedisIO()


class ConfigFiles(object):
    """Configure file set-up for Saskan_Eyes.
    """
    def __init__(self):
        """Initialize directories and files for saskan_eyes.
        """
        self.SRC_DIR, self.TGT_DIR, self.SRC_FILES = self.init_source_files()
        ok = False
        if self.SRC_FILES is not None:
            ok = self.init_app_dirs()
        if ok:
            ok = self.init_bash_dirs()
        if ok:
            ok = self.copy_html_files()
        if ok:
            ok = self.copy_jpg_files()
        if ok:
            ok = self.copy_config_files()
        if ok:
            ok = self.copy_python_files()
        if ok:
            ok = self.write_default_configs()
        if ok:
            ok = self.copy_bash_files()
        if ok:
            ok = self.write_redis_config()
        else:
            print(f"{BT.txt.process_error} file deployment")

    # Command line argument handlers
    # ==============================================================
    def init_source_files(self):
        """Handle command-line arguments."""
        src_files = None
        parser = ap.ArgumentParser(description=BT.txt.desc_cfg_files)
        parser.add_argument('source_dir', metavar='FROM', type=str,
                            help=BT.txt.desc_source)
        parser.add_argument('target_dir', metavar='TO', type=str,
                            help=BT.txt.desc_source)
        args = parser.parse_args()
        if "BowDataSchema" not in args.source_dir:
            args.source_dir = args.source_dir + "/BowDataSchema"
        ok, err, src_files = FI.get_dir(args.source_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {args.source_dir} {err}")
        return(args.source_dir, args.target_dir, src_files)

    def init_app_dirs(self):
        """Create saskan app directories if they don't already exist.
        - [TGT]/saskan
        - [TGT]/saskan/bin
        - [TGT]/saskan/cfg
        - [TGT]/saskan/res
        """
        # Check path for app resources
        for dir in (BT.path_app, BT.path_bin, BT.path_cfg, BT.path_res):
            app_dir = path.join(self.TGT_DIR, dir)
            ok, err, _ = FI.get_dir(app_dir)
            if not(ok):
                ok, err = FI.make_dir(app_dir)
            ok, err = FI.make_executable(app_dir)
            if ok:
                print(f"{BT.txt.file_ok} {app_dir}")
            else:
                print(f"{BT.txt.file_error} {app_dir} {err}")
        return ok

    def init_bash_dirs(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        ok, err, _ = FI.get_dir(BT.path_usr_bin)
        if ok:
            print(f"{BT.txt.file_ok} {BT.path_usr_bin}")
        else:
            print(f"{BT.txt.file_error} {BT.path_usr_bin} {err}")
        return ok

    def copy_html_files(self):
        """Copy to [TGT]/saskan/res:
        - [SRC]BowDataSchema/html/*.html
        """
        html_dir = path.join(self.SRC_DIR, "html")
        ok, err, ht_files = FI.get_dir(html_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {html_dir} {err}")
        else:
            for hf in ht_files:
                if str(hf)[-5:] == ".html":
                    ht_name = str(hf).split("/")[-1]
                    res_file = path.join(self.TGT_DIR, BT.path_res, ht_name)
                    ok, err = FI.copy_file(p_path_from=str(hf),
                                           p_path_to=res_file)
                    if ok:
                        ok, err = FI.make_readable(res_file)
                        print(f"{BT.txt.file_ok} {res_file}")
                    else:
                        print(f"{BT.txt.file_error} {res_file} {err}")
        return ok

    def copy_jpg_files(self):
        """Copy to [TGT]/saskan/res:
        - [SRC]BowDataSchema/images/*.jpg
        """
        img_dir = path.join(self.SRC_DIR, "images")
        ok, err, files = FI.get_dir(img_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {img_dir} {err}")
        else:
            for jf in files:
                if str(jf)[-4:] == ".jpg":
                    jf_name = str(jf).split("/")[-1]
                    res_file = path.join(self.TGT_DIR, BT.path_res, jf_name)
                    ok, err = FI.copy_file(p_path_from=str(jf),
                                           p_path_to=res_file)
                    if ok:
                        ok, err = FI.make_readable(res_file)
                        print(f"{BT.txt.file_ok} {res_file}")
                    else:
                        print(f"{BT.txt.file_error} {res_file} {err}")
        return ok

    def copy_config_files(self):
        """Copy to [TGT]/saskan/cfg:
        - [SRC]BowDataSchema/config_widgets.json
        - [SRC]BowDataSchema/saskan_ontology_xml.owl
        """
        cfg_dir = path.join(self.SRC_DIR, "config")
        ok, err, files = FI.get_dir(cfg_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {cfg_dir} {err}")
        else:
            for cf in files:
                cf_name = str(cf).split("/")[-1]
                cfg_file_to = path.join(self.TGT_DIR, BT.path_cfg, cf_name)
                ok, err = FI.copy_file(p_path_from=str(cf),
                                       p_path_to=cfg_file_to)
                if ok:
                    ok, err = FI.make_readable(cfg_file_to)
                    print(f"{BT.txt.file_ok} {cfg_file_to}")
                else:
                    print(f"{BT.txt.file_error} {cfg_file_to} {err}")
        return ok

    def copy_python_files(self):
        """Copy to [TGT]/saskan/bin:
        - [SRC]BowDataSchema/*.py
        """
        ok, err, files = FI.get_dir(self.SRC_DIR)
        if not(ok):
            print(f"{BT.txt.file_error} {self.SRC_DIR} {err}")
        else:
            for pf in files:
                if str(pf)[-3:] == ".py":
                    py_name = str(pf).split("/")[-1]
                    bin_file = path.join(self.TGT_DIR, BT.path_bin, py_name)
                    ok, err = FI.copy_file(p_path_from=str(pf),
                                           p_path_to=bin_file)
                    if ok:
                        ok, err = FI.make_executable(bin_file)
                        print(f"{BT.txt.file_ok} {bin_file}")
                    else:
                        print(f"{BT.txt.file_error} {bin_file} {err}")
        return ok

    def write_default_configs(self):
        """Write default confings to control logging and monitoring.
        Write to [TGT]/saskan/cfg/
        - debug_level.cfg
        - trace_level.cfg
        - info_level.cfg
        - warn_level.cfg
        - error_level.cfg

        @DEV:
        - Consider using a single config file instead.
        """
        for cfg, default_val in ((BT.debug_level, BT.txt.val_nodebug),
                                 (BT.log_level, BT.txt.val_error),
                                 (BT.trace_level, BT.txt.val_notrace)):
            cfg_file = path.join(self.TGT_DIR, cfg)
            ok, err = FI.write_file(cfg_file, default_val)
            if ok:
                ok, err = FI.make_writable(cfg_file)
                print(f"{BT.txt.file_ok} {cfg_file}")
            else:
                print(f"{BT.txt.file_error} {cfg_file} {err}")
                break
        return ok

    def copy_bash_files(self):
        """Copy to /usr/local/bin:
        - [SRC]BowDataSchema/saskan_eyes
        - [SRC]BowDataSchema/saskan_install
        - [SRC]BowDataSchema/saskan_config
        - [SRC]BowDataSchema/saskan_log

        Edit these files with app_dir before writing them.
        """
        bash_dir = path.join(self.SRC_DIR, "bash")
        bin_dir = path.join(self.TGT_DIR, BT.path_bin)
        ok, err, files = FI.get_dir(bash_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {bash_dir} {err}")
        else:
            for bf in files:
                bf_name = str(bf).split("/")[-1]
                bash_file_to = path.join(BT.path_usr_bin, bf_name)
                ok, err, bash_file_data = FI.get_file(str(bf))
                if ok:
                    bash_file_data =\
                        bash_file_data.replace("~APP_DIR~", bin_dir)
                    if bf_name == "saskan_install":
                        bash_file_data =\
                            bash_file_data.replace("~SRC_DIR~", self.SRC_DIR)
                        bash_file_data =\
                            bash_file_data.replace("~TGT_DIR~", self.TGT_DIR)
                    ok, err = FI.write_file(p_path=bash_file_to,
                                            p_data=bash_file_data)
                    ok, err = FI.make_executable(bash_file_to)
                    print(f"{BT.txt.file_ok} {bash_file_to}")
                else:
                    print(f"{BT.txt.file_error} {bash_file_to} {err}")
        return ok

    def write_redis_config(self):
        """Write to Redis "basement" (0) database:
        - Location of [TGT]

        Redis record format:
        {db_namespace:
            {"name": record_key_value,
             "values": record_values_dict,
             "audit": audit_dict}}"

        Call RI.set_audit_values() to set audit values.
        It also determines whether to do an insert or update.
        """
        app_path = path.join(self.TGT_DIR, BT.path_app)
        record_key = "config.app_path"
        db_rec: dict = {BT.txt.ns_db_basement:
                        {"name": record_key,
                         "values": {"app_path": app_path}}}
        db_rec, do_update = RI.set_audit_values(db_rec)
        if do_update:
            RI.do_update(p_db=BT.txt.ns_db_basement, p_rec=db_rec)
        else:
            RI.do_insert(p_db=BT.txt.ns_db_basement, p_rec=db_rec)
        print(f"{BT.txt.rec_ok} " +
              f"{BT.txt.ns_db_basement}.{record_key} " +
              f"({db_rec['audit']['version']})")


if __name__ == '__main__':
    CF = ConfigFiles()
