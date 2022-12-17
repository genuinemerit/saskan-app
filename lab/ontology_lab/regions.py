#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Classes and functions for defining a game region
"""
import random
import sys
# Local packages
sys.path.append('./')
import dbsqlite
import names
sys.path.append('../../web/app')
from main import utils

# FUNCTIONS

# CLASS
# =========================

class Region(object):
    '''
    Methods and data for creating region characteristics.
    '''
    # Class Constants
    _TBL_DDL = ['create_dnatype_tables.sql',
                'create_region_tables.sql',
                'create_langfam_tables.sql',
                'create_lang_tables.sql',
                'create_clanname_tables.sql']
    _VW_DDL = ['create_dnatype_views.sql',
               'create_region_views.sql',
               'create_langfam_views.sql',
               'create_lang_views.sql',
               'create_clanname_views.sql']
    _INS_DML = ['insert_dnatype.sql',
                'insert_region.sql',
                'insert_langfam.sql',
                'insert_lang.sql',
                'insert_clanname.sql']

    def __init__(self):
        '''
        Instantiate region object.
        '''
        # Class attributes
        self.lang_fams = {}
        self.regions = {}
        self.local_regions = []
        self.clans = {}
        self.bow_db = None
        self.stat_ok = None
        self.msg = ''

    def reset_region(self):
        '''
        (Re-)Initialize region object.
        '''
        # Class attributes
        self.lang_fams = {}
        self.regions = {}
        self.local_regions = []
        self.clans = {}
        self.bow_db = None

    def create_world_db(self, dbname='bowdev'):
        '''
        @param dbname is what name to give to the new database file.
        @return 2-tuple (status, msg) of either failed call or last success

        Destroy this database if it already exists.
        Connect to instance of sqlite database for storing world- or
        environment-level info for a game world.
        '''
        self.reset_region()
        self.bow_db = dbsqlite.BowDB()
        # Destroy the db if it already exists.
        (stat_ok, msg) = self.bow_db.destroy_db(dbname)
        # Create new database file.
        (stat_ok, msg) = self.bow_db.connect_db(dbname)
        return (stat_ok, msg)

    def create_tables_and_views(self):
        '''
        Execute SQL files to create standard set of tables and views for
        a BallOfWax world.
        @return 2-tuple (status, msg) of either failed call or last success
        '''
        # run DDL to create tables
        for this_sql in Region._TBL_DDL:
            (stat_ok, msg) = self.bow_db.exec_ddl_table(this_sql)
            if not stat_ok:
                return (stat_ok, msg)
        # run DDL to create views
        for this_sql in Region._VW_DDL:
            (stat_ok, msg) = self.bow_db.exec_ddl_view(this_sql)
            if not stat_ok:
                return (stat_ok, msg)
        return(stat_ok, msg)

    def insert_sqlfile_data(self):
        '''
        Execute SQL DML files to insert values into tables
        @return 2-tuple (status, msg) of either failed call or last success
        '''

        # run DML to insert data from file-based DML
        for this_sql in Region._INS_DML:
            (stat_ok, msg) = self.bow_db.exec_dml(this_sql)
            if not stat_ok:
                return (stat_ok, msg)
        return(stat_ok, msg)

    def get_regions(self, local_container=None):
        '''
        @param local_container is a list of region_container values
          that identify a localized game region
        Load region info form the database to the class
        @return (stat, msg, regions and local_regions class attributes)
            unless failure, then return (status, msg)
        '''
        # Read data from regions view
        (stat_ok, msg, data) = self.bow_db.exec_dal_query('list_region.sql')
        # Populate the regions attribute
        if stat_ok:
            for row in data:
                self.regions[row['COMMON_NM']] = \
                    {'desc':row['REGION_DESC'],
                     'lang1':row['FIRST_LANG'],
                     'lang2':row['SECOND_LANG'],
                     'name1':row['LOCAL_NM_1'],
                     'name2':row['LOCAL_NM_2'],
                     'con':row['CONTAINER'],
                     'geo':row['GEO_DESC']}
            # Identify the local regions
            self.local_regions = []
            for region in self.regions.keys():
                if local_container != None:
                    if self.regions[region]['con'] in local_container \
                    and not region in local_container:
                        self.local_regions.append(region)
                else:
                    self.local_regions.append(region)
        else:
            return (stat_ok, msg)
        return (stat_ok, msg, self.regions, self.local_regions)

    def get_languages(self):
        '''
        Load language info from the database to the class
        @return (stat, msg, lang_fams class attribute) unless failure,
            then return (status, msg)
        '''
        # Read data from language families view
        (stat_ok, msg, data) = self.bow_db.exec_dal_query('list_langfam.sql')
        # Populate the lang_fams attribute
        if stat_ok:
            for row in data:
                self.lang_fams[row['LANG_FAMILY_NM']] = \
                    {'dna':row['LANG_FAMILY_DNA_TYP'],
                     'region':row['LANG_FAMILY_REGION'],
                     'desc':row['LANG_FAMILY_DESC'],
                     'langs':{}}
        else:
            return (stat_ok, msg)

        # Read data from languages table
        (stat_ok, msg, data) = self.bow_db.exec_dal_query('list_lang.sql')
        # Populate the lang_fams attribute
        if stat_ok:
            for row in data:
                lang = row['LANG_NM']
                # self.lang_fams[row['LANG_FAMILY_NM']]['languages'] = \
                self.lang_fams[row['LANG_FAMILY_NM']]['langs'][lang] =\
                    {'dna':row['LANG_DNA_TYP'],
                     'region':row['LANG_REGION'],
                     'desc':row['LANG_DESC']}
        else:
            return (stat_ok, msg)

        return (stat_ok, msg, self.lang_fams)

    def get_clans(self, clan_cnt=10):
        '''
        @param clan_cnt is the number of tribes to create above and beyond
          the defaults defined in the database
        @return clans class attribute unless failure, then return (stat, msg)

        Generate names of major clans by readign data in from the db and
           using the names functions.
        '''
        # Read data from clan names table
        (stat_ok, msg, data) = \
            self.bow_db.exec_dal_query('list_clanname.sql')
        if stat_ok:
            # Load defaults into class attribute
            for row in data:
                surname = row['SURNAME']
                self.clans[surname] = \
                    {'dna': row['DNA_TYP'],
                     'region':row['REGION_NM'],
                     'language':row['LANG_NM']}
            # Generate clan surnames using names function
            surnames = names.create_surnames(clan_cnt)
            for surname in surnames:
                self.clans[surname] = \
                    {'dna': '', 'region':'', 'language':''}
                # Choose item from local_regions
                rand_int = random.randint(0, len(self.local_regions)-1)
                this_region = self.local_regions[rand_int]
                self.clans[surname]['region'] = this_region
                # Choose language based on regions
                rand_int = utils.random_100()
                if rand_int < 50:
                    this_lang = self.regions[this_region]['lang1']
                else:
                    this_lang = self.regions[this_region]['lang1']
                self.clans[surname]['language'] = this_lang
                # Choose DNA based on language
                for lang_fam in self.lang_fams.keys():
                    if this_lang in self.lang_fams[lang_fam]['langs'].keys():
                        this_dna = \
                            self.lang_fams[lang_fam]['langs'][this_lang]['dna']
                self.clans[surname]['dna'] = this_dna
        else:
            return (stat_ok, msg)

        # Next ...Save clan info to db

        return self.clans

    def get_tribes(self, min_cnt=3, max_cnt=12):
        '''
        @param min_cnt is min number of tribes to create per clan
        @param max_cnt is max number of tribes to create per clan

        Generate names and characteristics of tribes within each clan,
        using the names functions.
        '''
        for clan in self.clans.keys():
            self.clans[clan]['tribes'] = \
                names.create_surnames(random.randint(min_cnt, max_cnt))

        # Next .. assign characteristics to tribes and save to db

        return self.clans

def test_me():
    '''
    Simple unit tests for this Class.
    '''
    # Personality
    w_obj = Region()
    w_obj.create_world_db('bowdev00')
    w_obj.create_tables_and_views()
    w_obj.insert_sqlfile_data()
    w_obj.get_regions([u'Uterung', u'Skantaring'])
    print w_obj.local_regions
    w_obj.get_languages()
    w_obj.get_clans(4)
    print w_obj.get_tribes(1, 5)

if __name__ == '__main__':
    test_me()
