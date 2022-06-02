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
    """Static 'internal' strings used by..
        - saskan_install
        - saskan_meta
        - RedisIO

    App-related texts should be stored in the JSON config file.
    """
    def __init__(self):
        """Initialize infrastructure strings.

        @DEV
        - Any reason these can't also be a dataclass?
        """
        self.io()

    def io(self):
        """Application files, directories, DBs, graph geometry, etc. """
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
        self.gg_info: dict = {
            'N': "Nodes",
            'D2': "Bi-directional Edges",
            'D1': "Single-directional Edges"}
        self.gg_static_attrs: set = {'label', 'node_from', 'node_to', 'group'}

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
