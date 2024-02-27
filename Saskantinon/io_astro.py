#!python
"""
:module:    io_astro.py

:author:    GM (genuinemerit @ pm.me)

:classes:
- UniverseModel   # Define a Game Universe and GalaxyCluster
- AstroIO

Related:
- io_file.py
- io_astro_test.py
- saskan_math.py
- saskan_report.py

Schema and Config files:
- configs/d_dirs.json        # directories
- configs/t_texts_en.json    # text strings in English
- schema/saskan_astro.json   # astronomical bodies

Database:
- [APP]/schema/SASKAN_DB
SQL:
- [APP]/schema/*.SQL


@TODO:
- Now that DB tables are defined and can be used,
  and data can be retrieved from DB (though we might
  need to parse it a bit more),
  and that io_data is defined as the place to hold
  all constant values and data structures for in-game
  use, and some basic test data values have been added
  to the astronomical stuctures up to the level of Star System,
  let's do some re-factoring of io_astro as follows:
- Move all constant values to io_data.py.
- Move all data structures to io_data.py.
- Handle all SQL activities in io_db.py.
- Handle basic set-up DML and DDL-creation in io_data
  and io_db.
- Modify this class to use io_db and io_data.
- Make the algorithms and methods in this class more
  flexible and re-usable.
  = For example: as before, but in a more clear-cut fashion,
  compute boundary values and so on rather than hard-coding them;
  keep track of and avoid collisions; use standards for naming and
  so on, using GitHub co-pilot to optimize the code.
  - For any given astronomical set of data that we want to
  display in-game, define MAP and GRID (and related) data
  that can be used to configure the 'map-winodow' used by
  the saskan_game.py module. Also define external methods for
  providing data to display in the 'consolde-window', associated
  with a given map-grid combination.
"""
import copy
import math
# import matplotlib.pyplot as plt
# import numpy as np
# import pendulum
# import pickle
import random
# import time

from collections import OrderedDict
# from matplotlib.animation import FuncAnimation
from pprint import pformat as pf  # noqa: F401
from pprint import pprint as pp  # noqa: F401
# from typing import Tuple, Union
from typing import Union

from io_db import DataBase
from io_file import FileIO
from io_shell import ShellIO
# from os import path
# from saskan_math import SaskanMath  # type: ignore

# Constant classes don't need to be instantiated
from io_data import Astro
from io_data import Universe
from io_data import ExternalUniv
from io_data import GalacticCluster
from io_data import Galaxy
from io_data import StarSystem
# from io_data import Geog
# from io_data import Geom
# from io_data import Struct         # type: ignore

DB = DataBase()
FI = FileIO()
SI = ShellIO()


# ==================== UniverseModel =================================
class AstroUniverse:
    """Class for creating a Universe, External Universe and
       Galactic Cluster object.

    - Timing Pulsar is a neutron star in the Cluster which
        regulates time measurements within the Cluster.
    - External Universe is everything outside the Cluster.
    - Universe encompasses both Galactic Cluster and External U.
    - When a Galactic Cluster is added to a Universe, the size
      of the External U diminishes, but size of U stays the same.
    - All data is saved to the database and returned as dictionary
      structures.
    """

    def __init__(self):
        """
        Initialize AstroUniverse object.
        """
        pass

    def get_all_universes(self):
        """
        Load all existing U, XU, GC, GX, SS data from database.
        """
        self.ALL_U = DB.execute_select_all('SELECT_ALL_UNIVERSE')
        self.ALL_XU = DB.execute_select_all('SELECT_ALL_EXTERNAL_UNIVERSE')
        self.ALL_GC = DB.execute_select_all('SELECT_ALL_GALACTIC_CLUSTER')
        self.ALL_GX = DB.execute_select_all('SELECT_ALL_GALAXY')
        self.ALL_SS = DB.execute_select_all('SELECT_ALL_STAR_SYSTEM')

    def get_external_universe(self,
                              p_univ_nm: str) -> dict:
        """
        Return object for a given Eternal Universe.
        :args:
        - p_univ_nm: Name of Universe
        """
        XU = {}
        if self.ALL_XU['univ_nm_fk'] is not None:
            if p_univ_nm in self.ALL_XU['univ_nm_fk']:
                xux = self.ALL_XU['univ_nm_fk'].index(p_univ_nm)
                XU = {k: self.ALL_XU[k][xux] for k in self.ALL_XU.keys()}
        return XU

    def get_galactic_clusters(self,
                              p_univ_nm: str) -> dict:
        """
        Return objects for Galactic Clusters in specified Universe.
        :args:
        - p_univ_nm: Name of Universe
        """
        GC = {}
        if self.ALL_GC['univ_nm_fk'] is not None\
                and p_univ_nm in self.ALL_GC['univ_nm_fk']:
            gcux = [i for i, val in enumerate(self.ALL_GC['univ_nm_fk'])
                    if val == p_univ_nm]
            for i in gcux:
                GC[self.ALL_GC['galactic_cluster_nm_pk'][i]] =\
                    {k: self.ALL_GC[k][i] for k in self.ALL_GC.keys()}
        return GC

    def get_galaxies(self,
                     p_galactic_cluster_nm: str) -> dict:
        """
        Return objects for Galaxies in specified Galactic Cluster.
        """
        GX = {}
        if self.ALL_GX['galactic_cluster_nm_fk'] is not None\
                and p_galactic_cluster_nm in\
                self.ALL_GX['galactic_cluster_nm_fk']:
            gxux = [i for i, val
                    in enumerate(self.ALL_GX['galactic_cluster_nm_fk'])
                    if val == p_galactic_cluster_nm]
            for i in gxux:
                GX[self.ALL_GX['galaxy_nm_pk'][i]] =\
                    {k: self.ALL_GX[k][i] for k in self.ALL_GX.keys()}
            return GX
        else:
            print("No Galaxies found in " +
                  f"Galactic Cluster {p_galactic_cluster_nm}")
        return GX

    def get_star_systems(self,
                         p_galaxy_nm: str,
                         p_pulsars_only: bool = False,
                         p_black_holes_only: bool = False) -> dict:
        """
        Return objects for Star Systems in specified Galaxy.
        """
        SS = {}
        if self.ALL_SS['galaxy_nm_fk'] is not None\
                and p_galaxy_nm in self.ALL_SS['galaxy_nm_fk']:
            ssux = [i for i, val
                    in enumerate(self.ALL_SS['galaxy_nm_fk'])
                    if val == p_galaxy_nm]
            for i in ssux:
                if p_pulsars_only and self.ALL_SS['is_pulsar'][i] == '0':
                    continue
                if p_black_holes_only and\
                        self.ALL_SS['is_black_hole'][i] == '0':
                    continue
                SS[self.ALL_SS['star_system_nm_pk'][i]] =\
                    {k: self.ALL_SS[k][i] for k in self.ALL_SS.keys()}
        else:
            print("No Star Systems found in " +
                  f"Galactic Cluster {p_galaxy_nm}")
        return SS

    def get_universe(self,
                     p_univ_nm_pk: Union[str, None] = None) -> dict:
        """
        Return objects for a given universe, including XU, GCs, GXs, SSs.
        :args:
        - p_univ_nm_pk: Name of Universe to lookup. If not specified,
          then just return objects with a data structure defined, but
          empty of values.
        """
        data = {}
        data['update'] = False
        data['U'] = Universe.to_dict(Universe)['UNIVERSE']
        data['XU'] =\
            ExternalUniv.to_dict(ExternalUniv)['EXTERNAL_UNIVERSE']
        data['GC'] =\
            GalacticCluster.to_dict(GalacticCluster)['GALACTIC_CLUSTER']
        data['GX'] = Galaxy.to_dict(Galaxy)['GALAXY']
        data['SS'] = StarSystem.to_dict(StarSystem)['STAR_SYSTEM']

        # These are values returned from the database.
        # I need to modify io_db so that "grouped" values
        #  returned by a SELECT have been converted back to objects.

        if p_univ_nm_pk not in ('', None)\
                and p_univ_nm_pk in self.ALL_U['univ_nm_pk']:
            data['update'] = True
            ux = self.ALL_U['univ_nm_pk'].index(p_univ_nm_pk)
            data['U'] = OrderedDict((k, self.ALL_U[k][ux])
                                    for k in self.ALL_U.keys())
            data['XU'] = self.get_external_universe(p_univ_nm_pk)
            data['GC'] = self.get_galactic_clusters(p_univ_nm_pk)
            data['GX'] = {}
            for cluster_nm in data['GC'].keys():
                galaxies = self.get_galaxies(cluster_nm)
                for g_nm in galaxies.keys():
                    data['GX'][g_nm] = galaxies[g_nm]
            SS = {}
            for g_nm in data['GX'].keys():
                star_systems = self.get_star_systems(g_nm)
                for ss_nm in star_systems.keys():
                    SS[ss_nm] = star_systems[ss_nm]
        return data

    def set_univ_name(self,
                      p_db_univ_nm: Union[str, None],
                      p_univ_nm: Union[str, None]) -> str:
        """
        :returns: (str) Name of new or existing universe
        """
        def set_random_name():
            uname = ' '.join(random.choice(nms) for nms in Astro.UNAME)
            return uname

        univ_nm = ''
        if p_univ_nm in ('', None):
            if self.ALL_U['univ_nm_pk'] is None:
                univ_nm = set_random_name()
            else:
                univ_nm = set_random_name()
                while univ_nm in self.ALL_U['univ_nm_pk']:
                    univ_nm = set_random_name()
        elif p_univ_nm == p_db_univ_nm:
            univ_nm = p_db_univ_nm
        else:
            univ_nm = p_univ_nm
        return univ_nm

    def set_univ_radius(self,
                        p_db_radius_gly: float,
                        p_radius_gly: Union[float, str, None]) -> float:
        """
        Set radius of universe.
        :args:
        - p_db_radius_gly: (float) radius of universe in gly per DB record
        - p_radius_gly: (float, str, None) radius of universe in gly per user
        Allow for user input of 'small','medium','large', or float.
        Use min and max values as set in io_data::Astro
        :returns: (float) radius in gly
        """
        def random_radius():
            return round(random.uniform(
                Astro.U_MIN_RAD_GLY, Astro.U_MAX_RAD_GLY), 3)

        radius_gly = 0.0
        if p_radius_gly in (0.0, '', None):
            p_radius_gly = p_db_radius_gly
        if p_radius_gly in ('small', 'medium', 'large'):
            radius_gly =\
                Astro.U_MIN_RAD_GLY if p_radius_gly == 'small'\
                else Astro.U_MAX_RAD_GLY if p_radius_gly == 'large'\
                else random_radius()
        elif isinstance(p_radius_gly, str) or p_radius_gly == 0.0:
            radius_gly = random_radius()
        else:
            radius_gly = Astro.U_MIN_RAD_GLY\
                if p_radius_gly < Astro.U_MIN_RAD_GLY else Astro.U_MAX_RAD_GLY\
                if p_radius_gly > Astro.U_MAX_RAD_GLY else p_radius_gly
        return radius_gly

    def set_univ_age(self,
                     p_db_age_gyr: float,
                     p_age_gyr: Union[float, str, None]) -> float:
        """
        Set age of the universe in terms of elapsed time since Big
        Bang in Gavoran years.
        Allow for 'young', 'old', 'average' strings, or float.
        Use min and max ages as set in io_data::Astro
        :args:
        - (float) Age of universe in Gavoran years as set on DB record.
        - (float|str|None) Age of universe in Gavoran years as set by user.
        """
        def random_age():
            return random.uniform(Astro.U_MIN_AGE_GYR, Astro.U_MAX_AGE_GYR)

        age_gyr = 0.0
        if p_age_gyr in (0.0, '', None):
            p_age_gyr = p_db_age_gyr
        if p_age_gyr in ('young', 'average', 'old'):
            age_gyr =\
                Astro.U_MIN_AGE_GYR if p_age_gyr == 'young'\
                else Astro.U_MAX_AGE_GYR if p_age_gyr == 'old'\
                else random_age()
        elif isinstance(p_age_gyr, str) or p_age_gyr == 0.0:
            age_gyr = random_age()
        else:
            age_gyr = Astro.U_MIN_AGE_GYR\
                if p_age_gyr < Astro.U_MIN_AGE_GYR else Astro.U_MAX_AGE_GYR\
                if p_age_gyr > Astro.U_MAX_AGE_GYR else p_age_gyr
        return age_gyr

    def set_universe(self,
                     p_univ_nm: Union[str, None] = None,
                     p_radius_gly: Union[float, str, None] = None,
                     p_age_gyr: Union[float, str, None] = None) -> str:
        """
        Add a new Universe to the database, or update if already exists.
        :args:
        - (str) Optional. Universe name or '' or None.
        - (float|str|None) Optional. Universe radius in gly.
        :writes (DB): UNIVERSE
        :returns: (str) Name of updated or inserted universe.
        """
        u_data = self.get_universe(p_univ_nm)
        U = copy.deepcopy(u_data['U'])
        U['univ_nm_pk'] = self.set_univ_name(U['univ_nm_pk'], p_univ_nm)
        U['radius_gly'] = self.set_univ_radius(U['radius_gly'], p_radius_gly)
        U['volume_gly3'] = (4/3) * math.pi * (U['radius_gly'] ** 3)
        U['volume_pc3'] = U['volume_gly3'] * Astro.GLY_TO_PC
        U['age_gyr'] = self.set_univ_age(U['age_gyr'], p_age_gyr)
        U['expansion_rate_kmpsec_per_mpc'] = Astro.U_EXP_RATE
        U['total_mass_kg'] = U['volume_gly3'] * Astro.U_VOL_TO_MASS
        U['dark_energy_kg'] = U['total_mass_kg'] * Astro.U_DARK_ENERGY_PCT
        U['dark_matter_kg'] = U['total_mass_kg'] * Astro.U_DARK_MATTER_PCT
        U['baryonic_matter_kg'] = U['total_mass_kg'] * Astro.U_BARYONIC_PCT
        if u_data['update']:
            if U != u_data['U']:
                key = list()
                key.append(U.pop("univ_nm_pk"))
                vals = list(U.values())
                DB.execute_update('UPDATE_UNIVERSE', vals, key)
        else:
            vals = tuple(U.values())
            DB.execute_insert('INSERT_UNIVERSE', vals)
        ix = False
        if self.ALL_U['univ_nm_pk'] is not None:
            if U['univ_nm_pk'] in self.ALL_U['univ_nm_pk']:
                ix = self.ALL_U['univ_nm_pk'].index(U['univ_nm_pk'])
        for k, v in U.items():
            if ix:
                self.ALL_U[k][ix] = v
            else:
                self.ALL_U[k] = [v]
        return U['univ_nm_pk']

    def set_external_univ_name(self,
                               p_univ_nm: str,
                               p_db_external_univ_nm: Union[str, None],
                               p_external_univ_nm: Union[str, None]) -> str:
        """
        If xu name provided, but it does not match existing xu name,
          ignore the provided name and return the existing name.
        If no xu name os provided, and there is an existing XU, use
          the exixting name.
        If xu name provided, and there is no existing XU, use provided name.
        if no xu name provied and there is no existing XU, then geneate
          XU name from the Universe Name.
        :args:
        - (str) Name of universe (required)
        - (str|None) Name of existing external universe or None
        - (str|None) Name of new external universe or None.
        :returns: (str) Name of new or existing external universe
        """
        external_univ_nm = ''
        if p_external_univ_nm not in ('', None) and\
                p_db_external_univ_nm not in ('', None):
            external_univ_nm = p_db_external_univ_nm
        elif p_external_univ_nm in ('', None) and\
                p_db_external_univ_nm not in ('', None):
            external_univ_nm = p_db_external_univ_nm
        elif p_external_univ_nm not in ('', None) and\
                p_db_external_univ_nm in ('', None):
            external_univ_nm = p_external_univ_nm
        else:
            external_univ_nm = "External " + p_univ_nm
        return external_univ_nm

    def set_external_universe(self,
                              p_univ_nm: str,
                              p_external_univ_nm: Union[str, None]):
        """
        Based on settings of Universe, either create or update its
        associated External Universe object.

        @TODO:
        - Pick up here. Populate or recalculate External Universe values.
        - Insert or Update database.
        - Refresh self.XU values.
        - Then see notes on refacoring io_db handling of "groups"/objects.
        """
        u_data = self.get_universe(p_univ_nm)
        XU = copy.deepcopy(u_data['XU'])

        pp(("XU 1: ", XU))

        XU['univ_nm_fk'] = u_data['U']['univ_nm_pk']
        db_external_univ_nm = None
        if 'external_univ_nm_pk' in XU.keys():
            db_external_univ_nm = XU['external_univ_nm_pk']
        XU['external_univ_nm_pk'] =\
            self.set_external_univ_name(db_external_univ_nm,
                                        XU['univ_nm_fk'],
                                        p_external_univ_nm)
        pp(("XU 2: ", XU))

    def set_astro(self,
                  p_univ_nm: Union[str, None] = None,
                  p_radius_gly: Union[float, str, None] = None,
                  p_age_gyr: Union[float, str, None] = None,
                  p_external_univ_nm: Union[str, None] = None):
        """
        Set all objects in the universe. Pretty much everything is
        inter-connected. Let's see if we can have a single interface
        for any type of update or insert to a universe, at least
        down to a certain level -- e.g., worlds and moons.

        @TODO:
        - Do EXTERNAL_UNIVERSE, whic has no grouped objects. Then...
        - Abstract the io_db method that translates embedded objects
          to DB columns. For example, io_data.Struct.CoordXYZ objects
          become 3 columns on the database. It is the logic in
          io_db.set_sql_column_group()
        - Refactor io_db to take advantage of to_dict methods
          included with the table structures to transform the grouped
          DB columns back into the corresponding object. Do this in
          both the SELECT methods as well as INSERT, UPDATE. In other
          words, don't require the calling modules to expect anything
          other than the structures -- including objects -- as
          defined in io_data.
        - But don't store the objects as JSON or BLOB or Pickles.
          I still want to be able to query and update elements within
          those objects in a normal SQL way.
        """
        self.get_all_universes()
        univ_nm = self.set_universe(p_univ_nm, p_radius_gly, p_age_gyr)

        print("\n\n1------")
        pp((self.ALL_U))
        pp((self.ALL_XU))

        self.set_external_universe(univ_nm, p_external_univ_nm)

        print("\n\n2------")
        pp((self.ALL_U))
        pp((self.ALL_XU))
