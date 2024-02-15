#! python
"""

:module:    io_db.py
:class:     DataBase/0
:author:    GM (genuinemerit @ pm.me)
:configs:
- configs/d_dirs.json

Manage data for saskan_data app using sqlite3.
"""
import pendulum
import shutil
import sqlite3 as sq3

from collections import OrderedDict
from copy import copy
from pathlib import Path
from os import path
from pprint import pprint as pp    # noqa: F401

from io_file import FileIO
from io_shell import ShellIO

FI = FileIO()
SI = ShellIO()


class DataBase(object):
    """Support Sqlite3 database setup, usage, maintenance.
    """

    def __init__(self):
        """
        Initialize DataBase object from configs.
        """
        self.DB_PATH = path.join(FI.D['APP']['root'],
                                 FI.D['APP']['dirs']['db'])
        self.DB = path.join(self.DB_PATH, FI.D['DB']['main'])
        self.DB_BKUP = path.join(self.DB_PATH, FI.D['DB']['bkup'])
        self.db_conn = None

    # Generate SQL files from Pydantic models
    # ===========================================
    def set_sql_data_type(self,
                          p_def_value: object,
                          p_constraints: dict) -> str:
        """
        Convert default value data type to SQLITE data type.
        :args:
        - p_def_value (object) default value
        - p_constraints (dict) Dict of constraints for the table
        :returns:
        - (str) SQLITE data type
        """
        sql = ''
        if 'JSON' in p_constraints.get('JSON', []):
            sql = ' JSON'
        else:
            field_type = type(p_def_value).__name__
            data_types = {
                str: ' TEXT',
                bool: ' BOOLEAN',
                float: ' NUMERIC',
                int: ' INTEGER'
            }
            sql = data_types.get(field_type, ' TEXT')
        return sql

    def set_sql_default(self,
                        p_def_value: object,
                        p_data_type: str) -> str:
        """
        Extract SQL default value from Pydantic data object.
        :args:
        - p_def_value (object) Pydantic value object
        - p_data_type (str) SQLITE data type
        :returns:
        - (str) SQLITE SQL DEFAULT clause
        """
        sql = ''
        col_default = str(p_def_value).strip()
        if col_default == 'True':
            col_default = '1'
        elif col_default == 'False':
            col_default = '0'
        elif p_data_type not in ('INTEGER', 'NUMERIC'):
            col_default = f"'{col_default}'"
        sql = f" DEFAULT {col_default}"
        return sql

    def set_sql_comment(self,
                        p_def_value: object) -> str:
        """
        Convert constraint annotations to SQLITE COMMENT.
        :args:
        - p_def_value (object) may be a class-object value
          if so, then add a comment
        :returns:
        - (str) SQLITE COMMENT
        """
        sql = ''
        for data_type in ['rect', 'pg', 'color', 'surface']:
            if data_type in str(p_def_value):
                sql += f",   -- {str(p_def_value)} object"
        return sql

    def set_sql_column_group(self,
                             p_col_nm: str,
                             p_constraints: dict,
                             p_col_names: list) -> tuple:
        """
        Generate SQL CREATE TABLE code from a data model
        for specialized data types, by splitting them into separate
        columns grouped with a similar name.
        :args:
        - p_col_nm (str) Name of customized data objects
        - p_constraints (dict) Dict of constraints for the table
        - p_col_names (list) List of column names already processed
        :returns: tuple of:
        - (str) One or more lines of SQL code
        - (list) Updated list of column names already processed
        """
        sql = ''
        if 'GROUP' in p_constraints and p_col_nm in p_constraints['GROUP']:
            group_class = copy(p_constraints['GROUP'][p_col_nm])
            sql += f"-- GROUP {p_col_nm}: {str(group_class)}\n"
            sub_model = {k: v for k, v in group_class.__dict__.items()
                         if not k.startswith('_')}
            for k, v in sub_model.items():
                g_col_nm = f'{p_col_nm}_{k}'
                p_col_names.append(g_col_nm)
                sql += f' {g_col_nm}'
                data_type = self.set_sql_data_type(v, p_constraints)
                sql += data_type
                sql += self.set_sql_default(v, data_type.split(' ')[1])
                sql += self.set_sql_comment(v)
                sql += ',\n'
        return (sql, p_col_names)

    def set_sql_foreign_keys(self,
                             p_constraints: dict) -> str:
        """
        Generate SQL FOREIGN KEY code from a Pydantic data model.
        :args:
        - p_constraints (dict) Dict of constraints for the table
        :returns:
        - (str) One or more lines of SQL code
        """
        sql = ''
        foreign_keys = p_constraints.get('FK', {})
        for col, ref in foreign_keys.items():
            table_name, column_name = ref[0], ref[1]
            sql += f"FOREIGN KEY ({col}) REFERENCES {table_name}" +\
                   f"({column_name}) ON DELETE CASCADE,\n"
        return sql

    def set_sql_primary_key(self,
                            p_constraints: dict) -> str:
        """
        Generate SQL PRIMARY KEY code from a Pydantic data model.
        :args:
        - p_constraints (dict) Dict of constraints for the table
        :returns:
        - (str) One or more lines of SQL code
        """
        primary_key = p_constraints.get('PK')
        if primary_key:
            sql = f"PRIMARY KEY ({', '.join(primary_key)}),\n"
        else:
            sql = ''
        return sql

    def set_sql_check_constraints(self,
                                  p_constraints: dict) -> str:
        """
        Convert CHECK constraint annotations to a SQLITE CHECK rule
        that validates against a list of allowed values, similar to ENUM.
        For example:
        CHECK (col_name IN ('val1', 'val2', 'val3'))
        :args:
        - p_constraints (dict) Dict of constraints for the table
        :returns:
        - (str) SQLITE CHECK rule
        """
        check_constraints = p_constraints.get('CK', {})
        sql = ''
        for ck_col, ck_vals in check_constraints.items():
            check_values = ', '.join(map(str, ck_vals))
            sql += f"CHECK ({ck_col} IN ({check_values})),\n"
        return sql

    def generate_create_sql(self,
                            p_table_nm: str,
                            p_constraints: dict,
                            p_col_fields: dict) -> list:
        """
        Generate SQL CREATE TABLE code from data model.
        :args:
        - p_table_name (str) Name of table to create SQL for
        - p_constraints (dict) Dict of constraints for the table
        - p_col_fields (dict) Dict of column fields, default values
        :writes:
        - SQL file to [APP]/sql/CREATE_[p_table_name].sql
        :returns:
        - (list) List of column names
        """
        col_names = []
        sqlns = []

        for col_nm, def_value in p_col_fields.items():
            sql, col_names =\
                self.set_sql_column_group(col_nm, p_constraints, col_names)

            if not sql:
                col_names.append(col_nm)
                data_type_sql =\
                    self.set_sql_data_type(def_value, p_constraints)
                default_sql =\
                    self.set_sql_default(def_value,
                                         data_type_sql.split(' ')[1])
                comment_sql = self.set_sql_comment(def_value)
                sql = f"{col_nm}{data_type_sql}{default_sql}{comment_sql},\n"

            sqlns.append(sql)

        sqlns.append(self.set_sql_check_constraints(p_constraints))
        sqlns.append(self.set_sql_foreign_keys(p_constraints))
        sqlns.append(self.set_sql_primary_key(p_constraints))
        sqlns[-1] = sqlns[-1][:-2]

        sql = f"CREATE TABLE IF NOT EXISTS {p_table_nm} " +\
              f"(\n{''.join(sqlns)});\n"
        FI.write_file(path.join(self.DB_PATH, f"CREATE_{p_table_nm}.sql"), sql)

        return col_names

    def generate_drop_sql(self,
                          p_table_name: str):
        """
        Generate SQL DROP TABLE code.
        :args:
        - p_table_name (str) Name of table to drop
        :writes:
        - SQL file to [APP]/sql/DROP_[p_table_name].sql
        """
        sql = f"DROP TABLE IF EXISTS {p_table_name};\n"
        file_path = path.join(self.DB_PATH, f"DROP_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_insert_sql(self,
                            p_table_name: str,
                            p_col_names: list):
        """
        Generate SQL INSERT code.
        :args:
        - p_table_name (str) Name of table to insert into
        - p_col_names (list) List of column names for the table
        :writes:
        - SQL file to [APP]/sql/INSERT_[p_table_name].sql
        """
        placeholders = ', '.join(['?' for _ in p_col_names])
        columns = ',\n'.join(p_col_names)
        sql = f"INSERT INTO {p_table_name} (\n{columns}) " +\
              f"VALUES ({placeholders});\n"
        file_path = path.join(self.DB_PATH, f"INSERT_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_select_all_sql(self,
                                p_table_name: str,
                                p_constraints: dict,
                                p_col_names: list):
        """
        Generate SQL SELECT ALL code.
        :args:
        - p_table_name (str) Name of table to select from
        - p_constraints (dict) Dict of constraints for the table
        - p_col_names (list) List of column names for the table
        :writes:
        - SQL file to [APP]/sql/SELECT_ALL_[p_table_name].sql
        """
        columns = ',\n'.join(p_col_names)
        sql = f"SELECT {columns}\nFROM {p_table_name}"

        if "ORDER" in p_constraints:
            order_by = ', '.join(p_constraints["ORDER"])
            sql += f"\nORDER BY {order_by}"

        sql += ';\n'

        file_path = path.join(self.DB_PATH, f"SELECT_ALL_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_select_pk_sql(self,
                               p_table_name: str,
                               p_constraints: dict,
                               p_col_names: list):
        """
        Generate SQL SELECT WHERE = [PK] code.
        :args:
        - p_table_name (str) Name of table to select from
        - p_constraints (dict) Dict of constraints for the table
        - p_col_names (list) List of column names for the table
        :writes:
        - SQL file to [APP]/sql/SELECT_BY_PK_[p_table_name].sql
        """
        pk_conditions = ' AND '.join([f'{col}=?' for col in p_constraints['PK']])
        sql = f"SELECT {', '.join(p_col_names)}\n" +\
              f"FROM {p_table_name}\nWHERE {pk_conditions}"

        if "ORDER" in p_constraints:
            order_by = ', '.join(p_constraints['ORDER'])
            sql += f"\nORDER BY {order_by}"

        sql += ';\n'

        file_path = path.join(self.DB_PATH, f"SELECT_BY_PK_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_update_sql(self,
                            p_table_name: str,
                            p_constraints: dict,
                            p_col_names: list):
        """
        Generate SQL UPDATE code.
        - If more than one PK, then use AND logic in the WHERE clause
        :args:
        - p_table_name (str) Name of table to update
        - p_constraints (dict) Dict of constraints for the table
        - p_col_names (list) Dict of column names for the table
        :writes:
        - SQL file to [APP]/sql/UPDATE_[p_table_name].sql
        """
        pk_conditions =\
            ' AND '.join([f'{col}=?' for col in p_constraints['PK']])
        set_columns =\
            ',\n'.join([f'{col}=?' for col in p_col_names
                        if col not in p_constraints['PK']])

        sql = f"UPDATE {p_table_name} SET\n{set_columns}\n" +\
              f"WHERE {pk_conditions};\n"

        file_path = path.join(self.DB_PATH, f"UPDATE_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_delete_sql(self,
                            p_table_name: str,
                            p_constraints: dict):
        """
        Generate SQL DELETE code.
        - If more than one PK, then use AND logic in the WHERE clause
        :args:
        - p_table_name (str) Name of table to delete from
        - p_constraints (dict) Dict of constraints for the table
        :writes:
        - SQL file to [APP]/sql/DELETE_[p_table_name].sql
        """
        pk_conditions =\
            ' AND '.join([f'{col}=?' for col in p_constraints['PK']])
        sql = f"DELETE FROM {p_table_name}\nWHERE {pk_conditions};\n"
        file_path = path.join(self.DB_PATH, f"DELETE_{p_table_name}.sql")
        FI.write_file(file_path, sql)

    def generate_sql(self,
                     p_data_model: object):
        """
        Generate full set of SQL code from a Pydantic data model.
        :args:
        - p_data_model: data model class object
        """
        model = {k: v for k, v in p_data_model.__dict__.items()
                 if not k.startswith('_') or k == '_tablename'}
        table_name = model.pop('_tablename', None)
        constraints = {k: v for k, v in model.pop('Constraints', {}).items()
                       if not k.startswith('_')}
        col_names = self.generate_create_sql(table_name, constraints, model)
        self.generate_drop_sql(table_name)
        self.generate_insert_sql(table_name, col_names)
        self.generate_select_all_sql(table_name, constraints, col_names)
        self.generate_select_pk_sql(table_name, constraints, col_names)
        self.generate_update_sql(table_name, constraints, col_names)
        self.generate_delete_sql(table_name, constraints)

    # Backup, Archive and Restore
    # ===========================================

    def backup_db(self):
        """Copy main DB file to backup location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        self.execute_insert(
            'INSERT_BACKUP',
            (SI.get_key(), bkup_dttm, 'backup', self.DB, self.DB_BKUP))
        shutil.copyfile(self.DB, self.DB_BKUP)

    def archive_db(self):
        """Copy main DB file to archive location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        file_nm = 'SASKAN_' + bkup_dttm + '.arcv'
        bkup_nm = path.join(self.DB_PATH, file_nm)
        self.execute_insert(
            'INSERT_BACKUP',
            (SI.get_key(), bkup_dttm, 'archive', self.DB, file_nm))
        shutil.copyfile(self.DB, bkup_nm)

    def restore_db(self):
        """Copy backup DB file to main location."""
        bkup_dttm = pendulum.now().format('YYYYMMDD_HHmmss')
        self.execute_insert(
            'INSERT_BACKUP',
            (SI.get_key(), bkup_dttm, 'restore', self.DB_BKUP, self.DB))
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
        sql_nm = str(p_sql_nm.split('.')[0]).upper() + '.sql'
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
            for ln in p_sql_select.split('\n'):
                if ln.upper().startswith('FROM'):
                    tbl_nm = ln.split(' ')[1]
                    break
        else:
            tbl_nm = p_tbl_nm
        self.cur.execute(f"PRAGMA table_info({tbl_nm})")
        cols = self.cur.fetchall()
        col_nms = [c[1] for c in cols]
        return col_nms

    def set_dict_from_cursor(self,
                             p_cols: list) -> OrderedDict:
        """
        Translate current cursor contents into a dict of lists
        :args:
        - p_cols (list) List of column names
        :return:
        - (OrderedDict )dict of lists, with column names as keys
          and in same order as listed in table-column order.
        """
        result = OrderedDict().fromkeys(p_cols)
        FETCH = self.cur.fetchall()    # list of tuples
        for row in FETCH:
            for i, col in enumerate(p_cols):
                if result[col] is None:
                    result[col] = list()
                result[col].append(row[i])
        return result

    # Executing SQL Scripts
    # ===========================================
    def execute_dml(self,
                    p_sql_nm: str):
        """Run a static SQL DROP OR CREATE file, that is,
        a SQL file which does not use dynamic parameters.
        :args:
        - p_sql_nm (str): Name of external SQL file
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        if SQL.count(';') > 1:
            self.cur.executescript(SQL)
        else:
            self.cur.execute(SQL)
        if self.db_conn is not None:
            self.db_conn.commit()
        self.disconnect_db()

    def execute_select_all(self,
                           p_sql_nm: str) -> OrderedDict:
        """Run a SQL SELECT ALL file which does not use
           any dynamic parameters.
        Iterate (fetchall) over the cursor to see record(s).
        :args:
        - p_sql_nm (str): Name of external SQL file
        :returns:
        - (OrderedDict) Dict of lists, {col_nms: [data values]}
        """
        self.connect_db()
        SQL: str = self.get_sql_file(p_sql_nm)
        COLS: list = self.get_db_columns(p_sql_select=SQL)
        self.cur.execute(SQL)
        result = self.set_dict_from_cursor(COLS)
        self.disconnect_db()
        return result

    def execute_select_by_pk(self,
                             p_sql_nm: str,
                             p_key_vals: list) -> OrderedDict:
        """Run a SQL SELECT by PK file which uses key values
        (primary key) for WHERE clause.
           For now I will assume that:
            - caller knows what values to provide and in what order
        Iterate (fetchall) over the cursor to see record(s).
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_key_vals (list): Value of primary key(s) to match on
        :returns:
        - (dict) Dict of lists, {col_nms: [data values]}

        @DEV:
        - Next, add:
            - SELECT method that uses a VIEW which includes
              all or some associated records from other tables.
        """
        if isinstance(p_key_vals, str):
            p_key_vals = [p_key_vals]
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        COLS = self.get_db_columns(p_sql_select=SQL)
        self.cur.execute(SQL, p_key_vals)
        result = self.set_dict_from_cursor(COLS)
        self.disconnect_db()
        return result

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

        @ DEV:
        - Can probably use a list instaed of a tuple, if that
          helps with anything down the road. OR maybe just to
          be consistent with other methods.
        """
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_values)
        self.db_conn.commit()   # type: ignore
        self.disconnect_db()

    def execute_update(self,
                       p_sql_nm: str,
                       p_values: list,
                       p_key_vals: list):
        """Run a SQL UPDATE file which uses dynamic values.
           Key value is matching condition for WHERE clause (prim key).
           Values are the column names in specified order.
           For now I will assume that:
            - UPDATEs will always expect full list of values
            - caller knows what values to provide and in what order
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_values (list): list of values to update
        - p_key_vals (list): Value of primary key)s_ to match on
        """
        if isinstance(p_key_vals, str):
            p_key_vals = [p_key_vals]
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_values + p_key_vals)
        if self.db_conn is not None:
            self.db_conn.commit()   # type: ignore
        self.disconnect_db()

    def execute_delete(self,
                       p_sql_nm: str,
                       p_key_vals: list):
        """Run a SQL DELETE file which uses key values (primary key)
           for WHERE clause (prim key).
           For now I will assume that:
            - caller knows what values to provide and in what order
        :args:
        - p_sql_nm (str): Name of external SQL file
        - p_key_vals (list): Value of primary key(s) to match on
        """
        if isinstance(p_key_vals, str):
            p_key_vals = [p_key_vals]
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
        self.cur.execute(SQL, p_key_vals)
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
