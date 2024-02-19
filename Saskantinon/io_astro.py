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

# import math
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
# from io_data import Geog
# from io_data import Geom
# from io_data import Struct         # type: ignore

DB = DataBase()
FI = FileIO()
SI = ShellIO()


# ==================== UniverseModel =================================
class Universe:
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
            print("Error: No External Universe " +
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
            print("Error: No Galactic Clusters found in " +
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
            print("Error: No Galaxies found in " +
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
            print("Error: No Star Systems found in " +
                  f"Galactic Cluster {p_galaxy_nm}")
        return SS

    def get_universe(self,
                     p_univ_nm_pk: str = '') -> dict:
        """
        Return objects for a given universe, including XU, GCs, GXs, SSs.
        """
        U = {}
        XU = {}
        GC = {}
        GX = {}
        SS = {}
        # Get universe and related data
        if p_univ_nm_pk != '' and p_univ_nm_pk in self.ALL_U['univ_nm_pk']:
            ux = self.ALL_U['univ_nm_pk'].index(p_univ_nm_pk)
            U = {k: self.ALL_U[k][ux] for k in self.ALL_U.keys()}
            XU = self.get_external_universe(p_univ_nm_pk)
            GC = self.get_galactic_clusters(p_univ_nm_pk)
            GX = {}
            for cluster_nm in GC.keys():
                galaxies = self.get_galaxies(cluster_nm)
                for g_nm in galaxies.keys():
                    GX[g_nm] = galaxies[g_nm]
            SS = {}
            for g_nm in GX.keys():
                star_systems = self.get_star_systems(g_nm)
                for ss_nm in star_systems.keys():
                    SS[ss_nm] = star_systems[ss_nm]
        if U == {}:
            print(f"No Universe named {p_univ_nm_pk}")
        return {"U": U, "XU": XU, "GC": GC, "GX": GX, "SS": SS}

    def set_universe(self,
                     p_univ_nm: str,
                     p_radius_gly: Union[float, str, None]) -> dict:
        """
        Add a new Universe to the database, or update it already exists.
        :args:
        - (str) Optional. Universe name or '' or None.
        - (float) Optional. Universe radius in gly.
        :writes (DB): UNIVERSE, and optionally EXTERNAL_UNIVERSE
        :returns: (bool) is_new_universe flag
        """
        data = self.get_universe(p_univ_nm)
        univ = data['U']
        # set name
        if univ != {}:
            if p_univ_nm in univ['univ_nm_pk']:
                print(f"Universe {p_univ_nm} already exists. Updating,..")
        else:
            if p_univ_nm in ('', None):
                univ['univ_nm_fk'] =\
                    ' '.join(random.choice(nms) for nms in Astro.UNAME)
                print(f"Creating new Universe named:  {p_univ_nm},..")
        # set radius
        if p_radius_gly != 0.0:
            univ['radius_gly'] = Astro.MIN_RAD_GLY\
                if univ['radius_gly'] < p_radius_gly else Astro.MAX_RAD_GLY\
                if univ['radius_gly'] > p_radius_gly else p_radius_gly
        else:
            univ['radius_gly'] =\
                random.uniform(Astro.MIN_RAD_GLY, Astro.MAX_RAD_GLY)
        return univ
