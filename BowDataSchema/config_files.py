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

BT = BootTexts()
FI = FileIO()


class ConfigFiles(object):
    """Configure file set-up for Saskan_Eyes.

    - Copy to /usr/local/bin:
        - BowDataSchema/saskan_eyes
    """
    def __init__(self):
        """Initialize directories and files for saskan_eyes.
        """
        self.SRC_DIR, self.SRC_FILES = self.init_source_files()
        if self.SRC_FILES is not None:
            if not self.init_app_dirs():
                print(f"{BT.txt.process_error} file deployment")
            else:
                ok = self.copy_html_files()
                if ok:
                    ok = self.copy_jpg_files()
                if ok:
                    ok = self.copy_config_files()
                if ok:
                    ok = self.copy_python_files()
                if ok:
                    ok = self.copy_bash_file()
                if ok:
                    print("ok")

    # Command line argument handlers
    # ==============================================================
    def init_source_files(self):
        """Handle command-line arguments."""

        # Define command-line arguments
        src_files = None
        parser = ap.ArgumentParser(description=BT.txt.desc_cfg_files)
        parser.add_argument('source_dir', metavar='DIR', type=str,
                            help=BT.txt.desc_source)
        args = parser.parse_args()
        if "BowDataSchema" not in args.source_dir:
            args.source_dir = args.source_dir + "/BowDataSchema"
        ok, err, src_files = FI.get_dir(args.source_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {args.source_dir} {err}")
        return(args.source_dir, src_files)

    def init_app_dirs(self):
        """Create saskan app directories if they don't already exist.
        """
        for app_dir in (BT.path_app, BT.path_bin, BT.path_cfg, BT.path_res):
            ok, err, _ = FI.get_dir(app_dir)
            if not(ok):
                ok, err = FI.make_dir(app_dir)
            if ok:
                print(f"{BT.txt.file_ok} {app_dir}")
            else:
                print(f"{BT.txt.file_error} {app_dir} {err}")
        ok, err, _ = FI.get_dir(BT.path_usr_bin)
        if not(ok):
            print(f"{BT.txt.file_error} {BT.path_usr_bin} {err}")
        else:
            print(f"{BT.txt.file_ok} {BT.path_usr_bin}")
        return ok

    def copy_html_files(self):
        """Copy to $HOME/saskan/res:
        - BowDataSchema/html/*.html
        """
        html_dir = path.join(self.SRC_DIR, "html")
        ok, err, ht_files = FI.get_dir(html_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {html_dir} {err}")
        else:
            for hf in ht_files:
                if str(hf)[-5:] == ".html":
                    ht_name = str(hf).split("/")[-1]
                    res_file = path.join(BT.path_res, ht_name)
                    _, _, html_data = FI.get_file(hf)
                    ok, err = FI.write_file(p_path=res_file, p_data=html_data)
                    if not(ok):
                        print(f"{BT.txt.file_error} {res_file} {err}")
                    else:
                        print(f"{BT.txt.file_ok} {res_file}")
        return ok

    def copy_jpg_files(self):
        """Copy to $HOME/saskan/res:
        - BowDataSchema/images/*.jpg
        """
        img_dir = path.join(self.SRC_DIR, "images")
        ok, err, files = FI.get_dir(img_dir)
        if not(ok):
            print(f"{BT.txt.file_error} {img_dir} {err}")
        else:
            for jf in files:
                if str(jf)[-4:] == ".jpg":
                    jf_name = str(jf).split("/")[-1]
                    res_file = path.join(BT.path_res, jf_name)
                    _, _, jpeg_data = FI.get_file(jf, "rb")
                    ok, err = FI.write_file(p_path=res_file, p_data=jpeg_data,
                                            p_file_type="wb+")
                    if not(ok):
                        print(f"{BT.txt.file_error} {res_file} {err}")
                    else:
                        print(f"{BT.txt.file_ok} {res_file}")
        return ok

    def copy_config_files(self):
        """Copy to $HOME/saskan/cfg:
        - BowDataSchema/config_widgets.json
        - BowDataSchema/saskan_ontology_xml.owl
        """
        for cf_name in ("config_widgets.json", "saskan_ontology_xml.owl"):
            cf = path.join(self.SRC_DIR, cf_name)
            cfg_file = path.join(BT.path_cfg, cf_name)
            _, _, cfg_data = FI.get_file(cf)
            ok, err = FI.write_file(p_path=cfg_file, p_data=cfg_data)
            if not(ok):
                print(f"{BT.txt.file_error} {cfg_file} {err}")
            else:
                print(f"{BT.txt.file_ok} {cfg_file}")
        return ok

    def copy_python_files(self):
        """Copy to $HOME/saskan/bin:
        - BowDataSchema/*.py
        """
        ok, err, files = FI.get_dir(self.SRC_DIR)
        if not(ok):
            print(f"{BT.txt.file_error} {self.SRC_DIR} {err}")
        else:
            for pf in files:
                if str(pf)[-3:] == ".py":
                    py_name = str(pf).split("/")[-1]
                    bin_file = path.join(BT.path_bin, py_name)
                    _, _, py_data = FI.get_file(pf)
                    ok, err = FI.write_file(p_path=bin_file, p_data=py_data)
                    if not(ok):
                        print(f"{BT.txt.file_error} {bin_file} {err}")
                    else:
                        print(f"{BT.txt.file_ok} {bin_file}")
        return ok

    def copy_bash_file(self):
        """Copy to /usr/local/bin:
        - BowDataSchema/saskan_eyes
        """
        bash_name = "saskan_eyes"
        bf = path.join(self.SRC_DIR, bash_name)
        bash_file = path.join(BT.path_usr_bin, bash_name)
        _, _, bash_data = FI.get_file(bf)
        ok, err = FI.write_file(p_path=bash_file, p_data=bash_data)
        if not(ok):
            print(f"{BT.txt.file_error} {bash_file} {err}")
        else:
            print(f"{BT.txt.file_ok} {bash_file}")
            cmd = f"chmod u=rwx,g=rx,o=rx {bash_file}"
            ok, result = BT.run_cmd(cmd)
            print(result)
        return ok


if __name__ == '__main__':
    CF = ConfigFiles()
