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

import math
# import matplotlib.pyplot as plt
# import numpy as np
# import pendulum
# import pickle
import random
# import time

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
        Load existing U, XU, GC, GX, SS data from database.
        """
        self.ALL_U = DB.execute_select_all('SELECT_ALL_UNIVERSE')
        print(f"Known universes are: {str(self.ALL_U['univ_nm_pk'])}")
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
        if p_univ_nm in self.ALL_XU['univ_nm_fk']:
            xux = self.ALL_XU['univ_nm_fk'].index(p_univ_nm)
            XU = {k: self.ALL_XU[k][xux] for k in self.ALL_XU.keys()}
        else:
            print("No External Universe " +
                  f"associated with {p_univ_nm}")
        return XU

    def get_galactic_clusters(self,
                              p_univ_nm: str) -> dict:
        """
        Return objects for Galactic Clusters in specified Universe.
        :args:
        - p_univ_nm: Name of Universe
        """
        GC = {}
        if p_univ_nm in self.ALL_GC['univ_nm_fk']:
            gcux = [i for i, val in enumerate(self.ALL_GC['univ_nm_fk'])
                    if val == p_univ_nm]
            for i in gcux:
                GC[self.ALL_GC['galactic_cluster_nm_pk'][i]] =\
                    {k: self.ALL_GC[k][i] for k in self.ALL_GC.keys()}
        else:
            print("No Galactic Clusters found in " +
                  f"Universe {p_univ_nm}")
        return GC

    def get_galaxies(self,
                     p_galactic_cluster_nm: str) -> dict:
        """
        Return objects for Galaxies in specified Galactic Cluster.
        """
        GX = {}
        if p_galactic_cluster_nm in self.ALL_GX['galactic_cluster_nm_fk']:
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
        if p_galaxy_nm in self.ALL_SS['galaxy_nm_fk']:
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
        data['U'] = Universe.to_dict(Universe)
        data['XU'] = ExternalUniv.to_dict(ExternalUniv)
        data['GC'] = GalacticCluster.to_dict(GalacticCluster)
        data['GX'] = Galaxy.to_dict(Galaxy)
        data['SS'] = StarSystem.to_dict(StarSystem)
        if p_univ_nm_pk not in ('', None)\
                and p_univ_nm_pk in self.ALL_U['univ_nm_pk']:
            ux = self.ALL_U['univ_nm_pk'].index(p_univ_nm_pk)
            data['U'] = {k: self.ALL_U[k][ux] for k in self.ALL_U.keys()}
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

    def set_univ_nm(self,
                    p_db_univ_nm: Union[str, None],
                    p_univ_nm: Union[str, None]) -> str:
        """
        :returns: (str) Name of new or existing universe
        """
        def set_random_name():
            return ' '.join(random.choice(nms) for nms in Astro.UNAME)

        univ_nm = 'unknown'
        if p_univ_nm in ('', None):
            if self.ALL_U['univ_nm_pk'] is None:
                univ_nm = set_random_name()
            else:
                while univ_nm not in self.ALL_U['univ_nm_pk']:
                    univ_nm = set_random_name()
            print(f"Creating new Universe  <<{univ_nm}>>")
        elif p_univ_nm == p_db_univ_nm:
            univ_nm = p_db_univ_nm
            print(f"Universe <<{univ_nm}>> already exists.")
        else:
            univ_nm = p_univ_nm
            print(f"Creating new Universe <<{univ_nm}>>")
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
        :writes (DB): UNIVERSE, and optionally EXTERNAL_UNIVERSE
        :returns: (str)  maybe some kind of status meesage indicating
          update, insert or no action taken

        @TODO:
        - Insert or Update DB. Finish the first prototype with
          UNIVERSE, since it does not contain embedded objects.
          Do EXTERNAL_UNIVERSE also. Then...
        - Abstract the io_db method that translate embedded objects
          to DB columns. For example, io_data.Struct.CoordXYZ objects
          become 3 columns on the database. Will need to do the same
          logic prior to inserting or updating for tables that use these
          types of structures. It is the logic in io_db.set_sql_column_group()
          so maybe that method can just be called from here. Or maybe
          it needs to be abstracted in way to make it available to both
          io_db and io_astro (and other callers).
        - May also be useful to refactor io_db a bit to take advantage
          of the to_dict methods included with the table structures.
        - May also want to develop a method to transform the grouped
          DB columns back into the corresponding object.
        - Another way to manage it would be to do transforms in both
          directions in io_db, as part of insert, update and select logic.
          - I kind of like that idea. Keeps the logic in one place.
          - Lets the user use the objects as they are designed to be used.
        """
        u_data = self.get_universe(p_univ_nm)
        U = u_data['U']['UNIVERSE']
        U['univ_nm_pk'] = self.set_univ_nm(U['univ_nm_pk'], p_univ_nm)
        U['radius_gly'] = self.set_univ_radius(U['radius_gly'], p_radius_gly)
        U['volume_gly3'] = (4/3) * math.pi * (U['radius_gly'] ** 3)
        U['volume_pc3'] = U['volume_gly3'] * Astro.GLY_TO_PC
        U['age_gyr'] = self.set_univ_age(U['age_gyr'], p_age_gyr)
        U['expansion_rate_kmpsec_per_mpc'] = Astro.U_EXP_RATE
        U['total_mass_kg'] = U['volume_gly3'] * Astro.U_VOL_TO_MASS
        U['dark_energy_kg'] = U['total_mass_kg'] * Astro.U_DARK_ENERGY_PCT
        U['dark_matter_kg'] = U['total_mass_kg'] * Astro.U_DARK_MATTER_PCT
        U['baryonic_matter_kg'] = U['total_mass_kg'] * Astro.U_BARYONIC_PCT
        u_data['U']['UNIVERSE'] = U

        pp(("U", U))
        pp(("u_data", u_data))

        return 'Completed'
