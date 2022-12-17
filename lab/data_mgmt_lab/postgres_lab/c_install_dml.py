#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
:module:    c_install_dml
:class:     InstallDML
:test:      TestInstallDML
:author:  genuinemerit <dave@davidstitt.solutions>
"""
from pathlib import Path

# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=E0401
# from pprint import pprint as pp
import param

from c_func_basic import FuncBasic
from c_bow_const import BowConst
from c_func_pg import FuncPG
Ġ = BowConst()
ß = FuncBasic()
Ƥ = FuncPG()

class InstallDML(param.Parameterized):
    """
    Generate code to create and drop Postgresql functions for all schemas, tables.

    * Use psycopg2 to generate DML-level stored functions for bowdb tables.
    * Generate PSQL functions for delete, insert, update, maintain of tables.

    :protip:
        * This is driven by reading a list of all tables that exist in a database.
        * In order to intialize the database catalog, first call (FuncPG).map_db().

    :Inherit:  FuncPG_ --> FuncConfig_ --> FuncBasic_ --> BowConst_
    """

    schema_name = param.String(default='', doc='Name of schema being modified')
    table_name = param.String(default='', doc='Name of table being modified')
    sql_create = param.String(default='', doc='SQL code for CREATE DDL')
    sql_drop = param.String(default='', doc='SQL code for DROP DDL')
    record_struct = [] # {array} Defines the row structure of a table

    # ===================================================
    def __gen_delete_func(self):
        """
    **__gen_delete_func/0**
    * Generate postgresql function for doing a DELETE by id against the table.
    * Set class attributes for schema, table before calling this function.
    :Sets:
        - self.sql_create {string} CREATE function code
        - self.sql_drop {string} DROP function code
        """
        schema_table = self.schema_name + "." + self.table_name
        self.sql_create += """\n
/* DELETE {0} BY ID {1}
CREATE OR REPLACE FUNCTION bow_func.delete_{2}(
    IN p_id  INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_id_in       INTEGER=NULL;
    v_id_out      INTEGER=NULL;
BEGIN
    v_id_in := p_id;
    DELETE FROM {0} bow WHERE bow.id = v_id_in;
    SELECT bow.id INTO v_id_out FROM {0} bow WHERE bow.id = v_id_in;
    IF v_id_out IS NULL THEN
        RETURN v_id_out;        /* Delete succeeded. */
    ELSE
        RETURN NULL;            /* Delete failed. */
    END IF;
END;
$$ LANGUAGE plpgsql;
""".format(schema_table, Ġ.UNBAR_DML, self.table_name)

        self.sql_drop += """
DROP FUNCTION IF EXISTS bow_func.delete_{0}(INTEGER) CASCADE;""".format(self.table_name)

    # ===================================================
    def __gen_insert_func(self):
        """
    **__gen_insert_func/0**
    * Generate postgresql function for doing an INSERT against the table.
    * Set class attributes for schema, table and record_struct before calling this function.
    :Sets:
        - self.sql_create {string} CREATE function code
        - self.sql_drop {string} DROP function code
        """
        schema_table = "{0}.{1}".format(self.schema_name, self.table_name)
        self.sql_create += """\n
/* INSERT INTO {0} {1}
CREATE OR REPLACE FUNCTION bow_func.insert_{2} (
    IN p_rec   {0})
RETURNS INTEGER AS $$
DECLARE
    v_rec_in      {0};
    v_id_out      INTEGER=NULL;
BEGIN
    v_rec_in := p_rec;
    INSERT INTO {0} (
""".format(schema_table, Ġ.UNBAR_DML, self.table_name)
        for col in self.record_struct:
            if col.col_nm != 'id':
                self.sql_create += "{0}, ".format(col.col_nm)
        self.sql_create = self.sql_create[:-2]
        self.sql_create += ")\n    VALUES (\n"
        for col in self.record_struct:
            if col.col_nm != 'id':
                self.sql_create += "            v_rec_in.{0},\n".format(col.col_nm)
        self.sql_create = self.sql_create[:-2] + ");"
        self.sql_create += """
    RETURN v_id_out;
END;
$$ LANGUAGE plpgsql;
"""
        self.sql_drop += """
DROP FUNCTION IF EXISTS bow_func.insert_{0}({1}) CASCADE;""".format(self.table_name, schema_table)

    # ===================================================
    def __gen_update_func(self):
        """
    **__gen_update_func/0**
    * Generate postgresql function for doing an UPDATE against the table.
    * Set class attributes for schema, table and record_struct before calling this function.
    :Sets:
        - self.sql_create {string} CREATE function code
        - self.sql_drop {string} DROP function code
        """
        schema_table = "{0}.{1}".format(self.schema_name, self.table_name)
        self.sql_create += """\n
/* UPDATE {0} {1}
CREATE OR REPLACE FUNCTION bow_func.update_{2} (
    IN p_rec   {0})
RETURNS INTEGER AS $$
DECLARE
    v_rec_in      {0};
    v_id_out      INTEGER=NULL;
BEGIN
    v_rec_in := p_rec;
    UPDATE {0} bow SET
""".format(schema_table, Ġ.UNBAR_DML, self.table_name)
        for col in self.record_struct:
            if col.col_nm != 'id':
                self.sql_create += "        {0} = v_rec_in.{0},\n".format(col.col_nm)
        self.sql_create = self.sql_create[:-2]
        self.sql_create += """
    WHERE bow.id = v_rec_in.id;
    RETURN v_rec_in.id;
END;
$$ LANGUAGE plpgsql;

""".format(self.table_name)

        self.sql_drop += """
DROP FUNCTION IF EXISTS bow_func.update_{0}({1}) CASCADE;

""".format(self.table_name, schema_table)


    # ===================================================
    def __write_schema_funcs(self):
        """
    **__write_schema_funcs/0**
    * Write PSQL files for schema functions, first archiving older versions if they exist.
        """
        dttm = ß.get_dttm()
        create_fnm = "/home/bow/db/dml/create_func_{0}.psql".format(self.schema_name)
        drop_fnm = "/home/bow/db/dml/drop_func_{0}.psql".format(self.schema_name)
        for (filnm, fildat) in [(create_fnm, self.sql_create), (drop_fnm, self.sql_drop)]:
            if Path(filnm).exists() and Path(filnm).is_file():
                ß.run_cmd("mv {0} {1}.bak.{2}".format(filnm, filnm[:-5], dttm.curr_ts))
                if ß.cmd_rc:
                    msg = "Not archived: {0} \n{1}".format(filnm, str(ß.cmd_result))
                    raise ValueError(ß.log_me(msg, Ġ.ERROR))
            dml_file = open(filnm, 'a')
            dml_file.write(fildat)
            dml_file.close()


    # ===================================================
    def gen_schema_funcs(self, schema_nm):
        """
    **gen_schema_funcs/1**
    * Generate postgresql functions for all tables in the schema by calling other methods.
    :Args:
        - schema_nm {string} a valid bow* schema name.
    :Sets:
        - self.sql_create {string} CREATE code
        - self.sql_drop {string} DROP code
        """
        Ƥ.map_db()
        self.schema_name = ''
        self.table_name = ''
        if schema_nm not in Ƥ.db_cat.keys():
            raise ValueError(ß.log_me("Schema {0} not found in DB catalog".format(schema_nm),
                                      Ġ.ERROR))
        self.schema_name = schema_nm
        self.sql_create = """-- dml/create_func_{0}.psql
/* CREATE Functions for tables in schema: {0}
{1}
SET SESSION ROLE bow_sup;
""".format(self.schema_name, Ġ.UNBAR_DML)
        self.sql_drop = """-- dml/drop_func_{0}.psql
/* DROP Functions for tables in schema: {0}
{1}
SET SESSION ROLE bow_sup;
""".format(self.schema_name, Ġ.UNBAR_DML)
        for table_nm in Ƥ.db_cat[schema_nm]:
            self.table_name = table_nm
            self.record_struct = Ƥ.db_cat[self.schema_name][self.table_name]
            self.sql_create += """
/* CREATE functions for table: {0}
{1}
""".format(self.table_name, Ġ.UNBAR_DML)
            self.sql_drop += """
/* DROP functions for table: {0}
{1}
""".format(self.table_name, Ġ.UNBAR_DML)
            self.__gen_delete_func()
            self.__gen_insert_func()
            self.__gen_update_func()
        self.__write_schema_funcs()
