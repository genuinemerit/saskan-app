#!/usr/bin/python3
# coding: utf-8

"""Manage data for saskan_data app using sqlite3.
   - Set all DB datatypes to Text, to begin with.
   - Later, add hash_id and audit fields.

:module:    io_db.py
:classes:
- DataBase
:author:    GM (genuinemerit @ pm.me)
:configs:
- configs/d_dirs.json
"""
# import json
import sqlite3 as sq3
from copy import copy
from os import path, remove
from pathlib import Path
from pprint import pprint as pp

from io_file import FileIO

FI = FileIO()


class DataBase(object):
    """Support Sqlite3 database setup, usage, maintenance."""

    def __init__(self):
        """Initialize Dbase object.
        """
        self.DB = path.join(FI.D['APP'],
                            FI.D['ADIRS']['ONT'],
                            FI.D['DBNAME'])
        self.db_conn = None
        self.NULL = ""
        self.INTEGER = int()
        self.REAL = float()
        self.TEXT = str()
        self.BLOB = bytes()

    # DataBase Connections
    # ===========================================

    def disconnect_db(self):
        """Drop DB connection to SASKAN_DB."""
        if hasattr(self, "db_conn") and self.db_conn is not None:
            try:
                self.cur.close()
                self.db_conn.close()
            except RuntimeWarning:
                pass
        self.db_conn = None

    def connect_db(self):
        """Open DB connection to SASKAN_DB.
        Indicate that the DB should help to maintain referential
        integrity for foreign keys.
        This will create a SASKAN_DB file at the specified location
        if one does not already exist.
        :sets:
        - db_conn: the database connection
        - cur: cursor for the connection
        """
        self.disconnect_db()
        self.db_conn = sq3.connect(self.DB)
        self.db_conn.execute("PRAGMA foreign_keys = ON;")
        self.cur = self.db_conn.cursor()

    def get_sql_file(self,
                     p_sql_nm: str) -> str:
        """Read SQL from named file.
        :args:
        - p_sql_nm (str) Name of  SQL file in [APP]/schema
        :returns:
        - (str) Content of the SQL file
        """
        sql_nm = p_sql_nm.upper() + '.SQL'\
            if '.SQL' not in p_sql_nm\
            else p_sql_nm
        sql_path = path.join(FI.D['APP'],
                             FI.D['ADIRS']['ONT'],
                             sql_nm)
        SQL = FI.get_file(sql_path)
        return SQL

    def get_db_columns(self,
                       p_tbl_nm: str = None,
                       p_sql: str = None) -> list:
        """ For currently open connection and cursor, for the
        specified SQL SELECT file, return a list of the table's
        column names.
        :args:
        - p_tbl_nm (str) Optional. If provided, use this instead
          of scanning the SQL code.
        - p_sql (str) Optional. Text content of a well-structured
          SQL SELECT file, where table name is the last word in the
          first line. Use this is p_tbl_nm is not provided.
        :returns:
        - (list) of column names for the table
        """
        if p_tbl_nm is None:
            SQL = p_sql
            tbl_nm = SQL.split('\n')[0].split(' ')[-1]
        else:
            tbl_nm = p_tbl_nm
        self.cur.execute(f"PRAGMA table_info({tbl_nm})")
        cols = self.cur.fetchall()
        col_nms = [c[1] for c in cols]
        return col_nms

    def execute_select(self,
                       p_sql_nm: str) -> dict:
        """Run a SQL SELECT file which does not use
           any dynamic parameters.
        :args:
        - p_sql_nm (str): Name of external SQL file
        :returns:
        - (dict) Dict of lists, {col_nms: [data values]}
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        COLS = self.get_db_columns(p_sql=SQL)
        self.cur.execute(SQL)
        DATA = [r for r in self.cur.fetchall()]
        result = {col: [row[i] for row in DATA]
                  for i, col in enumerate(COLS)}
        self.disconnect_db()
        return result

    def execute_dml(self,
                    p_sql_nm: str):
        """Run a static SQL DROP, CREATE, DELETE, INSERT or MODIFY file,
        that is, a 'hard-coded' one which does not use any dynamic
        parameters.
        :args:
        - p_sql_nm (str): Name of external SQL file
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL)
        self.db_conn.commit()
        self.disconnect_db()

    def execute_insert(self,
                       p_sql_nm: str,
                       p_values: tuple):
        """Run a SQL INSERT file which uses dynamic values.
           Values are the column names in specified order.
           For now I will assume that:
            - INSERTs will always expect full list of values
            - caller knows what values to provide and in what order
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_values (tuple): n-tuple of values to insert

        @TODO:
        - Make a similar method to handle UPDATE via SQL file.
        - In that case, we'll want the PK value separately from the update
          values. And I think I can just always expect all col values.
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_values)
        self.db_conn.commit()
        self.disconnect_db()

    def execute_update(self,
                       p_sql_nm: str,
                       p_key_val: str,
                       p_values: tuple):
        """Run a SQL UPDATE file which uses dynamic values.
           Key value is the matching condition for WHERE clause (prim key).
           Values are the column names in specified order.
           For now I will assume that:
            - UPDATEs will always expect full list of values
            - caller knows what values to provide and in what order
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_key_val (str): Value of primary key to match on
        - p_values (tuple): n-tuple of values to update
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_values + (p_key_val,))
        self.db_conn.commit()
        self.disconnect_db()


    # =======================================================
    # Worry about all this later...
    # =======================================================

    def disconnect_dbkup(self):
        """Drop connection to backup database at specified path."""
        if hasattr(self, "dbkup_conn") and self.dbkup_conn is not None:
            try:
                self.dbkup_conn.close()
            except RuntimeWarning:
                pass
        self.dbkup_conn = None

    def connect_dbkup(self):
        """Open connection to backup database at specified path."""
        bkup_db = path.join(
            self.APP, TX.db.sask_bkup, TX.db.db_name)
        self.disconnect_dbkup()
        self.dbkup_conn = sq3.connect(bkup_db)

    def disconnect_darcv(self):
        """Drop connection to archive database at specified path."""
        if hasattr(self, "darcv_conn") and self.darcv_conn is not None:
            try:
                self.darcv_conn.close()
            except RuntimeWarning:
                pass
        self.darcv_conn = None

    def connect_darcv(self, p_arcv_db):
        """Open connection to archive database at specified path.

        Args:
            p_arcv_db (str): full path to archive DB file
        """
        self.disconnect_darcv()
        self.darcv_conn = sq3.connect(p_arcv_db)

    def backup_db(self):
        """Make full backup of the main database to the backup db.

        Create a backup database file if it does not exist, else
          overwrite existing backup DB file.
        """
        self.connect_dmain()
        self.connect_dbkup()
        self.dmain_conn.backup(self.dbkup_conn, pages=0, progress=None)
        self.disconnect_dmain()
        self.disconnect_dbkup()

    def archive_db(self):
        """Make full backup of main database with a timestamp.

        Distinct from regular backup file. A time-stamped, one-time copy.
        Make a point-in-time copy, e.g., prior to doing a purge.
        """
        main_db = path.join(self.APP, TX.db.sask_db, TX.db.db_name)
        if Path(main_db).exists():
            dttm = UT.get_dttm('UTC')
            arcv_db = path.join(self.APP, TX.db.sask_arcv,
                                "{}.{}".format(TX.db.db_name, dttm.curr_ts))
            self.connect_dmain()
            self.connect_darcv(arcv_db)
            self.dmain_conn.backup(self.darcv_conn, pages=0, progress=None)
            self.disconnect_dmain()
            self.disconnect_darcv()
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ms.wrote, arcv_db))
        else:
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ew.no_database, main_db))

    def destroy_main_db(self):
        """Delete the main database file."""
        main_db = path.join(
            self.APP, TX.db.sask_db, TX.db.db_name)
        if Path(main_db).exists():
            remove(main_db)
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ms.removed, main_db))
        else:
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ew.no_database, main_db))

    def destroy_bkup_db(self):
        """Delete the backup database file."""
        bkup_db = path.join(self.APP, TX.db.sask_bkup, TX.db.db_name)
        if Path(bkup_db).exists():
            remove(bkup_db)
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ms.removed, bkup_db))
        else:
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ew.no_database, bkup_db))

    class BuildSchemaDB(object):
        """Use this sub-class when setting up a new database.

        @DEV
        - Make this a separate module. It is really part of setup code.
        """

        def __init__(self, DB: object):  # noqa: N803
            """Initialize BuildSchemaDB object.

            Args:
                DB (object): Instance of parent class.
            """
            self.DB = DB
            self.LOG = DB.LOG
            self.SCH = DB.SCH
            self.CS = ", "
            self.TRACE = self.get_trace_level()
            if self.TRACE != "NONE":
                print(">> Trace is turned ON.")
                print(">> Logging is enabled.")
                print(">> Schema data has been loaded.")
                if self.TRACE == "DETAIL":
                    pp(("Schema data:\n", DB.SCH))
            self.meta = dict()
            self.edges = dict()
            self.tables = dict()
            self.sql = {
                "ddl": {},
                "dml": {}}

        def get_trace_level(self):
            """If log/trace_level == "SHOW", write trace info to console."""
            trc_path = path.join(self.DB.APP, TX.db.sask_log, TX.db.log_trace)
            with open(trc_path, "r") as trcf:
                trace_mode = trcf.read()
            trcf.close()
            return trace_mode.strip()

        def get_schema_meta(self):
            """Harvest SQL metadata from schema categories.

            Using Category.Entity keys, like `map.places`, `story.artifact`,
            create dicts for -->
            - "about" - descriptions of tables
            - "python_func" - edit functions and what fields use them
            - "pick_one", "pick_many: - options names, values
            - "table" - SQL Table names
            - "import" - SQL sub-entity names
            - "edge_assoc" - one-to-many tables
            - "ref_edges" - reference for foreign keys other than edge_assoc
            - <SQL types> - like Integer, Float, etc. not really used,
              but collected for sake of completeness, may be useful in reviews

            `self.meta` will drive processing of metadata to generate
            SQL tables, either directly (basic tables) or indirectly (others).
            """
            def set_meta_dict(mkey):
                if mkey not in self.meta:
                    self.meta[mkey] = dict()

            def collect_about():
                mkey = "about"
                set_meta_dict(mkey)
                if mkey in a_val.keys():
                    self.meta[mkey][ikey] = a_val[mkey]

            def collect_sql_types():
                if "sql_ty" in a_val.keys():
                    mkey = a_val["sql_ty"].lower()
                    set_meta_dict(mkey)
                    self.meta[mkey][ikey] = mkey

            def collect_pick_options():
                for pick in ("ref.pick_one", "ref.pick_many"):
                    if pick in a_valv.keys():
                        mkey = pick.replace("ref.", "")
                        set_meta_dict(mkey)
                        self.meta[mkey][ikey + "." + a_valk] =\
                            a_valv[pick]

            def collect_edge_assocs():
                if "prim.kit" in a_valv.keys():
                    mkey = "edge_assoc"
                    set_meta_dict(mkey)
                    self.meta[mkey][ikey + "." + a_valk] =\
                        a_valv["prim.kit"][0]

            def collect_foreign_keys():
                if a_valv[-4:] == ".oid":
                    mkey = "foreign_key"
                    set_meta_dict(mkey)
                    self.meta[mkey][ikey + "." + a_valk] = a_valv

            # get_schema_meta() main
            # =============================================
            for catg_nm in self.SCH['Catgs'].keys():
                for a_nm, a_val in self.SCH['Catgs'][catg_nm]['Attrs'].items():
                    ikey = catg_nm + "." + a_nm
                    collect_about()
                    collect_sql_types()
                    for a_valk, a_valv in a_val.items():
                        if type(a_valv) is dict:
                            collect_pick_options()
                            collect_edge_assocs()
                        elif type(a_valv) is str:
                            collect_foreign_keys()

        def set_oid_uid_cols(self) -> dict:
            """Set up the first two cols used on all tables."""
            oid_uid = {"__oid": "TEXT\tNOT NULL",
                       "__uid": "TEXT\tPRIMARY KEY"}
            return oid_uid

        def set_tbl_col_from_cols(self) -> dict:
            """Set up `tbl_`, `col_` from` cols used on ref tables."""
            tbl_col_from = {"_tbl_from": "TEXT",
                            "_col_schema_from": "TEXT",
                            "_col_db_from": "TEXT"}
            return tbl_col_from

        def set_tbl_col_to_cols(self) -> dict:
            """Set up `tbl_`, `col_` to cols used on ref tables."""
            tbl_col_to = {"_tbl_to": "TEXT",
                          "_col_to": "TEXT"}
            return tbl_col_to

        def set_oid_in_out_cols(self) -> dict:
            """Set up `oid_` in, out cols used on ref tables."""
            oid_in_out = {"_oid_in": "TEXT",
                          "_oid_out": "TEXT"}
            return oid_in_out

        def set_audit_cols(self) -> dict:
            """Set up the audit cols used on all tables."""
            audit_cols = {'ω_init_dttm': 'TEXT\tNOT NULL',
                          'ω_remv_dttm': 'TEXT',
                          'ω_updt_dttm': 'TEXT\tNOT NULL',
                          'ωω_hash':
                          'TEXT\tNOT NULL\tCHECK (length(ωω_hash) = 64)'}
            return audit_cols

        def store_sql_file(self,
                           p_file_nm: str,
                           p_sql: str) -> str:
            """Save SQL DDL or DML file.

            Args:
                p_file_nm (str): SQL file name without path.
                p_sql (str): Content to write to the file.

            Returns: (str) full path to the saved file.
            """
            sqf_path = path.join(self.DB.APP, TX.db.sask_db,
                                 "{}.sql".format(p_file_nm))
            with open(sqf_path, "w") as sqf:
                sqf.write(p_sql)
            sqf.close()
            self.LOG.write_log(
                ST.LogLevel.DEBUG, "{} {}".format(TX.ms.wrote, sqf_path))
            return sqf_path

        def execute_sql_file(self,
                             p_tbl_nm: str,
                             p_sql_type: str):
            """Run a SQL file.

            Execute the DDL or DML file for the identified table.
            For multi-line DML, execute each instruction,
            like each `INSERT`, separately.

            Args:
                p_tbl_nm (str): SQL table name defined in `self.tables`.
                p_sql_type (str): Must be 'ddl' or 'dml' (may expand later)

            Raises:
            - SQL file is not identified
            - SQL path invalid
            - SQL execution failed
            """
            def verify_metadata():
                if p_tbl_nm in self.tables\
                        and p_sql_type in self.tables[p_tbl_nm]:
                    sql_file = path.join(self.DB.APP, TX.db.sask_db,
                                         self.tables[p_tbl_nm][p_sql_type])
                else:
                    msg = "{}{} ({})".format(
                        TX.ew.bad_table_name, p_tbl_nm, p_sql_type)
                    self.LOG.write_log(ST.LogLevel.ERROR, msg)
                    raise Exception(OSError, msg)
                return sql_file

            def read_sql_file():
                try:
                    with open(sql_file, 'r') as sqf:
                        sql = sqf.read()
                    sqf.close()
                except Exception as err:
                    msg = TX.ew.bad_path + sql_file
                    self.LOG.write_log(
                        ST.LogLevel.ERROR,
                        str(err) + "\n{}".format(msg))
                    raise Exception(IOError, msg)
                return sql

            def connect():
                self.DB.connect_dmain()
                cur = self.DB.dmain_conn.cursor()
                return cur

            def disconnect(cur):
                cur.close()
                self.DB.dmain_conn.commit()
                self.DB.disconnect_dmain()

            def execute_ddl(cur, sql, sql_file):
                try:
                    cur.execute(sql)
                    self.LOG.write_log(
                        ST.LogLevel.DEBUG,
                        TX.ms.sql_exec + ": {}".format(sql_file))
                except Exception as err:
                    self.LOG.write_log(
                        ST.LogLevel.ERROR,
                        str(err) + "\tIn: " + str(sql_file))

            def execute_dml(cur, sql, sql_file):
                for cmd_sql in sql.split(";"):
                    try:
                        cur.execute(cmd_sql + ";")
                    except Exception as err:
                        self.LOG.write_log(
                            ST.LogLevel.ERROR, str(err) +
                            "\tIn: " + str(sql_file) +
                            "\tCode: " + str(cmd_sql))
                self.LOG.write_log(
                    ST.LogLevel.DEBUG,
                    TX.ms.sql_exec + ": {}".format(sql_file))

            # execute_sql_file() main
            # ===============================
            sql_file = verify_metadata()
            sql = read_sql_file()
            cur = connect()
            if p_sql_type == "ddl":
                execute_ddl(cur, sql, sql_file)
            elif p_sql_type == "dml":
                execute_dml(cur, sql, sql_file)
            disconnect(cur)

        def generate_sql_ddl(self,
                             p_tbl_nm: str):
            """Generate and save SQL DDL file for creating a table.

            Args:
                p_tbl_nm (str): Name to use to define table on DB.
            """
            sql = """-- TABLE: {}

CREATE TABLE IF NOT EXISTS {} (
            """.format(p_tbl_nm, p_tbl_nm)
            for coln in sorted(self.tables[p_tbl_nm]["cols"].keys()):
                colv = self.tables[p_tbl_nm]["cols"][coln]
                sql += "\n{}\t{},".format(coln.strip(), colv.strip())
            sql = sql[:-1]
            sql += ");\n"
            self.tables[p_tbl_nm]["ddl"] =\
                self.store_sql_file(
                    p_file_nm="create_{}".format(p_tbl_nm),
                    p_sql=sql)

        def generate_pick_sql_dml(self,
                                  p_mcatg: str):
            """Generate DML code for pick tables.

            Columns get created on database in alphabetical order,
            no matter what order they;re listed in metadat.

            The pick tables contain "to", lookup values for fields
            identified as foreign keys to a pick table.
            Metadata for those FK relations is stored in `ref_foreign_key`,

            Args:
                p_mcatg (str): `self.meta` key for pick table being created.
            """
            msql = ""
            tbl_nm = "ref_{}".format(p_mcatg)
            for mkey in sorted(self.meta[p_mcatg].keys()):
                fromitm = mkey.split(".")
                tbl_from = fromitm[0] + "_" + fromitm[1]
                col_schema_from = fromitm[2]
                col_db_from = "_fk_" + col_schema_from + "_" + p_mcatg
                oid = UT.get_uid()  # same for all rows for tbl-in/col-in
                dt = UT.get_dttm('UTC')
                for pickv in self.meta[p_mcatg][mkey]:
                    hash_val = UT.get_hash(tbl_from + col_schema_from + pickv)
                    sql = """
INSERT INTO {} VALUES (
'{}', '{}',
'{}', '{}',
'{}', '{}',
'{}', '{}', '{}', '{}');""".format(tbl_nm,
                                   oid, UT.get_uid(),
                                   col_db_from, col_schema_from,
                                   tbl_from, pickv,
                                   dt.curr_utc, self.DB.NULL,
                                   dt.curr_utc, hash_val)
                    msql += sql
            self.tables[tbl_nm]["dml"] = self.store_sql_file(
                p_file_nm="insert_{}".format(tbl_nm), p_sql=msql)

        def generate_foreign_key_sql_dml(self):
            """Define how to populate data rows on ref_foreign_key table.

            Columns get created on database in alphabetical order,
            no matter what order they;re listed in metadat.

            This is a metadata-only table with static values.
            It shows all oid-based logical-foreign-key relationships between
            tables, including:
                - one-to-many, using association tables
                - one-to-many, using pick_one or pick_many tables
                - one-to-one, direct links between basic tables
            """
            msql = ""
            tbl_nm = "ref_foreign_key"
            for mcatg in ("foreign_key", "edge_assoc",
                          "pick_one", "pick_many"):
                for mkey in sorted(self.meta[mcatg].keys()):
                    inv = mkey.split(".")
                    tbl_from = inv[0] + "_" + inv[1]
                    col_schema_from = inv[2]
                    col_db_from = "_fk_"
                    if mcatg in ("foreign_key", "edge_assoc"):
                        col_to = "__oid"
                        outv = self.meta[mcatg][mkey].split(".")
                        tbl_to = outv[0] + "_" + outv[1]
                        if mcatg == "edge_assoc":
                            col_db_from += "x_"
                        col_db_from += col_schema_from + "_" + tbl_to
                    else:
                        col_to = "__uid"
                        tbl_to = "ref_" + mcatg
                        col_db_from += col_schema_from + "_" + mcatg
                    dt = UT.get_dttm('UTC')
                    hash_val = UT.get_hash(
                        str(col_db_from) + col_schema_from +
                        col_to + tbl_from + tbl_to)
                    sql = """
INSERT INTO {} VALUES (
'{}', '{}',
'{}', '{}', '{}',
'{}', '{}',
'{}', '{}', '{}', '{}');""".format(tbl_nm,
                                   UT.get_uid(), UT.get_uid(),
                                   col_db_from, col_schema_from, col_to,
                                   tbl_from, tbl_to,
                                   dt.curr_utc, self.DB.NULL,
                                   dt.curr_utc, hash_val)
                    msql += sql
            self.tables[tbl_nm]["dml"] = self.store_sql_file(
                p_file_nm="insert_{}".format(tbl_nm), p_sql=msql)

        def generate_about_sql_dml(self):
            """Define how to populate data rows on ref_about table.

            Columns get created on database in alphabetical order,
            no matter what order they;re listed in metadat.

            This is a static metadata table containing descriptions
            of tables.
            """
            msql = ""
            mcatg = "about"
            tbl_nm = "ref_{}".format(mcatg)
            dataty = "text"
            for mkey in sorted(self.meta[mcatg].keys()):
                tbl_from = mkey if "_x_" in mkey\
                    else mkey.split(".")[0] + "_" + mkey.split(".")[1]
                about = self.meta[mcatg][mkey]
                dt = UT.get_dttm('UTC')
                hash_val = UT.get_hash(tbl_from + about + dataty)
                sql = """
INSERT INTO {} VALUES (
'{}', '{}',
'{}', '{}', '{}',
'{}', '{}',
'{}', '{}', '{}', '{}');""".format(tbl_nm,
                                   UT.get_uid(), UT.get_uid(),
                                   self.DB.NULL, self.DB.NULL, tbl_from,
                                   about, dataty,
                                   dt.curr_utc, self.DB.NULL,
                                   dt.curr_utc, hash_val)
                msql += sql
            self.tables[tbl_nm]["dml"] = self.store_sql_file(
                p_file_nm="insert_{}".format(tbl_nm), p_sql=msql)

        def create_table(self,
                         p_mkey: str,
                         p_cols: dict,
                         p_is_xref: bool = False,
                         p_about: str = None,
                         p_dml_func: object = None):
            """Generate DDL code and create a new table.

            For association tables, extra logic names the table.
            Optionally generate, run DML code to populate it.

            Args:
                p_mkey (str): category.item_name like `ref.about`
                p_cols (dict): Name, value definition of SQL columns.
                p_is_xref (bool): True or False. Default is False.
                p_about (str): Table description.
                    If = None, then description is already stored in
                    `about` meta.
                    If not None and is an assoc (xref) table,
                    then about param = `to-tblnm~about phrase`, e.g.,
                    tilde (~) separated
                p_dml_func (object): Reference to function for generating
                  DML code for the table. Optional. If it is None, then no
                  DML function is executed.
            """
            def name_assoc_table():
                """Make an efficient xref (assoc) table name.

                If from-tbl name same as from-field name, do not repeat
                the from-tbl name.
                If to-tbl in same category as from-tbl, do not repeat
                the category name.
                """
                from_catg = p_mkey.split(".")[0]
                from_tbl = list(set(p_mkey.split(".")))
                if from_catg in from_tbl:
                    from_tbl.remove(from_catg)
                from_tbl = from_tbl[0]\
                    if len(from_tbl) == 1 else "_".join(from_tbl)
                to_key = p_about.split("~")[0].split(".")
                if from_catg in to_key:
                    to_key.remove(from_catg)
                if "oid" in to_key:
                    to_key.remove("oid")
                to_key = to_key[0]\
                    if len(to_key) == 1 else "_".join(to_key)
                tblnm = "{}_{}_x_{}".format(from_catg, from_tbl, to_key)
                self.meta["about"][tblnm] = p_about.split("~")[1]
                return tblnm

            # create_table() main
            # ==============================
            if p_is_xref:
                tblnm = name_assoc_table()
            else:
                tblnm = p_mkey.replace(".", "_")
                if p_about is not None:
                    self.meta["about"][p_mkey] = p_about
            self.tables[tblnm] = dict()
            self.tables[tblnm]["cols"] = p_cols
            self.generate_sql_ddl(tblnm)
            self.execute_sql_file(tblnm, "ddl")
            if p_dml_func is not None:
                p_dml_func()
                self.execute_sql_file(tblnm, "dml")

        def create_pick_tables(self):
            """Build out metadata for and create the `ref_pick_*` table.

            Two tables:
            - ref_pick_one: Select one item from set of options.
            - ref_pick_many: Select one-to-may items from set of options.

            These tables may have multiple rows per tbl_from/col_from combo.
            """

            def generate_pick_one_sql_dml():
                self.generate_pick_sql_dml("pick_one")

            def generate_pick_many_sql_dml():
                self.generate_pick_sql_dml("pick_many")

            abouts = (TX.ms.ab_pick_one, TX.ms.ab_pick_many)
            dml_funcs = (generate_pick_one_sql_dml,
                         generate_pick_many_sql_dml)
            for ti, mkey in enumerate(("ref.pick_one", "ref.pick_many")):
                self.create_table(
                    p_mkey=mkey,
                    p_cols={**self.set_oid_uid_cols(),
                            **self.set_tbl_col_from_cols(),
                            "option": "TEXT NOT NULL",
                            **self.set_audit_cols()},
                    p_is_xref=False,
                    p_about=abouts[ti],
                    p_dml_func=dml_funcs[ti])

        def create_assoc_tables(self):
            """Build out metadata for and create the `edge_assoc` tables.

            These are association tables. They hold lists of OID key
            values that tie to together a column on the `in` (from) table
            to oids/records on the `out` (to) table.

            The tables are named using `_x_` syntax to help quickly
            idenfify the relationship. If the from table name and column
            name have the same value (as they often do) then we abbreviate
            the from name in the xref table name

            These are updated dynamically, not statically. The links are
            between one from-side logical row (oid) and multiple to-side
            logical rows (oids), by way of a shared oid on the association
            table.
            - From table stores OID of the association table row.
            - Association table stores OIDs of from-row and to-rows.
            - The linked-to table has no special stores other than its
               usual OID idenitifier(s).
            """
            for mkey in self.meta["edge_assoc"]:
                self.create_table(
                    p_mkey=mkey,
                    p_cols={**self.set_oid_uid_cols(),
                            **self.set_tbl_col_from_cols(),
                            **self.set_tbl_col_to_cols(),
                            **self.set_oid_in_out_cols(),
                            **self.set_audit_cols()},
                    p_is_xref=True,
                    p_about="{}~{}".format(
                        self.meta["edge_assoc"][mkey],
                        TX.ms.ab_edge_assoc),
                    p_dml_func=None)

        def create_fkey_table(self):
            """Build out metadata for and create the `ref_foreign_key` table.

            It is purely a metadata table docuenting all oid-based links
            between tables, both one-logical-row to one-logical-row
            relationships and relationships that go through an association
            table.  It is informational only, so specific row-level oid values
            are not recorded.
            """
            self.create_table(
                p_mkey="ref.foreign_key",
                p_cols={**self.set_oid_uid_cols(),
                        **self.set_tbl_col_from_cols(),
                        **self.set_tbl_col_to_cols(),
                        **self.set_audit_cols()},
                p_is_xref=False,
                p_about=TX.ms.ab_foreign_key,
                p_dml_func=self.generate_foreign_key_sql_dml)

        def create_about_table(self):
            """Build out metadata for and create the `ref_about` table.

            It contains "about" text for all tables, with
            reference to what table (`tbl_from`) it is for.
            It also holds a `col_from` field for future use,
            if/when I add about info at the column level.

            Datatype BLOB (bytes) used instead of TEXT.
            So no auto conversion to UTF and it could be
            binary like a PDF. In such cases, content of PDF
            stored in tDB, not a URL reference to a file.
            Presently always set datatype to TEXT.
            """
            self.create_table(
                p_mkey="ref.about",
                p_cols={**self.set_oid_uid_cols(),
                        **self.set_tbl_col_from_cols(),
                        "about": "\tBLOB NOT NULL",
                        "datatype": "TEXT",
                        **self.set_audit_cols()},
                p_is_xref=False,
                p_about=TX.ms.ab_about,
                p_dml_func=self.generate_about_sql_dml)

        def create_basic_tables(self):
            """Build out metadata for and create regular data tables.

            Define consistent, concise, well-ordered column names on tables.

            Handle pick lists by reference to pick tables.
            Don't use CONSTRAINT for those.
            """
            def get_tblnm_attrs(mkey):
                catg = mkey.split(".")[0]
                entity = mkey.split(".")[1]
                tblnm = "{}_{}".format(catg, entity)
                attrs = {atnm: atval for atnm, atval
                         in self.SCH['Catgs'][catg]['Attrs'][entity].items()
                         if atnm not in ("about", "audit", "sql_ty")}
                return (tblnm, attrs)

            def set_list_or_sel_cols(atkey, atnm):
                if atkey == "prim.kit":
                    colnm = "x_{}".format(atnm)
                elif atkey == "ref.pick_one":
                    colnm = "_fk_{}_{}".format(atnm,
                                               atkey.replace(".", "_")[4:])
                elif atkey == "ref.pick_many":
                    colnm = "_fk_{}_{}".format(atnm,
                                               atkey.replace(".", "_")[4:])
                return (colnm, 'TEXT')

            def set_link_cols(colnm, atval, dataty):
                colnm = colnm.replace(".", "_")
                if atval != [] and atval[-4:] == ".oid":
                    colnm = "_fk_{}_{}".format(
                        colnm, atval.replace(".", "_"))[:-4]
                    dataty = "TEXT"
                return (colnm, dataty)

            def set_prim_datatype(atval):
                prim_nm = atval.split(".")[1]
                prim_attrs =\
                    self.SCH['Catgs']["prim"]['Attrs'][prim_nm]
                if "sql_ty" in list(prim_attrs.keys()):
                    dataty =\
                        "\t{}".format(prim_attrs["sql_ty"].upper())
                if "sql_constraint" in list(prim_attrs.keys()):
                    dataty +=\
                        "\t{}".format(prim_attrs["sql_constraint"])
                if "sql_check" in list(prim_attrs.keys()):
                    dataty += "\tCHECK ({})".format(
                        prim_attrs["sql_check"].replace(
                            "%name", colnm))
                return dataty

            # create_basic_tables() main
            # ===================================
            for mkey in self.meta["table"].keys():
                tblnm, attrs = get_tblnm_attrs(mkey)
                sql_cols = dict()
                for atnm, atval in sorted(attrs.items()):
                    dataty = None
                    if isinstance(atval, dict):
                        atkey = list(atval.keys())[0]
                        colnm, dataty = set_list_or_sel_cols(atkey, atnm)
                        atval = atval[atkey]
                        atval = "" if atval == [] else atval[0]
                    else:
                        colnm = atnm
                    colnm, dataty = set_link_cols(colnm, atval, dataty)
                    if dataty is None and "prim." in atval:
                        dataty = set_prim_datatype(atval)
                    sql_cols[colnm] = dataty

                self.create_table(
                    p_mkey=mkey,
                    p_cols={**self.set_oid_uid_cols(),
                            **sql_cols,
                            **self.set_audit_cols()})

        def create_all_tables(self, p_db_path: str) -> bool:
            """Create DB tables on main database matching Schema categories.

            1) Collect, prepare, curate metadata based on schema.
            2) Generate and store SQL DDL and DML files based metadata.
            3) If database already exists, archive it, then remove it.
            4) Execute DDL files to create database.

            Args:
                p_db_path (str): Full path to main DB location.
            Returns:
                (bool): True on success, else False
            """
            if self.TRACE != "NONE":
                print("\ncreate_all_tables\n========")

            tables_status = False
            self.DB.archive_db()
            self.DB.destroy_main_db()
            self.DB.destroy_bkup_db()
            self.get_schema_meta()
            self.create_pick_tables()
            self.create_assoc_tables()
            self.create_fkey_table()
            self.create_about_table()
            self.create_basic_tables()
            tables_status = True

            if self.TRACE != "NONE":
                print(">> Database has been rebuilt")
            return tables_status

        def save_db_status(self, token_path, db_status):
            """Store token with DB status setting."""
            with open(token_path, 'w') as tok:
                tok.write(db_status + "\n")
            tok.close()

        def create_db(self, p_db_path: str):
            """Create main database.

            Args:
                p_db_path (str): validated path to db storage location
            """
            _, _, db_status = FI.get_db_status()
            if db_status != "COMPLETE":

                if self.TRACE != "NONE":
                    print(">> Rebuilding the database...")
                    print(">>> DB path: {}".format(p_db_path))
                    print(">>> DB name: {}".format(TX.db.db_name))

                db_full_path = path.join(p_db_path, TX.db.db_name)
                if self.create_all_tables(db_full_path):
                    db_status = "COMPLETE"
                FI.set_db_status(db_status)

        def verify_db_path(self):
            """Fail if data store path does not exist."""
            db_path = path.join(self.DB.APP, TX.db.sask_db)
            if not Path(db_path).exists():
                msg = TX.ew.bad_path + db_path
                raise Exception(OSError, msg)
            return db_path

    class QueryDBMeta(object):
        """Use this sub-class to run read-only meta-queries.

        This is a class just for metadata queries.
        Since they are likely to be seldom used, kept
        separate for better garbage collection.

        @DEV:
        - Consider making it a separate class altogether.
        """

        def __init__(self, DB: object):     # noqa: N803
            """Initialize QueryDBMeta object."""
            self.DB = DB
            self.LOG = DB.LOG
            self.MASTER_DATA = self.get_master_data()

        def get_about_metadata(self,
                               p_tbl_nm: str,
                               p_col_nm: str = None) -> object:
            """Read ref_about table for selected item.

            Currently, there is `about` on the DB only for tables.
            Table generated entirely by logic (some ref_ tables)
            currently do not have `about` info.

            Args:
                p_tbl_nm (str): Table to get about info on.
                p_col_nm (str, optional): Column to get about info on.

            Raises:
                IOError if SQL execution fails.

            Returns:
                object: resultset
            """
            result = None
            self.DB.connect_dmain()
            cur = self.DB.dmain_conn.cursor()
            sql = "SELECT about, MAX(ω_updt_dttm), __oid, __uid "
            sql += "FROM ref_about "
            sql += "WHERE _tbl_from='{}' ".format(p_tbl_nm)
            sql += "AND ω_remv_dttm = '';"
            try:
                result = cur.execute(sql).fetchall()
                self.DB.disconnect_dmain()
            except IOError:
                self.DB.dmain_conn.close()
            # Add oid, uid and audit info if it becomes useful...
            result_rec = [{
                "tbl_nm": p_tbl_nm,
                "about": rec[0]} for rec in result]
            return result_rec[0]

        def get_master_data(self) -> object:
            """Read sqlite_master to get table metadata.

            Raises:
                IOError if SQL execution fails.

            Returns:
                (object): resultset
            """
            result = None
            self.DB.connect_dmain()
            cur = self.DB.dmain_conn.cursor()
            sql = "SELECT tbl_name, sql FROM sqlite_master WHERE type='table';"
            try:
                result = cur.execute(sql).fetchall()
                self.DB.disconnect_dmain()
            except IOError:
                self.DB.dmain_conn.close()
            result = [{"catg_tbl": rec[0],
                       "catg_nm": rec[0].split("_")[0],
                       "tbl_nm": rec[0].split("_", 1)[1],
                       "sql": rec[1]} for rec in result]
            return result

        def get_db_categories(self) -> list:
            """Pull only list of domain names from metadata.

            Returns:
                list: names of data categories
            """
            domains = [rec["catg_nm"] for rec in self.MASTER_DATA]
            return sorted(set(domains))

        def get_db_tables(self, catg_nm: str) -> list:
            """Return all tables in a specified domain (data category).

            Args:
                catg_nm: Name of domain to be queried.

            Returns:
                list: names of tables in domain.
            """
            tables = [rec["tbl_nm"] for rec in self.MASTER_DATA
                      if rec["catg_nm"] == catg_nm]
            return sorted(set(tables))

        def convert_check_sql_to_meta(self,
                                      p_check: str,
                                      p_col_nm: str) -> str:
            """Convert CHECK SQL to a dict describing the rule.

            Args:
                p_check (str): CHECK SQL
                p_col_nm (str): Name of the db column.

            Returns:
                str: rule_description for display

            @DEV
            - Not using `IN` rules to verify select options,
              but left logic here in case `IN` checks added later.
            """
            rule = None
            if p_check is not None:
                if ' IN ' in p_check.upper():
                    enum = TX.ms.pick_one\
                        if '_one' in p_col_nm else TX.ms.pick_many
                    values = p_check.split("(")[2][:-3].replace("'", "")
                    if values.strip() == "":
                        values = TX.ms.undefined.title()
                    rule = "{}: ({})".format(enum.title(), values)
                elif "length" in p_check.lower():
                    rule = "{}={}".format(
                        TX.ms.length.title().strip(),
                        p_check.split(" ")[3][:-1])
                elif " AND " in p_check.upper():
                    rule = "{}:{}".format(
                        TX.ms.range_is.title(),
                        p_check.split("(")[1][:-1].replace(
                            p_col_nm, "").replace("  ", " ").strip())
            return rule

        def get_db_columns(self,
                           p_tbl_nm: str,
                           p_col_nm: str = None,
                           p_use_catg_tbl: bool = False) -> list:
            """Return all columns in a specified table.

            Include data type, constraints, checks, key, FK and audit
            designations.

            Args:
                p_tbl_nm: Name of table to be queried.
                p_use_catg_tbl: If True, use full table name (dom + tbl).
                p_col_nm: Optional. Name of column to be queried.

            Returns:
                list: names of columns in table.
            """
            if p_use_catg_tbl:
                ddl = [rec["sql"] for rec in self.MASTER_DATA
                       if rec["catg_tbl"] == p_tbl_nm][0]
            else:
                ddl = [rec["sql"] for rec in self.MASTER_DATA
                       if rec["tbl_nm"] == p_tbl_nm][0]
            ddl = ddl[:-1].split("\n")[2:]
            if p_col_nm is not None:
                ddl = [col for col in ddl if p_col_nm in col]
            ddl_out = list()
            for col in ddl:
                col_data = col.split("\t")
                col_dict = {
                    "name": col_data[0],
                    "type": col_data[1],
                    "is_key": False, "is_link": False, "is_audit": False,
                    "constraint": None, "check": None}
                if col_data[0][:2] == "__":
                    col_dict["is_key"] = True
                elif col_data[0][:1] == "_":
                    col_dict["is_link"] = True
                if col_data[0][:1].lower() == "ω":
                    col_dict["is_audit"] = True
                if len(col_data) > 2:
                    if col_data[2] in (
                            "NOT NULL", "PRIMARY KEY",
                            "NOT NULL,", "PRIMARY KEY,"):
                        col_dict["constraint"] = col_data[2]
                    else:
                        col_dict["check"] = col_data[2]
                if len(col_data) > 3:
                    col_dict["check"] = col_data[3]
                # Remove trailing commas
                for c in ("type", "check", "constraint"):
                    if col_dict[c] is not None and col_dict[c][-1:] == ",":
                        col_dict[c] = col_dict[c][:-1]
                col_dict["check"] =\
                    self.convert_check_sql_to_meta(
                        col_dict["check"], col_dict["name"])
                ddl_out.append(col_dict)
            return ddl_out

        def get_edges_metadata(self,
                               p_tbl_nm: str,
                               p_col_nm: str) -> dict:
            """Pull edges info from metadata table for selected table and col.

            If col_nm is "__oid", "__uid" lookup using _col_*_from, _tbl_from,
              returning 1..many tables and columns that point to this target.
              May return multiple records.

            Otherwise, it is an "fk_ column, lookup using _col_to, _tbl_to,
              returning the table.__oid or .__id pointed to by this FK.
              Should return only one record.

            Args:
                p_tbl_nm (str): Full name of table on which column is found.
                p_col_nm (str): Name of column to search for.

            Returns:
                (dict): Information about linked columns and tables
            """
            def get_incoming_links(col_nm, tbl_nm):
                """Search for multiple links to an _oid or _uid field."""
                sql = """
SELECT _tbl_from, _col_db_from, _tbl_to, _col_to FROM ref_foreign_key
 WHERE _col_to = '{}' AND _tbl_to = '{}'
 AND ω_remv_dttm = '';""".format(col_nm, tbl_nm)
                return sql

            def get_outgoing_links(col_nm, tbl_nm):
                """Search for what (single) an FK_ field links to."""
                sql = """
SELECT _tbl_from, _col_db_from, _tbl_to, _col_to FROM ref_foreign_key
 WHERE _col_db_from = '{}' AND _tbl_from = '{}'
   AND ω_remv_dttm = '';""".format(col_nm, tbl_nm)
                return sql

            # get_edges_metadata() MAIN
            self.DB.connect_dmain()
            cur = self.DB.dmain_conn.cursor()
            if p_col_nm in ("__oid", "__uid"):
                sql = get_incoming_links(p_col_nm, p_tbl_nm)
            else:
                sql = get_outgoing_links(p_col_nm, p_tbl_nm)
            try:
                result = cur.execute(sql).fetchall()
                self.DB.disconnect_dmain()
            except IOError:
                self.DB.dmain_conn.close()
            edges = None
            if result != [] and result[0] != (None, None, None, None):
                edges = list()
                for rec in result:
                    edges.append(
                        {"from": "{}.{}".format(rec[0], rec[1]),
                         "to": "{}.{}".format(rec[2], rec[3])})
            return edges

    # Using the sub-classes
    # --------------------------------------------------

    def create_new_db(self):
        """Build the database based on Schema.

        This proceeds only if db_status token in <app>/log
        is removed or set to a value other than 'COMPLETE'.
        """
        newdb = self.BuildSchemaDB(self)
        db_path = newdb.verify_db_path()
        newdb.create_db(db_path)

    def query_meta_db(self) -> object:
        """Return sub-class object for running queries."""
        metadb = self.QueryDBMeta(self)
        return metadb

    # ================== OLDER CODE ========================

    def set_insert_sql(self,
                       p_tbl_name: str,
                       p_data_rec: dict,
                       p_audit_rec: dict) -> str:
        """Format SQL for an INSERT.

        Args:
            p_tbl_name (str): user, citizen
            p_data_rec (dict): mirrors a "data" dataclass
            p_audit_rec (dict): mirrors the "audit" dataclass

        Returns:
            str: formatted SQL to execute
        """
        sql_cols = list(p_data_rec.keys()) + list(p_audit_rec.keys())
        sql_cols_txt = ", ".join(sql_cols)
        sql_vals = ""
        for cnm, val in p_data_rec.items():
            if cnm == "encrypt_key":
                sql_vals += "?, "
            elif val is None:
                sql_vals += "NULL, "
            else:
                sql_vals += "'{}', ".format(val)
        for cnm, val in p_audit_rec.items():
            if val is None:
                sql_vals += "NULL, "
            else:
                sql_vals += "'{}', ".format(val)
        sql = "INSERT INTO {} ({}) VALUES ({});".format(p_tbl_name,
                                                        sql_cols_txt,
                                                        sql_vals[:-2])
        return(sql)

    def hash_data_values(self,
                         p_data_rec: dict,
                         p_audit_rec: dict) -> tuple:
        """Hash a data row as needed.

        Args:
            p_data_rec (dict): mirrors "data" dataclass
            p_audit_rec (dict): mirrors "audit" dataclass

        Returns:
            tuple of updated dicts ("audit": .., "data": ..)
        """
        data_rec = p_data_rec
        audit_rec = p_audit_rec
        hash_str = ""
        for cnm, val in p_data_rec.items():
            if (cnm != "encrypt_key"
                    and val not in (None, "None", "")):
                hash_str += str(val)
        audit_rec["hash_id"] = UT.get_hash(hash_str)
        return(data_rec, audit_rec)

    def query_latest(self,
                     p_tbl_name: str,
                     p_oid: str = None,
                     p_single: bool = True):
        """Get the latest non-deleted record(s) for selected table.

        Args:
            p_tbl_name (str): user, citizen
            p_oid (str): Required for citizen.
            p_single (bool): If True, return only latest row even if there are
                             multiples with NULL ts_remv. If False, return
                             all latest rows that have a NULL ts_remv.

        Returns:
            dict ("data": ..., "audit", ...) for user   OR
            list (of dicts like this ^) for citizen
        """
        db_recs = None
        if p_tbl_name == "user":
            db_recs = self.query_user(p_single)
        elif p_tbl_name == "citizen":
            db_recs = self.query_citizen_by_oid(p_oid, p_single)
        return db_recs

    def set_insert_data(self,
                        p_tbl_name: str,
                        p_data: dict) -> tuple:
        """Format one logically new row for main database.

        Args:
            p_tbl_name (str): user, citizen
            p_data (dict): mirrors a "data" dataclass

        Returns:
            tuple: (dict: "data":.., dict: "audit":..)
        """
        audit_rec = dict()
        for cnm in ST.AuditFields.keys():
            audit_rec[cnm] = copy(getattr(ST.AuditFields, cnm))
        audit_rec["uid"] = UT.get_uid()
        audit_rec["oid"] = UT.get_uid()
        dttm = UT.get_dttm('UTC')
        audit_rec["ts_init"] = dttm.curr_utc
        audit_rec["ts_updt"] = dttm.curr_utc
        audit_rec["ts_remv"] = None
        data_rec, audit_rec =\
            self.hash_data_values(p_data, audit_rec)
        recs = self.query_latest(p_tbl_name, audit_rec["oid"])
        if recs is not None:
            aud = UT.make_namedtuple("aud", recs["audit"])
            if aud.hash_id == audit_rec["hash_id"]:
                return(None, None)
        # if p_tbl_name == "user":
        #    p_data["encrypt_key"] = CI.set_key()
        #    data_rec = self.encrypt_data_values(p_data)
        return(data_rec, audit_rec)

    def set_upsert_data(self,
                        p_tbl_name: str,
                        p_data: dict,
                        p_oid: str) -> tuple:
        """Format one logically updated row to main database.

        Do nothing if no value-changes are detected.

        Args:
            p_tbl_name (str): user, citizen
            p_data (dict): that mirrors a "data" dataclass
            p_oid (str): Object ID of record to be updated

        Returns:
            tuple: (dict: "data":.., dict: "audit":..,
                    hash_id of previous version) if prev row exits, else
                    (None, None, None)
        """
        recs = self.query_latest(p_tbl_name, p_oid)
        aud = UT.make_namedtuple("aud", recs["audit"])
        dat = UT.make_namedtuple("dat", recs["data"])
        if not aud or aud.oid != p_oid:
            msg = TX.ew.f_upsert_failed
            raise Exception(ValueError, msg)
        audit_rec = UT.make_dict(ST.AuditFields.keys(), aud)
        audit_rec["uid"] = UT.get_uid()
        audit_rec['oid'] = copy(aud.oid)
        audit_rec['ts_init'] = copy(aud.ts_init)
        dttm = UT.get_dttm('UTC')
        audit_rec['ts_updt'] = dttm.curr_utc
        if p_tbl_name == "user"\
                and p_data["encrypt_key"] in (None, "None", ""):
            p_data["encrypt_key"] = copy(dat.encrypt_key)
        data_rec, audit_rec =\
            self.hash_data_values(p_data, audit_rec)
        # if p_tbl_name == "user":
        #    data_rec = self.encrypt_data_values(p_data)
        if aud.hash_id == audit_rec["hash_id"]:
            return(None, None, None)
        return(data_rec, audit_rec, aud.hash_id)

    def set_logical_delete_sql(self,
                               p_tbl_name: str,
                               p_oid: str):
        """Store non-NULL ts_remv on previously-active record.

        Args:
            p_tbl_name (str): user, citizen
            p_oid (str): Object ID of record to be marked as deleted.
        """
        recs = self.query_latest(p_tbl_name, p_oid, False)
        try:
            aud = UT.make_namedtuple("aud", recs[0]["audit"])
        except:     # noqa: E722
            aud = UT.make_namedtuple("aud", recs["audit"])
        dttm = UT.get_dttm('UTC')
        sql = "UPDATE {}".format(p_tbl_name)
        sql += " SET ts_remv = '{}'".format(dttm.curr_utc)
        sql += " WHERE uid = '{}';".format(aud.uid)
        return sql

    def execute_txn_sql(self,
                        p_db_action: str,
                        p_tbl_name: str,
                        p_sql: str,
                        p_oid: str = None,
                        p_encrypt_key: str = None):
        """Execute SQL to modify the database content.

        Args:
            p_db_action (str): add, upd, del
            p_tbl_name (str): user, citizen
            p_sql (string): the SQL statement to execute
            p_oid (string): if updating a record, used to delete previous
            p_encrypt_key (string): if adding or updating a user record
        """
        self.connect_dmain()
        cur = self.dmain_conn.cursor()
        if p_encrypt_key:
            try:
                cur.execute(p_sql, [p_encrypt_key])
                self.dmain_conn.commit()
            except IOError:
                self.dmain_conn.close()
        else:
            try:
                cur.execute(p_sql)
                self.dmain_conn.commit()
            except IOError:
                self.dmain_conn.close()
        self.dmain_conn.close()
        if p_db_action == "upd":
            self.write_db("del", p_tbl_name, None, p_oid)

    def write_db(self,
                 p_db_action: str,
                 p_tbl_name: str,
                 p_data: dict = None,
                 p_oid: str = None):
        """Write a record to the DB.

        Args:
            p_db_action (str -> str): add, upd, del
            p_tbl_name (str): user, citizen
            p_data (dict): mirrors a "data" dataclass. None if "del".
            p_oid (string): Required for upd, del. Default is None.
        """
        if p_db_action == "add":
            data_rec, audit_rec = self.set_insert_data(p_tbl_name, p_data)
        elif p_db_action == "upd":
            data_rec, audit_rec, prev_hash_id =\
                self.set_upsert_data(p_tbl_name, p_data, p_oid)
        sql = ""
        encrypt_key = ""
        if p_db_action in ("add", "upd"):
            if data_rec is not None and audit_rec is not None:
                sql = self.set_insert_sql(p_tbl_name, data_rec, audit_rec)
                encrypt_key = data_rec["encrypt_key"]\
                    if "encrypt_key" in data_rec.keys() else False
        elif p_db_action == "del":
            sql = self.set_logical_delete_sql(p_tbl_name, p_oid)
        if sql:
            self.execute_txn_sql(p_db_action, p_tbl_name, sql,
                                 p_oid, encrypt_key)

    def format_query_result(self,
                            p_tbl_name: str,
                            p_result: list) -> list:
        """Convert sqlite3 results into local format.

        Sqlite returns each row as a tuple in a list.
        When no rows are found, sqlite returns a tuple with
          all values set to None, which is odd since then
          we get a rowcount > 0. Sqlite also returns an extra
          timestamp at the end of the tuple.
        Cast each row of returned data into a namedtuple that
          mirrors a Struct DB schema dataclass. Put those in a list.
          Ignore row if it has all None values.

        This formatter assumes no derived columns. Use it only for
         "straight" queries against the database.

        Args:
            p_tbl_name (str): user, citizen
            p_result (sqlite result set -> list): list of tuples

        Returns:
            list: each row is dict of dicts keyed by "data", "audit",
                  mirroring appropriate dataclass DB structures
        """
        def init_recs():
            dat_rec = dict()
            aud_rec = dict()
            for cnm in dat_keys:
                dat_rec[cnm] = copy(getattr(dat_dflt, cnm))
            for cnm in aud_keys:
                aud_rec[cnm] = copy(getattr(ST.AuditFields, cnm))
            return (dat_rec, aud_rec)

        data_out = list()
        dat_keys = self.get_attributes(p_tbl_name)
        aud_keys = ST.AuditFields.keys()
        val_nms = dat_keys + aud_keys
        dat_dflt = ST.UserFields if p_tbl_name == 'user'\
            else ST.CitizenFields
        max_ix = len(val_nms) - 1

        for rx, in_row in enumerate(p_result):
            all_none = True
            dat_rec, aud_rec = init_recs()
            for ix, val in enumerate(in_row):
                if ix > max_ix:
                    break
                all_none = False if val is not None else all_none
                val_nm = val_nms[ix]
                if val_nm in dat_keys:
                    dat_rec[val_nm] = val
                else:
                    aud_rec[val_nm] = val
            if not all_none:
                data_out.append({"data": dat_rec, "audit": aud_rec})
        # if p_tbl_name == "user" and len(data_out) > 0:
        #    data_out[0]["data"] =\
        #        self.decrypt_user_data(data_out[0]["data"])
        return data_out

    def format_query_sql(self,
                         p_tbl_name: str,
                         p_single: bool = True):
        """Format a SELECT query, with option to return only latest row.

        Returns all cols from selected table.

        Args:
            p_tbl_name (str)
            p_single (bool): If True, return only the latest row

        Returns:
            dict: of (dicts keyed by "data", "audit")  or
            list of dicts like that ^  or
            None if no rows found
        """
        data_cols = ST.UserFields.keys() if p_tbl_name == "user"\
            else ST.CitizenFields.keys()
        val_nms = data_cols + ST.AuditFields.keys()
        val_nms_txt = ", ".join(val_nms)
        sql = "SELECT {}, ".format(val_nms_txt)
        if p_single:
            sql += "MAX(ts_updt)"
        else:
            sql = sql[:-2]
        sql += " FROM {} ".format(p_tbl_name)
        sql += "WHERE ts_remv IS NULL;"
        recs = self.execute_query_sql(p_tbl_name, sql, p_single)
        return recs

    def execute_query_sql(self,
                          p_tbl_name: str,
                          p_sql: str,
                          p_single: bool = True):
        """Execute a SELECT query, with option to return only latest row.

        Args:
            p_sql (str) DB SELECT to execute
            p_tbl_name (str)
            p_single (bool): If True, return only the latest row

        Returns:
            dict: of (dicts keyed by "data", "audit")  or
            list of dicts like that ^  or
            None if no rows found
        """
        self.connect_dmain()
        cur = self.dmain_conn.cursor()
        result = cur.execute(p_sql).fetchall()
        self.disconnect_dmain()
        data_recs = self.format_query_result(p_tbl_name, result)
        if len(data_recs) < 1:
            data_recs = None
        elif p_single:
            data_recs = data_recs[0]
        return data_recs

    def query_user(self, p_single=True) -> dict:
        """Run read-only query against the user table.

        Args:
            p_single (bool): If True, return only the latest row

        Returns:
            dict: of (dicts keyed by "data", "audit")
        """
        return self.format_query_sql("user", p_single)

    def query_citizen_by_oid(self,
                             p_oid: str,
                             p_single: bool = True) -> dict:
        """Run read-only query against the citizen table.

        Return latest non-deleted record that matches on PID.

        Args:
            p_oid (str): efriends DB unique object ID
            p_single (bool): If True, return only latest row

        Returns:
            dict: of (dicts keyed by "data", "audit")
        """
        val_nms = list(ST.CitizenFields.keys()) +\
            list(ST.AuditFields.keys())
        val_nms_txt = ", ".join(val_nms)
        sql = "SELECT {}, ".format(val_nms_txt)
        if p_single:
            sql += " MAX(ts_updt)"
        else:
            sql = sql[:-2]
        sql += " FROM citizen WHERE oid = '{}'".format(str(p_oid))
        sql += " AND ts_remv is NULL;"
        recs = self.execute_query_sql("citizen", sql, p_single=True)
        return recs

    def query_citizen_by_profile_id(self,
                                    p_profile_id: str) -> dict:
        """Run read-only query against the citizen table.

        Return latest non-deleted record that matches on profile ID.

        Args:
            p_profile_id (str): eRepublik Identifier for a citizen

        Returns:
            dict: of (dicts keyed by "data", "audit")
        """
        val_nms = list(ST.CitizenFields.keys()) +\
            list(ST.AuditFields.keys())
        val_nms_txt = ", ".join(val_nms)
        sql = "SELECT {}, ".format(val_nms_txt)
        sql += " MAX(ts_updt) FROM citizen"
        sql += " WHERE profile_id = '{}'".format(str(p_profile_id))
        sql += " AND ts_remv is NULL;"
        recs = self.execute_query_sql("citizen", sql, p_single=True)
        return recs

    def query_citizen_by_name(self,
                              p_citizen_nm: str) -> dict:
        """Run read-only query against the citizen table.

        Return latest non-deleted record that matches on citizen name.

        Args:
            p_citizen_nm (str): eRepublik citizen name

        Returns:
            dict: of (dicts keyed by "data", "audit")
        """
        val_nms = list(ST.CitizenFields.keys()) +\
            list(ST.AuditFields.keys())
        val_nms_txt = ", ".join(val_nms)
        sql = "SELECT {}, ".format(val_nms_txt)
        sql += " MAX(ts_updt) FROM citizen"
        sql += " WHERE name = '{}'".format(str(p_citizen_nm))
        sql += " AND ts_remv is NULL;"
        recs = self.execute_query_sql("citizen", sql, p_single=True)
        return recs

    def query_for_profile_id_list(self) -> list:
        """Return a list of all active citizen profile IDs.

        Returns:
            list: of eRepublik citizen profile IDs
        """
        sql = "SELECT profile_id "
        sql += "FROM citizen WHERE ts_remv IS NULL;"
        recs = self.execute_query_sql("citizen", sql, p_single=False)
        id_list = list()
        for row in recs:
            id_list.append(row['data']['profile_id'])
        return id_list

    def query_citizen_sql(self, sql_file_name: str) -> list:
        """Run SQL read in from a file.

        Returns:
            list of tuples. First tuple contains headers, the rest values.
        """
        sql_file = path.join(self.APP, TX.db.sask_db, sql_file_name)
        with open(sql_file) as sqf:
            sql = sqf.read()
        sqf.close()
        self.connect_dmain()
        cur = self.dmain_conn.cursor()
        result = cur.execute(sql).fetchall()
        # Much nicer than the formatting I was doing earlier!
        headers = [meta_h[0] for meta_h in cur.description]
        self.disconnect_dmain()
        result.insert(0, tuple(headers))
        return(result)

    # ================  untested code =========================
    # Add rebuild_all_dbs (from DDL SQL code)

    def destroy_all_dbs(self, db_path: str):
        """Delete all database files.

        Args:
            db_path (string): Full path to the .db file

        Returns:
            bool: True if db_path legit points to a file

        @DEV - Add logging messages
        @DEV - Destroy only specific DBs
        """
        for d_path in [path.join(self.APP, TX.db.sask_db),
                       path.join(self.APP, TX.db.sask_bkup),
                       path.join(self.APP, TX.db.sask_arcv)]:
            remove(d_path)

    def purge_rows(self, p_oids: list, p_cursor: object):
        """Physically delete a row from citizen table on main db.

        Args:
            p_oids (list): (oids, ts_remv) tuples associated
                with rows to physically delete
            cur (object): a cursor on the main database
        """
        for row in p_oids:
            d_oid = row[0]
            d_ts_remv = row[1]
            sql = "DELETE citizen WHERE uid = '{}' ".format(d_oid)
            sql += "AND ts_remv = '{}';".format(d_ts_remv)
            p_cursor.execute(sql)

    def purge_db(self):
        """Remove rows from main db citizen table."""
        self.archive_db()

        # Modify to use an appropriate purge threshold, not just
        # "deleted before today"
        dttm = UT.get_dttm()
        sql = "SELECT oid, ts_remv FROM citizen "
        sql += "WHERE ts_remv < '{}' ".format(dttm.curr_utc)
        sql += "AND ts_remv IS NOT NULL;"

        self.connect_dmain()
        cur = self.dmain_conn.cursor()
        oid_list = [row for row in cur.execute(sql)]
        self.purge_rows(cur, oid_list)
        self.dmain_conn.commit()
        self.disconnect_dmain()
