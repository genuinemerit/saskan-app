#!/usr/bin/python3
# coding: utf-8

"""Manage data for saskan_data app using sqlite3.
   - Set all DB datatypes to Text, to begin with.
   - Later, add hash_id and audit fields.

:module:    io_db.py
:class:     DataBase/0
:author:    GM (genuinemerit @ pm.me)
:configs:
- configs/d_dirs.json
"""
# trunk-ignore(bandit/B403)
import pickle
from re import S
import pendulum
import shutil
import sqlite3 as sq3

from os import path
from pprint import pprint as pp    # noqa: F401
# from pydantic
from io_file import FileIO

from copy import copy
from pathlib import Path

FI = FileIO()


class DataBase(object):
    """Support Sqlite3 database setup, usage, maintenance.

    @DEV:
    - Add methods to generate SQL for CREATE, DROP, INSERT, UPDATE, DELETE
      from Pydantic models in io_data.py module.
    """

    def __init__(self):
        """Initialize Dbase object.
        """
        self.DB_PATH = path.join(FI.D['APP']['root'],
                                 FI.D['APP']['dirs']['db'])
        self.DB = path.join(self.DB_PATH, FI.D['DB']['main'])
        self.DB_BKUP = path.join(self.DB_PATH, FI.D['DB']['bkup'])
        self.db_conn = None

    # Generate SQL files from Pydantic models
    # Prototype -- not tested.
    # ===========================================

    def generate_create_sql(self,
                            p_table_name: str,
                            p_constraints: dict,
                            p_col_fields: dict):
        """
        Generate SQL CREATE TABLE code from a Pydantic data model.
        :args:
        - p_table_name (str) Name of table to create SQL for
        - p_constraints (dict) Dict of constraints for the table
        - p_col_fields (dict) Dict of column fields for the table
        :writes:
        - SQL file to [APP]/sql/CREATE_[p_table_name].sql
        """
        def set_data_type(col_nm, pyd_value, p_constraints):
            sql = col_nm
            # 'DT' constraint is used for BLOB, JSON and customize data types
            # BLOB and JSON are supported by SQLITE
            # customize data types are not supported by SQLITE, will be
            # converted to JSON with annotations. For example:
            # CoordXYZ --> vector: dict{'x': 0.0, 'y': 0.0, 'z': 0.0}
            # (or maybe I should get more specific... hmmmm.. they will all
            #  be converted to JSON, so use 'JSON' instead of DT. The
            #  annotations will be tied to Pydantic data models created in
            #  io_data.py... may be able to derive JSON directly from them.)
            if 'JSON' in p_constraints.keys() \
            and col_nm in p_constraints['JSON']:
                model_fields = copy(p_constraints['JSON'][col_nm].model_fields)

                pp(("JSON data type fields: ", model_fields))
                # Break out the sub-types of Pydantic model into separate
                # columns, or maybe just store them as JSON in a single column
                # @DEV -- pick up here
                # things to try:
                # -- recursive call to set_data_type to create sub-columns
                # -- convert to JSON and store in a single column (still need to
                # pull out the datatype and default values if any)
                # -- and think about how this might be handled in select, update,
                # insert actions

                sql += f' {p_constraints['JSON'][col_nm]}'
            else:
                # otherwise, convert Pydantic data type to SQLITE data type
                col_datatype = pyd_value.annotation.__name__
                for pyd_type in (('str', 'TEXT'),
                                 ('int', 'INTEGER'),
                                 ('float', 'NUMERIC')):
                    if col_datatype == pyd_type[0]:
                        sql += f" {pyd_type[1]}"
                        break
            return sql

        def set_data_rule(sql, col_nm, pyd_value, p_constraints):
            for pyd_rule in (('PK', 'PRIMARY KEY'),
                             ('UQ', 'UNIQUE'),
                             ('IX', 'INDEXED')):
                if pyd_rule[0] in p_constraints.keys() \
                and col_nm in p_constraints[pyd_rule[0]]:
                    sql += f' {pyd_rule[1]}'
            if pyd_value.is_required():
                sql+= ' NOT NULL'
            return sql

        def set_default(sql, pyd_value):
            col_default = str(pyd_value.get_default()).strip()
            if col_default not in (None, 'PydanticUndefined'):
                if pyd_value.annotation.__name__ == 'str':
                    sql += f" DEFAULT '{col_default}'"
                else:
                    sql += f" DEFAULT {col_default}"
            return sql

        def set_check_constraints(sql, col_nm, p_constraints):
            if 'CK' in p_constraints.keys() \
            and col_nm in p_constraints['CK']:
                sql += f' CHECK({col_nm} IN ('
                for ck_val in p_constraints['CK'][col_nm]:
                    sql += f"'{ck_val}', "
                sql = sql[:-2] + '))'
            return sql

        def set_foreign_key(sqlns, p_constraints):
            if 'FK' in p_constraints.keys():
                for col, ref in p_constraints['FK'].items():
                    sqlns.append(f"FOREIGN KEY ({col}) REFERENCES" +
                                f" ({ref[0]}){ref[1]} " +
                                "ON DELETE CASCADE")
            return sqlns

        # generate_create_sql main
        # ============================
        sqlns = []
        for col_nm, pyd_value in p_col_fields.items():
            sql = set_data_type(col_nm, pyd_value, p_constraints)
            sql = set_data_rule(sql, col_nm, pyd_value, p_constraints)
            sql = set_default(sql, pyd_value)
            sql = set_check_constraints(sql, col_nm, p_constraints)
            sqlns.append(sql)
        sqlns = set_foreign_key(sqlns, p_constraints)
        sql = f"CREATE TABLE IF NOT EXISTS {p_table_name} (\n" +\
              f"{',\n'.join(sqlns)});\n"
        FI.write_file(
            path.join(self.DB_PATH, f"CREATE_{p_table_name}.sql"), sql)

    def generate_drop_sql(self,
                          p_table_name: str):
        """Generate SQL DROP TABLE code.
        :args:
        - p_table_name (str) Name of table to drop
        :writes:
        - SQL file to [APP]/sql/DROP_[p_table_name].sql
        """
        sql = f"DROP TABLE IF EXISTS {p_table_name};\n"
        FI.write_file(
            path.join(self.DB_PATH, f"DROP_{p_table_name}.sql"), sql)

    def generate_insert_sql(self,
                            p_table_name: str,
                            p_col_fields: dict):
        """Generate SQL INSERT code.
        :args:
        - p_table_name (str) Name of table to insert into
        - p_col_fields (dict) Dict of column fields for the table
        :writes:
        - SQL file to [APP]/sql/INSERT_[p_table_name].sql
        """
        sql = f"INSERT INTO {p_table_name} " +\
              f"(\n{',\n'.join(p_col_fields.keys())})" +\
              " VALUES (" +\
              f"{', '.join(['?' for i in range(len(p_col_fields))])});\n"
        FI.write_file(
            path.join(self.DB_PATH, f"INSERT_{p_table_name}.sql"), sql)

    def generate_select_all_sql(self,
                                p_table_name: str,
                                p_constraints: dict,
                                p_col_fields: dict):
        """Generate SQL SELECT code.
        :args:
        - p_table_name (str) Name of table to select from
        - p_constraints (dict) Dict of constraints for the table
        - p_col_fields (dict) Dict of column fields for the table
        :writes:
        - SQL file to [APP]/sql/SELECT_ALL_[p_table_name].sql
        """
        sql = f"SELECT {',\n'.join(p_col_fields.keys())}\nFROM {p_table_name}"
        if "ORDER" in p_constraints.keys():
            sql += f"\nORDER BY {', '.join(p_constraints['ORDER'])}"
        sql += ';\n'
        FI.write_file(
            path.join(self.DB_PATH, f"SELECT_ALL_{p_table_name}.sql"), sql)

    def generate_update_sql(self,
                            p_table_name,
                            p_constraints,
                            p_col_fields):
        """Generate SQL UPDATE code.
        :args:
        - p_table_name (str) Name of table to update
        - p_constraints (dict) Dict of constraints for the table
        - p_col_fields (dict) Dict of column fields for the table
        :writes:
        - SQL file to [APP]/sql/UPDATE_[p_table_name].sql
        """
        sql = f"UPDATE {p_table_name} SET\n" +\
                f"{',\n'.join([f'{col}=?' for col in p_col_fields.keys()])}" +\
                f"\nWHERE {p_constraints['PK'][0]}=?;\n"
        FI.write_file(
            path.join(self.DB_PATH, f"UPDATE_{p_table_name}.sql"), sql)

    def generate_sql(self,
                     p_data_model: object):
        """
        Generate full set of SQL code from a Pydantic data model.
        :args:
        - p_data_model (inherited from BaseModel) Pydantic data model class
        """
        model_fields = copy(p_data_model.model_fields) # type: ignore
        table_name = model_fields['tablename'].get_default()
        constraints = p_data_model.constraints() # type: ignore
        col_fields = {nm: val for nm, val in model_fields.items()
                      if nm != 'tablename'}
        self.generate_create_sql(table_name, constraints, col_fields)
        self.generate_drop_sql(table_name)
        self.generate_insert_sql(table_name, col_fields)
        self.generate_select_all_sql(table_name, constraints, col_fields)
        self.generate_update_sql(table_name, constraints, col_fields)

    # Backup, Archive and Restore
    # ===========================================

    def backup_db(self):
        """Copy main DB file to backup location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        self.execute_insert(
            'INSERT_BKUPS',
            (bkup_dttm, self.DB_BKUP, 'backup',
             pickle.dumps({'files': [self.DB_BKUP]})))
        shutil.copyfile(self.DB, self.DB_BKUP)

    def archive_db(self):
        """Copy main DB file to archive location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        file_nm = 'SASKAN_' + bkup_dttm + '.arcv'
        bkup_nm = path.join(self.DB_PATH, file_nm)
        self.execute_insert(
            'INSERT_BKUPS', (bkup_dttm, bkup_nm, 'archive',
                             pickle.dumps({'files': [bkup_nm]})))
        shutil.copyfile(self.DB, bkup_nm)

    def restore_db(self):
        """Copy backup DB file to main location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        self.execute_insert(
            'INSERT_BKUPS', (bkup_dttm, self.DB, 'restore',
                             pickle.dumps({'files': [self.DB]})))
        shutil.copyfile(self.DB_BKUP, self.DB)

    # DataBase Connections
    # ===========================================

    def disconnect_db(self):
        """Drop DB connection to SASKAN_self."""
        if hasattr(self, "db_conn") and self.db_conn is not None:
            try:
                self.cur.close()
                self.db_conn.close()
            except RuntimeWarning:
                pass
        self.db_conn = None

    def connect_db(self,
                   p_db_nm: str = 'main'):
        """Open DB connection to SASKAN_self.
        :args:
        - p_db_nm (str) Optional. Default is 'main'.
          If set to 'bkup' then use the backup self.
          If neither, then connect to main self.
        Indicate that the DB should help to maintain referential
        integrity for foreign keys.
        This will create a DB file at the specified location
        if one does not already exist.
        :sets:
        - db_conn: the database connection
        - cur: cursor for the connection
        """
        self.disconnect_db()
        self.SASKAN_DB = self.DB if p_db_nm == 'arcv'\
            else self.DB_BKUP if p_db_nm == 'bkup'\
            else self.DB
        self.db_conn = sq3.connect(self.SASKAN_DB)  # type: ignore
        self.db_conn.execute("PRAGMA foreign_keys = ON;")
        self.cur: sq3.Cursor = self.db_conn.cursor()

    # SQL Helpers
    # ===========================================

    def has_tables(self) -> bool:
        """Check if the database has any tables.
        N.B. This method assumes that a connection and
           a cursor have already been established for
           the database file.
        :returns:
        - (bool) True if there are tables, False if not
        """
        self.cur.execute("SELECT name FROM sqlite_master\
                          WHERE type='table'")
        tables = self.cur.fetchall()
        return True if len(tables) > 0 else False

    def get_sql_file(self,
                     p_sql_nm: str) -> str:
        """Read SQL from named file.
        :args:
        - p_sql_nm (str) Name of  SQL file in [APP]/sql
        :returns:
        - (str) Content of the SQL file
        """
        sql_nm = str(p_sql_nm).upper()
        if '.SQL' not in sql_nm :
            sql_nm += '.SQL'
        sql_path = path.join(FI.D['APP']['root'],
                             FI.D['APP']['dirs']['db'],
                             sql_nm)
        SQL: str = FI.get_file(sql_path)
        if SQL == '':
            raise Exception(f"SQL file {sql_nm} is empty.")
        return SQL

    def get_db_columns(self,
                       p_tbl_nm: str = '',
                       p_sql_select: str = '') -> list:
        """ For currently open connection and cursor, for the
        specified SQL SELECT file, return a list of the table's
        column names.
        :args:
        - p_tbl_nm (str) Optional. If provided, use this instead
          of scanning the SQL code.
        - p_sql_select (str) Optional.
            Text content of a well-structured SQL SELECT file,
            where table name is the last word in the
          first line. Use this if p_tbl_nm is not provided.
        :returns:
        - (list) of column names for the table
        """
        if p_tbl_nm in (None, ''):
            SQL = p_sql_select
            tbl_nm = SQL.split('\n')[0].split(' ')[-1]
        else:
            tbl_nm = p_tbl_nm
        self.cur.execute(f"PRAGMA table_info({tbl_nm})")
        cols = self.cur.fetchall()
        col_nms = [c[1] for c in cols]
        return col_nms

    # Executing SQL Scripts
    # ===========================================

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
        SQL: str = self.get_sql_file(p_sql_nm)
        COLS: list = self.get_db_columns(p_sql_select=SQL)
        self.cur.execute(SQL)
        DATA: list = [r for r in self.cur.fetchall()]
        if len(DATA) == 0:
            result: dict = {col: [] for col in COLS}
        else:
            result: dict = {col: [row[i] for row in DATA]
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

        print(f"In execute_dml, p_sql_nm = {p_sql_nm}")

        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)

        print(f"In execute_dml, SQL = {SQL}\n")

        if SQL.count(';') > 1:
            self.cur.executescript(SQL)
        else:
            self.cur.execute(SQL)
        if self.db_conn is not None:
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
            - Any object values have already been pickled
              (though why not just store them as text?)
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_values (tuple): n-tuple of values to insert
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_values)
        self.db_conn.commit()   # type: ignore
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
        if self.db_conn is not None:
            self.db_conn.commit()   # type: ignore
        self.disconnect_db()

    # =====================================================================
    # Saskan Database Management -- Backup, archive, restart
    # =====================================================================

    def boot_saskan_db(self):
        """Create SASKAN.db database, if it does not already exist.
        - If it already exists and has tables, back it up and then boot it.
        - Do not wipe out any existing archives.
        - Scan self.DB_PATH for DROP and CREATE SQL files.
        """
        db_file_path = Path(self.DB)
        if db_file_path.exists():
            self.connect_db()
            if self.has_tables():
                self.backup_db()

        sql_files = FI.scan_dir(self.DB_PATH, 'DROP*.SQL')
        for sql in sql_files:
            self.execute_dml(sql.name)
        sql_files = FI.scan_dir(self.DB_PATH, 'CREATE*.SQL')
        for sql in sql_files:
            self.execute_dml(sql.name)

        self.disconnect_db()
        
