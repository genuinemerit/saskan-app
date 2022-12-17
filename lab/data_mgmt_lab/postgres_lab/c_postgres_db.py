#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    c_postgres_db
:class:     PostgresDB
:test:      TestPostgresDB
:author:  genuinemerit <dave@davidstitt.solutions>
:dev: Possibly enhance to work with memcached or other caching mechanism.
"""
# pylint: disable=C0103
# pylint: disable=E0401
from collections import OrderedDict
from pprint import pprint as pp

import json
import param

from c_func_basic import FuncBasic
from c_bow_const import BowConst
from c_func_pg import FuncPG
Ġ = BowConst()
ß = FuncBasic()
Ƥ = FuncPG()


class PostgresDB(param.Parameterized):
    """
    * Use Postgresql functions.
    * Use psycopg2 to wrap Python calls to bowdb stored functions and SELECTs.
    * Provides generic methods suitable for use with any table or view.

    :Inherits:  FuncPG_ --> BowFuncConfig_ --> BowFuncBasic_ --> BowConst_

    :protip:
        * Logic is driven by reading a list of all tables that exist in a database.
        * In order to initialize the database catalog, first call (FuncPG).map_db().
"""
    schema_name = param.String(default='', doc='Name of schema being modified')
    table_name = param.String(default='', doc='Name of table being modified')
    record_struct = []  # {array} Defines the row structure of a table
    record_data = OrderedDict()  # Collect data from a row structure

    def get_meta(self, p_table_nm, p_json=False):
        """
    **get_meta/1**
    * For selected table, return its meta_rec.
    :dev: Consider formatting for more effective use with APIs and GUIs
    :Args:
        - p_table_nm {string} Valid table name from one of the bow* schema.
        - p_json {boolean} Optional. If true, then return json-formatted structure instead of tuple
    :Return:
        - {namedtuple} of type self.meta_rec = (schema name, table name, record_struct) OR
        - {string} in JSON format containing the same info as self.meta_rec
        """
        def __get_meta_json():
            """ Convert metadata to JSON formatted string
            :Returns {string} JSON-formatted result:
            """
            rec_array = []
            col_ord = 1
            for rec_tup in self.record_struct:
                rec_array.append({"col_ord": col_ord,
                                  "col_nm": rec_tup.col_nm,
                                  "data_ty": rec_tup.data_ty,
                                  "nullable": rec_tup.nullable,
                                  "max_len": rec_tup.max_len})
                col_ord += 1
            meta_rec = OrderedDict()
            meta_rec["schema_name"] = self.schema_name
            meta_rec["table_name"] = self.table_name
            meta_rec["record_struct"] = rec_array
            return (meta_rec, json.dumps(meta_rec))

        ## get_meta ##
        # ===========
        self.init_record(p_table_nm)
        meta_rec, json_rec = __get_meta_json()
        if p_json:
            return json_rec
        return meta_rec

    def select_first_record(self, p_table_nm):
        """
    **select_first_record/1**
    * Collect first item returned in fetchall from a SELECT *.
    :dev:
        * Use this is for testing purposes only.
        * Should not be calling this on a normal basis.
        * Using SELECT * is almost always a bad idea. Should list items to be returned.
    :Args:
        - p_table_nm {string} Name of table to select on
        """
        self.init_record(p_table_nm)
        psql = "SELECT * FROM {0}.{1};".format(
            self.schema_name, self.table_name)
        Ƥ.call_postgres(psql)
        # Should probably check here if there is any result before calling load_record
        self.load_record(self.table_name, Ƥ.result[0])

    def init_record(self, p_table_nm, p_refresh=False):
        """
    **init_record/2**
    * Get record_struct from DB catalog.
    * Init record values to null for selected table if this is a refresh of the record structure.
    * Otherwise just set the record_data to empty OrderedDict.
    * Data record content gets refreshed if it is the first time it's being used, or if directed.
    :dev:
        - The record_struct may be used to do edits.
        - This could call for some more work at this level, e.g. buffering before/after.
    :Args:
        - p_table_nm {string} A valid table name from one of the bow* schema.
        - p_refresh {Boolean} Defaults to False.
    :Sets:
        - self.record_struct {list of namedtuple} Each item in list describes a column
        - self.record_data {OrderedDict} If a refresh, each value initialized to None
        """
        Ƥ.map_db()
        v_table_nm = p_table_nm.lower().strip()
        if self.table_name != v_table_nm or p_refresh:
            self.schema_name = ''
            self.table_name = ''
            self.record_struct = []
            for schema_nm in Ƥ.db_cat:
                if p_table_nm in Ƥ.db_cat[schema_nm]:
                    self.schema_name = schema_nm
                    self.table_name = v_table_nm
                    self.record_struct = Ƥ.db_cat[schema_nm][v_table_nm]
                    for col in self.record_struct:
                        self.record_data[col.col_nm] = None
                    break
            if self.record_struct == []:
                raise ValueError(ß.log_me("Table name {0} not in DB catalog".format(v_table_nm),
                                          Ġ.ERROR))

    def load_record(self, p_table_nm, p_cursor_rec):
        """
    **load_record/2**
    * Convert one unnamed tuple (cursor row) of record values.
    * Convert format returned from a postgres cursor to PostgresDB OrderedDict record format.
    :Args:
        - p_table_nm {string} Valid table name from one of the bow* schema
        - p_cursor_rec {tuple} Unnamed tuple that was produced by calling a postgresql cursor
    :Sets:
        - self.record_data {OrderedDict} Record content in a named, ordered format
        """
        self.init_record(p_table_nm)
        # Converts unnamed tuple to OrderedDict, guaranteeing we won't lose column order.
        idx_rec = [idx for idx in enumerate(p_cursor_rec)]
        idx = 0
        # pp(("load_record..record_data:", self.record_data))
        for col_nm in self.record_data:
            # Column-data returned from cursor should be in same order as retrieved from catalog.
            self.record_data[col_nm] = idx_rec[idx][1]
            idx += 1

    def select_bow(self, p_table_nm, p_select, p_match='AND'):
        """
    **select_bow/3**
    * SELECT a record by one or more field matches, using AND logic.
    * Match field names against the record layout defined in self.record_data.
    :Args:
        - p_table_nm {string} Name of table to select on
        - p_select {dict} - Required. Collection of field name:search value pairs
        - p_match {string} - 'OR' and 'AND' are only acceptable values; default to 'AND'
        """
        def __select_cols():
            """ Build list of column names to be returned
            :Return: {string} Column list for selected table formatted for use in SQL
            """
            meta_rec = self.get_meta(self.table_name)
            col_names = ''
            for cols in meta_rec.columns:
                col_names += " {0},".format(cols.col_nm)
            col_names = col_names[:-1]
            return col_names

        def __select_where(p_select, v_match):
            """ Build the WHERE clause based on provided parameters
            :Args:
                - {dict} of selected name:value pairs
                - {string} AND or OR
            :Return: {string} WHERE clause logic for SQL
            """
            v_wsql = ''
            for v_key, v_val in p_select.items():
                if v_key in self.record_data.keys():
                    if v_wsql != '':
                        v_wsql += ' {0}'.format(v_match)
                    v_wsql += " bow.{0} = '{1}'".format(v_key, v_val)
                else:
                    raise ValueError(ß.log_me('{0} not a valid field name'.format(v_key),
                                              Ġ.ERROR))
            if v_wsql == '':
                msg = 'Unable to formulate WHERE for <{0}>'.format(
                    str(p_select))
                raise ValueError(ß.log_me(msg, Ġ.ERROR))
            return v_wsql

        def __select_order(p_select):
            """ Build the ORDER BY clause based on WHERE columns
            :Args: {dict} of selected name:value pairs
            :Return: {string} ORDER BY clause logic for SQL
            """
            v_osql = ''
            for v_key, _ in p_select.items():
                v_osql += " bow.{0},".format(v_key)
            v_osql = v_osql[:-1]
            return v_osql

        ## select_bow ##
        # =============
        if len(p_select) < 1:
            raise ValueError(ß.log_me('p_select is empty', Ġ.ERROR))
        # init_record calls map_db if needed
        self.init_record(p_table_nm)
        v_match = p_match.upper().strip()
        if v_match != 'OR':
            v_match = 'AND'
        v_psql = "SELECT {0} FROM {1}.{2} bow ".format(__select_cols(),
                                                       self.schema_name,
                                                       self.table_name)
        v_psql += "WHERE {0} ORDER BY {1};".format(__select_where(p_select, v_match),
                                                   __select_order(p_select))
        Ƥ.call_postgres(v_psql)
        if Ƥ.result == []:
            self.init_record(self.table_name, p_refresh=True)
            ß.log_me('No rows selected for: {0}'.format(v_psql), Ġ.INFO)
        else:
            # Load first record returned in fetchall_cursor to record_data attribute.
            # :dev:
            # - Communicate when multiple rows were found.
            self.load_record(self.table_name, Ƥ.result[0])

    def maintain_rec(self, p_table_nm, p_rec, p_delete=None):
        """
    **maintain_rec/3**
    * Decide whether to do a delete, insert or update.
    * This is an "upsert" with a delete option.
    * Pass in record values (p_rec) as an OrderedDict matching the desired table structure.
    :Args:
        - p_table_nm {string} Valid name of a table in database catalog
        - p_rec {OrderedDict} Valid record structure (like self.record_data)
        - p_delete {boolean}  True if request is to delete a record, else None or false
    :Return: {integer} Key of the deleted, updated, or inserted record; or None
        """
        self.init_record(p_table_nm)
        self.record_data = p_rec
        # pp(("maintain..record_data:", self.record_data))
        Ƥ.py2pg_rec(self.record_data)  # sets self.flat_rec
        # print(("PostgresDB.maintain_rec.py2pg_rec:", self.flat_rec))
        v_id_out = None
        if Ƥ.flat_rec == '':
            ß.log_me('No record values provided to maintain', Ġ.WARN)
        else:
            v_id_in = self.record_data['id']
            if v_id_in is None:         # Do an INSERT

                pp(("PostgresDB.maintain_rec:", "Attempting insert"))

                v_sql = "SELECT bow_func.insert_{0}(p_rec:={1});".format(
                    self.table_name, Ƥ.flat_rec)

                print(("PostgresDB.maintain_rec.psql:", v_sql))
                Ƥ.call_postgres(v_sql, p_describe=True, p_notices=True)

                print(("PostgresDB.maintain_rec.notices:", Ƥ.notices))
                print(("PostgresDB.maintain_rec.desc:", Ƥ.desc))

                v_sql = "SELECT max(id) FROM {0}.{1};".format(
                    self.schema_name, self.table_name)
                Ƥ.call_postgres(v_sql)
                v_id_out = Ƥ.result[0][0]

                print(("PostgresDB.maintain_rec.v_id_out:", v_id_out))

            else:
                # Check that provided ID is a valid one
                self.select_bow(p_table_nm, {'id': v_id_in})
                v_id_in = Ƥ.result[0][0]
                # pp(("maintain...verify ID:", v_id_in))
                if v_id_in is None:
                    raise ValueError(ß.log_me("ID {0} not on table {1}".format(str(v_id_in),
                                                                               self.table_name),
                                              Ġ.ERROR))
                else:
                    if p_delete:            # Do a DLEETE
                        # pp(("maintain_rec:", "Attempting delete"))
                        v_sql = "SELECT bow_func.delete_{0}({1});".format(
                            self.table_name, v_id_in)
                        Ƥ.call_postgres(v_sql)
                        v_id_out = v_id_in
                    else:                   # Do an UPDATE
                        # pp(("maintain_rec:", "Attempting update"))
                        v_sql = "SELECT bow_func.update_{0}(p_rec:={1});".format(self.table_name,
                                                                                 Ƥ.flat_rec)
                        Ƥ.call_postgres(v_sql)
                        # pp(("maintain..result_after_update:", self.result))
                        v_id_out = v_id_in
        return v_id_out
