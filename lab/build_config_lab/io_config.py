#!python
"""Provision bootstrap text strings for the app.

For internationalization, swap in translated version
of this Class module.
Other texts are defined in JSON config file and loaded
into the Redis "Basement" (0) database with "meta:" label.

module:     io_config.py
class:      ConfigIO/0
author:     GM <genuinemerit @ pm.me>
"""
from dataclasses import dataclass


class ConfigIO(object):
    """Static strings used by..
        - saskan_install
        - meta_io

    App-related texts should be stored in a JSON config file,
    one for each language being used.

    The directories can also been defined in a config file too.

    As with the Home Finance app, having multiple config files
    is a good idea. Don't try to put everything in one file.
    Maybe even consider breaking up the "GUI" metadata.

    For enhancing performance, since I am having trouble with
    Redis, let's go back to the old way of doing things -- stash
    stuff in dev/shm, so it will reside in memory. Set a wee flag
    indicating that the data is available in memory. Worry about
    stashing shit in Redis or whatever later.

    I am also OK with having lots of little files, as long as
    they are clearly named and organzied. Pretty much samet thing
    as having Redis objects, innit?

    Finally, since everything is going to JSON/memory, let's
    merge ConfigIO and MetaIO into one class.
    """
    def __init__(self):
        """Initialize infrastructure strings.
        """
        self.io()

    def io(self):
        """Application files, directories, DBs, graph geometry, etc. """
        self.SRC = "/home/Dropbox/Apps/BoW/bow-data-schema/BowDataSchema"
        self.TGT = "/home/saskan"
        self.path_usr_bin: str = '/usr/local/bin'
        self.gui_metadata: str = 'config/gui_metadata.json'
        self.app_path_key: str = "app_path"
        self.dir_app: str = 'saskan'
        self.app_subdirs: list = ['config', 'html', 'images', 'python', 'save']
        self.log_configs: dict = {
            'debug': self.txt.val_nodebug,
            'info':  self.txt.val_noinfo,
            'warn': self.txt.val_nowarn,
            'error': self.txt.val_noerror,
            'trace': self.txt.val_notrace}
        self.copy_files: dict = {
            "": "python",
            "config": "config",
            "html": "html",
            "images": "images"}

    @dataclass
    class txt:
        """Errors, warnings, help, captions, descriptions, config values"""
        desc_cfg_files: str = 'Configure BoW files, directories, binaries'
        desc_cfg_meta: str = 'Configure BoW metadata'
        desc_debug: str = 'Write developer debug-level messages to log'
        desc_info: str = 'Write info, warning, and error messages to log'
        desc_refresh: str = 'Force refresh of Basement DB from config files'
        desc_saskan_eyes: str = 'Saskan Eyes - Admin GUI for whole Ball of Wax'
        desc_source: str = 'Location of cloned bow-data-schema repo'
        desc_target: str = 'Desired parent location of Saskan Eyes app'
        desc_traced: str = 'Write trace-level msgs to log, w/ docstrings'
        desc_tracef: str = 'Write trace-level msgs to log, w/o docstrings'
        desc_warn: str = 'Write warning, error messages to log, not info msgs'
        err_file: str = 'Bad file or directory: '
        err_not_found: str = 'No records found'
        err_process: str = 'Process aborted: '
        err_record: str = 'Bad record: '
        ns_db_basement: str = 'basement'
        ns_db_harvest: str = 'harvest'
        ns_db_log: str = 'log'
        ns_db_monitor: str = 'monitor'
        ns_db_schema: str = 'schema'
        rec_ok: str = 'ok: '
        val_debug: str = 'DEBUG'
        val_error: str = 'ERROR'
        val_group: str = 'Group'
        val_info: str = 'INFO'
        val_nodebug: str = 'NODEBUG'
        val_noerror: str = 'NOERROR'
        val_noinfo: str = 'NOINFO'
        val_notrace: str = 'NOTRACE'
        val_nowarn: str = 'NOWARN'
        val_ok: str = 'OK'
        val_traced: str = 'DOCS'
        val_tracef: str = 'NODOCS'
        val_ul: str = '============================================='
        val_warn: str = 'WARN'
