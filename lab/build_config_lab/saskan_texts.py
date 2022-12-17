#!python3.9
"""Provision text strings in American English
   for the "saskan" app(s).

For internationalization, swap in translated version.

module:     saskan_texts.py
class:      SaskanTexts/0
author:     GM <genuinemerit @ pm.me>
"""
from dataclasses import dataclass


class SaskanTexts(object):
    """Static text strings."""

    @dataclass
    class db:
        """File and database names."""

        # App directories
        app_dir = 'saskantinon'
        cache_catg: str = 'catgs.pkl'
        db_name: str = 'saskan.db'
        db_token: str = 'db_status'
        log_name: str = 'saskan.log'
        log_token: str = 'log_level'
        log_trace: str = 'trace_level'
        not_null: str = 'Not NULL'
        oid_fk: str = '__oid'
        sask_arcv: str = 'arcv'
        sask_bin: str = 'bin'
        sask_bkup: str = 'bkup'
        sask_cache: str = 'cache'
        sask_db: str = 'db'
        sask_log: str = 'log'
        sask_res: str = 'res'

    @dataclass
    class ew:
        """Error and warning messages."""

        py3_req: str = "Python 3.9 is required."
        bad_path: str = "Path could not be reached: "
        bad_sql_type: str = "Schema item SQL type unknown: "
        bad_meta_type: str = "Schema meta type unknown: "
        bad_table_name: str = "SQL file not defined for table: "
        no_database: str = "Cannot complete request. No file found at: "

    @dataclass
    class mn:
        """Menus and menu items."""

        # Menus & Menu Items
        i_add_code: str = "Add Code"
        i_build_app: str = "Build App"
        i_close: str = 'Close'
        i_commit_code: str = "Commit Code"
        i_dba: str = "DB Admin"
        i_deploy_app: str = "Deploy App"
        i_dml: str = "Modify Data"
        i_edit_res: str = 'Edit Resources'
        i_edit_sketch: str = 'Edit Sketches'
        i_events: str = 'Events'
        i_exit: str = 'Exit'
        i_explore: str = 'Explore'
        i_gloss: str = 'Glossary'
        i_guide: str = 'User Guide'
        i_prefs: str = 'Preferences'
        i_stats: str = "SQL Stats"
        m_app_mnu: str = "App Menu"
        m_dba: str = 'Data Base'
        m_file: str = 'File'
        m_help: str = 'Help'
        m_res: str = 'Resources'
        m_sketch: str = 'Sketch'
        m_swa: str = 'Software'

    @dataclass
    class ms:
        """Messages and Labels."""

        ab_about: str = "Describe purpose of a table."
        ab_edge_assoc: str = "List of links via association table."
        ab_foreign_key: str = "Logical (oid-based) foreign key links."
        ab_lambda: str = "Externalized edit functions for specific columns."
        ab_pick_one: str = "List of options. Only one may be selected."
        ab_pick_many: str = "List of options. One or more may be selected."
        db_audit: str = "Audit column: "
        db_check: str = "Check Rule: "
        db_column: str = "DB Column"
        db_connect: str = "Connected to DB: "
        db_constraint: str = "Constraint rule: "
        db_key: str = "Key column: "
        db_link: str = "Link column: "
        db_links_from: str = "Links from <-- "
        db_links_to: str = "Links to --> "
        db_table: str = "DB Table"
        data_select: str = "Data selected: "
        data_type: str = "Data Type: "
        description: str = "Description: "
        empty: str = 'No data selected'
        is_audit: str = "Audit Field: "
        init_trace: str = "Starting module: "
        lcl_tm: str = "\n== Localhost Time: "
        length: str = "length "
        log_loc: str = "Log file location: "
        log_lvl: str = "Log level: "
        name: str = "Name: "
        no: str = "No"
        no_info: str = "No info available."
        none: str = "None"
        nothing: str = "Nothing"
        nullable: str = "Nullable: "
        pick_one: str = 'Pick One'
        pick_many: str = 'Pick One/Many'
        py_ver: str = "Your Python version is: "
        range_is: str = "Range is"
        removed: str = "File deleted: "
        sep_line: str = "============"
        sql_exec: str = "SQL file executed: "
        start_sess: str = "\n== Log Session started"
        tbl_create: str = "Created table: "
        undefined: str = "undefined"
        unv_tm: str = "\n== Universal Time: "
        welcome: str = "Welcome to Saskan Eyes"
        wrote: str = "File written to: "
        yes: str = "Yes"

    @dataclass
    class res:
        """Static resource names."""
        # button graphics
        btn_collapse = ['btn_collapse', 'menu_collapsed.png']
        btn_expand = ['btn_expand', 'menu_expanded.png']
        btn_actor = ['btn_actor', 'actor.png']
        btn_map = ['btn_map', 'map.png']
        btn_time = ['btn_time', 'time.png']
        # button texts
        btn_clear = ["btn_clear", "Clear"]
        btn_insert = ["btn_insert", "Add"]
        btn_query = ["btn_query", "Find"]
        btn_redis_info = ["btn_redis_info", "Redis Services Info"]
        btn_redis_kill = ["btn_redis_kill", "Stop Redis Services"]
        btn_redo = ["btn_redo", "Redo"]
        btn_remove = ["btn_remove", "Delete"]
        btn_save = ["btn_save", "Save"]
        btn_undo = ["btn_undo", "Undo"]
        btn_update = ["btn_update", "Change"]
        btn_view = ["btn_view", "Select"]

        # DB tree frame names
        dbt = {"about": "frm_dbt_about",
               "columns": "frm_dbt_cols",
               "domains": "frm_dbt_doms",
               "tables": "frm_dbt_tbls"}
        # edit frame names
        edt = {"dba": "frm_edt_dba",
               "dbs": "frm_edt_dbs",
               "dml": "frm_edt_dml",
               "prefs": "frm_edt_prefs",
               "resource": "frm_edt_res",
               "sketch": "frm_edt_skt",
               "software": "frm_edt_sware"}
        # other frame names
        app_root: str = "app_root_frm"
        stat = {"bottom": "frm_stat_bot"}
        tbx = {"navbar": "frm_tbx_nav"}

        # button style names
        bts_edit: str = "edit_btn_style"
        bts_leaf: str = "leaf_btn_style"
        bts_toolbox: str = "toolbox_btn_style"
        # frame style names
        fms_branch: str = "branch_frm_style"
        fms_container: str = "container_frm_style"
        fms_editor: str = "editor_frm_style"
        fms_status: str = "status_frm_style"
        fms_toolbox: str = "toolbox_frm_style"
        # label style names
        lbs_leaf: str = "leaf_label_style"
        # menu style names
        mns_item: str = "menu_item_style"
        mns_menu: str = "menu_style"
        # text style names
        txs_label: str = "text_label_style"
        txs_title: str = "text_title_style"

        # other resources
        jobs_path: str =\
            "/home/dave/Dropbox/Apps/BoW/bow-data-schema/BowDataSchema"
        user_guide: str = "https://bow.genuinemerit.com/Saskan_Home.html"

    @dataclass
    class tl:
        """Window, frame, messagebox titles."""

        app: str = 'Saskan Eyes'
        ctls: str = 'Commands'
        db_about: str = 'About '
        db_column: str = 'Columns'
        db_domain: str = 'Domains'
        db_explore: str = "Data Base Explorer"
        db_table: str = "Tables"
        dml_title: str = 'Modify Data'
        dml_actor: str = "Mod Actor"
        dml_calendar: str = "Mod Calendar"
        dml_campaign: str = "Mod Campaign"
        dml_place: str = "Mod Place"
        events: str = 'Events Manager'
        gloss: str = 'Saskantinon Glossary'
        links: str = 'Links'
        pick_domain: str = 'Domain Selected: '
        prefs: str = 'Application Settings'
        res_command: str = 'Resource Commands'
        sketch_command: str = 'Sketch Commands'
        sw_command: str = 'Software Commmands'
        tables: str = 'Tables'

    @dataclass
    class AuditFields:
        """Define audit columns used on all tables."""

        uid: str = ""
        hash_id: str = ""
        oid: str = ""
        create_ts: str = ""
        update_ts: str = ""
        delete_ts: str = ""

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

# CONSTANTS

    @dataclass
    class Colors:
        """Set up color palette."""
        BLACK: str = "#000000"
        BLUE: str = "#1F25DE"
        GOLD: str = "#DED81F"
        GRAY: str = "#999999"
        GRAY_LIGHT: str = "#DDDDDD"
        LIME: str = "#85DE1F"
        VIOLET: str = "#781FDE"
        WHITE: str = "#FFFFFF"

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

    @dataclass
    class HashLevel:
        """Define valid hashing levels."""

        SHA512: int = 128
        SHA256: int = 64
        SHA224: int = 56
        SHA1: int = 40

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

    @dataclass
    class LogLevel:
        """Define valid logging levels."""

        CRITICAL: int = 50
        FATAL: int = 50
        ERROR: int = 40
        WARNING: int = 30
        NOTICE: int = 20
        INFO: int = 20
        DEBUG: int = 10
        NOTSET: int = 0

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

    @dataclass
    class MsgLevel:
        """Define supported tkinter messagebox types."""

        INFO: str = 'INFO'
        WARN: str = 'WARN'
        ERROR: str = 'ERROR'

        def keys(self):
            """Get column names."""
            return list(self.__dataclass_fields__.keys())

    @dataclass
    class TextHelp:
        """Define useful constants for displaying text."""

        LF: str = '\n'
        LF_TAB: str = '\n\t'
        LF_TABx2: str = '\n\t\t'
        TAB: str = '\t'
        TABx2: str = '\t\t'
        LINE: str = '======================================='

    @dataclass
    class TimeZone:
        """Define commonly-used time zone values."""

        TZ_LA: str = 'America/Los_Angeles'
        TZ_NY: str = 'America/New_York'
        UTC: str = 'UTC'
