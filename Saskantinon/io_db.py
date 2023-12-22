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
import pickle
import pendulum
import shutil
import sqlite3 as sq3

from os import path, remove
from pprint import pprint as pp    # noqa: F401
from io_file import FileIO

from copy import copy
from pathlib import Path

from io_file import FileIO

FI = FileIO()


class DataBase(object):
    """Support Sqlite3 database setup, usage, maintenance."""

    def __init__(self):
        """Initialize Dbase object.
        """
        self.DB_PATH = path.join(FI.D['APP']['root'],
                            FI.D['APP']['dirs']['db'],
                            FI.D['DB']['main'])
        self.DB = path.join(self.DB_PATH, FI.D['DB']['main'])
        self.DB_BKUP = path.join(self.DB_PATH, FI.D['DB']['bkup'])
        self.db_conn = None

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
        file_nm = 'HOFIN_' + bkup_dttm + '.arcv'
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
        """Drop DB connection to SASKAN_DB."""
        if hasattr(self, "db_conn") and self.db_conn is not None:
            try:
                self.cur.close()
                self.db_conn.close()
            except RuntimeWarning:
                pass
        self.db_conn = None

    def connect_db(self,
                   p_db_nm: str = 'main'):
        """Open DB connection to SASKAN_DB.
        :args:
        - p_db_nm (str) Optional. Default is 'main'.
          If set to 'bkup' then use the backup DB.
          If neither, then connect to main DB.
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

    def get_sql_file(self,
                     p_sql_nm: str) -> str:
        """Read SQL from named file.
        :args:
        - p_sql_nm (str) Name of  SQL file in [APP]/sql
        :returns:
        - (str) Content of the SQL file
        """
        sql_nm = p_sql_nm.upper() + '.SQL'\
            if '.SQL' not in p_sql_nm\
            else p_sql_nm
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
        self.connect_db()
        SQL = self.get_sql_file(p_sql_nm)
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
