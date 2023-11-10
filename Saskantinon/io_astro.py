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
"""

import math
import matplotlib.pyplot as plt
import numpy as np
# import pendulum
import pickle
import random
import time

# from os import path
from matplotlib.animation import FuncAnimation
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_db import DataBase              # type: ignore
from io_file import FileIO              # type: ignore
from io_shell import ShellIO            # type: ignore
from saskan_math import SaskanMath      # type: ignore

DB = DataBase()
FI = FileIO()
SI = ShellIO()
SM = SaskanMath()


# ==================== UniverseModel =================================

class UniverseModel:
    """Class for modeling a universe.

    - TU = Total Universe
    - GC = Galactic Cluster. Only one is needed to manage a game.
        But we can have 1 to many GC within a TU.
        See the GalaxyModel() for creating galaxies within a GC.
    - TP = Timing Pulsar (neutron star) in the GC which
        regulates time measurements within the GC.
    - XU = External Universe is everything outside of the GC.
    """

    def __init__(self,
                 p_boot_db: bool = False,
                 p_TU_nm: str = None,
                 p_GC_nm: str = None,
                 p_TP_nm: str = None):
        """Load or create TU, GC and TP. Create or modify XU.
            All data is saved to SASKAN_DB. There are distinct tables for the
            total universe (TU) and galactic cluster (GC) objects.
            The GC  includes info about the TP (Timing Pulsar).
            The XU (External Universe) is also stored on a separate table and
            it must be updated whenever a GC is added to a TU.
        :args:
        - p_boot_db (bool) Optional. If True, destroy DB, make new one.
        - p_TU_nm (str) Optional. Name of Total Universe.
            If p_TU_nm already in use, load univ from DB but
            proceed with Cluster, Pulsar creation and XU computation.
        - p_GC_nm (str) Optional. Name of Galactic Cluster.
            If p_GC_nm already in use, then stop if universe already
            exists. If new universe, tweak name of cluster to be unique,
        - p_TP_nm (str) Optional. Name of Timing Pulsar.
        """
        self.TU = None
        self.GC = None
        self.TP = None
        self.XU = None
        if p_boot_db:
            self.reboot_database()
        is_new_TU = self.set_universe_name(p_TU_nm)
        if is_new_TU:
            self.generate_universe()
        is_new_GC = self.generate_cluster_name(is_new_TU, p_GC_nm)
        if is_new_GC:
            self.generate_cluster(p_TP_nm)
        print(f"is_new_TU: {is_new_TU}")
        pp(('self.TU: ', self.TU))
        print(f"is_new_GC: {is_new_GC}")
        pp(('self.GC: ', self.GC))
        # self.XU = self.compute_external_universe(is_new_TU, is_new_GC)

    def reboot_database(self):
        """Delete all data. Create a fresh SASKAN_DB database.
        """
        DB.execute_dml('DROP_GALAXIES')
        DB.execute_dml('DROP_CLUSTERS')
        DB.execute_dml('DROP_XUS')
        DB.execute_dml('DROP_UNIVS')
        DB.execute_dml('CREATE_UNIVS')
        DB.execute_dml('CREATE_GALAXIES')
        DB.execute_dml('CREATE_CLUSTERS')
        DB.execute_dml('CREATE_XUS')

    @classmethod
    def get_new_TU_nm(cls):
        a1 = random.choice(["Cosmic", "Mysterious", "Eternal",
                            "Radiant", "Infinite", "Celestial"])
        a2 = random.choice(["Endless", "Magical", "Spectacular",
                            "Mystical", "Enchanting"])
        n = random.choice(["Universe", "Cosmos", "Realm", "Dimension",
                           "Oblivion", "Infinity"])
        tu_nm = f"{a1} {a2} {n}"
        return tu_nm

    @classmethod
    def get_new_GC_nm(cls):
        a1 = random.choice(["Runic", "Starry", "Brilliant",
                            "Blessed", "Eternal", "Celestial"])
        a2 = random.choice(["Oceanic", "Wonderful", "Waving",
                            "Milky", "Turning"])
        n = random.choice(["Way", "Home", "Heavens", "Lights",
                           "Path", "Cluster"])
        gc_nm = f"{a1} {a2} {n}"
        return gc_nm

    @classmethod
    def get_new_TP_nm(cls):
        a1 = random.choice(["Timer", "Chrono", "Clockwork",
                            "Lighthouse", "Beacon", "Pendumlum"])
        a2 = random.choice(["Pulsar", "Star", "Nova",
                            "Sentry", "Stupa"])
        n = str(round(random.uniform(100, 10000)))
        tp_nm = f"{a1} {a2} {n}"
        return tp_nm

    def set_universe_name(self,
                          p_TU_nm: str = None) -> bool:
        """If p_TU_nm already in use, then load data from DB;
        Otherwise use name provided or generate one at random.
        :args: (str) Optional. Universe name or none.
        :sets (dict): Initializes self.TU
        :returns: (bool) new universe flag
        """
        is_new_TU = True
        db_tu = DB.execute_select('SELECT_ALL_UNIVS')
        if p_TU_nm is not None:
            tu_nm = p_TU_nm
            for x, u_nm in enumerate(db_tu['univ_name']):
                if tu_nm == u_nm:
                    self.TU = pickle.loads(db_tu['univ_object'][x])
                    is_new_TU = False
                    break
        else:
            tu_nm = self.get_new_TU_nm()
            while tu_nm in db_tu['univ_name']:
                tu_nm = self.get_new_TU_nm()
        if is_new_TU:
            self.TU = {SM.ASTRO.TU: (tu_nm, SM.GEOM.NM)}
        return is_new_TU

    def generate_universe(self):
        """Define data for a new Total Universe.
        :sets: (dict): self.TU
        """
        radius_gly = random.uniform(45.824, 47.557)
        self.TU[SM.GEOM.RD] = (radius_gly, SM.ASTRO.GLY)      # Radius GPC
        volume_gly3 = (4/3) * math.pi * (radius_gly ** 3)
        self.TU[SM.GEOM.VL] = (volume_gly3, SM.ASTRO.GLY3)    # Volume GLY3
        self.TU[SM.ASTRO.ET] = (13.787e9, SM.ASTRO.GY)        # Age
        self.TU[SM.ASTRO.UER] = (73.3, SM.ASTRO.KSM)          # Expansion rate
        variance_pct = (volume_gly3 - SM.ASTRO.TUV) / SM.ASTRO.TUV
        mass_kg = (SM.ASTRO.TUK * variance_pct) + SM.ASTRO.TUK
        self.TU[SM.GEOM.MS] = (mass_kg, SM.GEOM.KG)           # Total matter kg
        # Apply dark energy, dark matter and baryonic matter percentages
        self.TU[SM.ASTRO.DE] = (mass_kg * SM.ASTRO.DEP, SM.GEOM.KG)  # kg
        self.TU[SM.ASTRO.DM] = (mass_kg * SM.ASTRO.DMP, SM.GEOM.KG)  # kg
        self.TU[SM.ASTRO.BM] = (mass_kg * SM.ASTRO.BMP, SM.GEOM.KG)  # kg
        DB.execute_insert('INSERT_UNIV_PROC',
                          (self.TU[SM.ASTRO.TU][0], pickle.dumps(self.TU)))

    def generate_cluster_name(self,
                              p_is_new_TU: bool,
                              p_GC_nm: str = None) -> bool:
        """Generate a name for the Galactic Cluster.
        :args:
        - (bool) p_is_new_TU  determines if new univ was generated
        - (str) Optional. Galactic Cluster name or none.
            If a name was provided, determine if it is already in use.
            If it is already in use and this is NOT a new universe, we're done,
               just pull in the data from DB.
            Otherwise generate a new GC.
            If name already in use and this IS a new universe, then modify the
               name so that it will be a unique within this universe.
        :sets:
        - (dict) self.GC
        :returns:
        - (bool) is-new-galactic-cluster flag
        """
        is_new_GC = True
        db_gc = DB.execute_select('SELECT_ALL_CLUSTERS')
        if p_GC_nm is not None:
            gc_nm = p_GC_nm
        else:
            gc_nm = self.get_new_GC_nm()
        self.GC = {SM.ASTRO.GC: (gc_nm, SM.GEOM.NM)}
        if gc_nm in db_gc['cluster_name']:
            if p_is_new_TU:
                # Cluster name already exists in another universe.
                while gc_nm in db_gc['cluster_name']:
                    gc_nm += " " + str(round(random.uniform(1, 100)))
                    self.GC[SM.ASTRO.GC] = (gc_nm, SM.GEOM.NM)
            else:
                # Cluster name already exists in this universe.
                for x, db_gc_nm in enumerate(db_gc['cluster_name']):
                    if db_gc_nm == gc_nm:
                        self.GC = pickle.loads(db_gc['cluster_object'][x])
                        is_new_GC = False
                        break
        return is_new_GC

    def detect_cluster_collision(self,
                                 p_loc: tuple,
                                 p_dim: tuple) -> tuple:
        """Determine if newly defined cluster loc collides with an existing
        cluster loc in same universe. Just draw a bounding rectangle and
        compare edges.
        :args:
        - p_loc (tuple): (x, y, z) of new cluster center location  (gly)
        - p_dim (tuple): (x, y, z) for new cluster ellipsoid shape (parsec)
        :returns:
        - (bool, list) (True if collision detected, else False, and
                        bounding rectangle of new cluster =
                        [(l, r), (t, b), (f, b)])
        """
        tu_nm = self.TU[SM.ASTRO.TU][0]
        gc_in_tu = dict()
        db_gc = DB.execute_select('SELECT_ALL_CLUSTERS')
        for x, db_tu_nm in enumerate(db_gc['univ_name_fk']):
            if db_tu_nm == tu_nm:
                gc_in_tu[db_gc['cluster_name'][x]] =\
                    pickle.loads(db_gc['cluster_object'][x])
        w = (p_dim[0] * SM.ASTRO.PC_TO_GLY) / 2  # width in gigalightyears
        bnd = list()
        bnd.append((p_loc[0] - w, p_loc[0] + w))    # Left, Right
        bnd.append((p_loc[1] - w, p_loc[1] + w))    # Top, Bottom
        bnd.append((p_loc[2] - w, p_loc[2] + w))    # Front, Back

        # Once we're saving multiple cluster, re-open this for debugging
        # Try using seeding the randomizer with a fixed value
        #  to force creation of collisions. If that doesn't work,
        #  override randomization with fixed values.
        # Looking reasonable so far. Since the locs are expressed
        #  in relatively reasonable units, like 1 or 2 digits to left of
        #  decimal point, might be able to do a visual check just using
        #  the locations. The bounding rects are expressed in the same
        #  terms, but the lengths of the edges can be very small... still
        #  they are usually in the first two signigicant digits. So maybe
        #  if everything is multiplied by 100 and rounded to nearest int,
        #  we could get a useful visual check.
        pp(("New cluster center location GLY: ", p_loc))
        pp(("New cluster bounding rect: ", bnd))

        collision = False
        for gc_nm, c in gc_in_tu.items():
            c_loc = c[f"{SM.ASTRO.GC} {SM.GEOG.LOC} {SM.GEOM.VE}"][0]
            c_bnd = c[f"{SM.GEOM.EL} {SM.GEOM.BND}"][0]

            print(f"Comparing to cluster {gc_nm}...")
            pp(("Old cluster center location GLY: ", c_loc))
            pp(("Old cluster bounding rect: ", c_bnd))

            if not (bnd[0][1] < c_bnd[0][0] or
                    bnd[0][0] > c_bnd[0][1] or
                    bnd[1][1] < c_bnd[1][0] or
                    bnd[1][0] > c_bnd[1][1] or
                    bnd[2][1] < c_bnd[2][0] or
                    bnd[2][0] > c_bnd[2][1]):
                collision = True
                break
        return (collision, bnd)

    def set_cluster_loc_and_size(self) -> tuple:
        """Set cluster location, dimensions.
        Verify no collision.
        - If randomized cluster location and size collides with an existing
        cluster in same universe, re-compute until no collision detected.
        - Collsion detection also sets the GC bounding rectangle.
        Then randomly set direction and angle of rotations.
        - Direction will be either + or - for each dimensional axis.
        - Limit the rotation angles to 0 to 90 degrees.
        - See notes in universe.html regarding pitch, yaw and roll
            terminology and standards for defining rotation.
        Finally, set the semi-axes of the ellipsoid.

        :returns:
        - ((float * 3): (x, y, z in gigalightyears from universe
                         center to center of cluster),
        - (float * 3): (x, y, z are width, depth, height in parsecs),
        - (float * 3): (a, b, c semi-axes which define ellipsoid shape),
        - (dict * 3):  (rotation direction and angle for each axis),
        - (list * 3):  (bounding rectangle of cluster in gigalihtyears))
        """
        def compute_cluster_loc_and_dim():
            loc = list()
            for d in range(0, 3):
                loc.append(random.uniform(-univ_r_gly, univ_r_gly))
            dim = list()
            dim.append(random.uniform(1e6, 1e7))    # x = 1 to 10 M parsecs
            dim.append(dim[0] * random.uniform(0.5, 0.8))  # y = 50% to 80% x
            dim.append(dim[1] * random.uniform(0.1, 0.2))  # z = 10% to 20% y
            return (loc, dim)

        univ_r_gly = self.TU[SM.GEOM.RD][0] * 0.99
        collision = True
        while collision:
            loc, dim = compute_cluster_loc_and_dim()
            collision, bnd = self.detect_cluster_collision(loc, dim)
        # Select rotation direction and angle for each axis.
        rot = list()
        for d in range(0, 3):
            dir = random.choice(['+', '-'])
            ang = round((random.uniform(0, 90)), 2)
            rot.append((dir, ang))
        # Axes of ellipsoid derived from dim, so unit is parsecs.
        axes = list()
        for d in dim:
            axes.append(d / 2)
        return (loc, dim, axes, rot, bnd)

    def set_cluster_vol_and_mass(self,
                                 p_axes: tuple) -> tuple:
        """Compute total volume of galactic cluster in cubic parsecs.
        Compute mass in kilograms for cluster's total allocation of:
            dark energy, dark matter, baryonic matter
        - Compute total GC matter as a percent from 1% to 5% of TU matter.
        - Get a sense of the density of the cluster (vol/mass ratio)
        - Apply constant percents for the 3 types of matter.
        :args:
        - p_a (float): relative x axis of ellipsoid
        - p_b (float): relative y axis of ellipsoid
        - p_c (float): relative z axis of ellipsoid
        - p_TU (dict): data about total universe
        :returns:
        - (float * 5): (GC total volume in cubic parsecs,
                        GC total mass in kilograms,
                        GC dark energy, dark matter, baryonic matter in kg)
        """
        gc_vol = (4/3) * math.pi * p_axes[0] * p_axes[1] * p_axes[2]  # PC3
        gc_mass_kg = self.TU[SM.GEOM.MS][0] * random.uniform(0.01, 0.05)
        gc_de_kg = self.TU[SM.ASTRO.DE][0] * SM.ASTRO.DEP   # kg
        gc_dm_kg = self.TU[SM.ASTRO.DM][0] * SM.ASTRO.DMP   # kg
        gc_bm_kg = self.TU[SM.ASTRO.BM][0] * SM.ASTRO.BMP   # kg
        return (gc_vol, gc_mass_kg, gc_de_kg, gc_dm_kg, gc_bm_kg)

    def generate_timing_pulsar(self,
                               p_TP_nm: str = None):
        """Define the timing pulsar within the GC.
        - Pulses (rotational frequency) per 'galactic second' in milliseconds.
        - Set pulsar location within inner third of the cluster space.
          Location is expressed in gigalight years, with reference to the
          center of the cluster.
        :args:
        - p_TP_nm (str) Optional. Name of neutron star / timing pulsar
        :sets:
        - (dict) Updated version of self.GC
        """
        tp_nm = p_TP_nm if p_TP_nm is not None else self.get_new_TP_nm()
        tp_loc = list()
        gc_loc = self.GC[f"{SM.ASTRO.GC} {SM.GEOG.LOC} {SM.GEOM.VE}"][0]
        gc_dim = self.GC[f"{SM.GEOM.EL} {SM.GEOM.DIM}"][0]
        for d in range(0, 3):
            delta = (gc_dim[d] / 2) * random.uniform(-0.33, 0.33)
            tp_loc.append((gc_loc[d] + delta))

        self.GC[SM.ASTRO.TP] = (tp_nm, SM.GEOM.NM)                  # Name
        self.GC[f"{SM.ASTRO.TP} {SM.ASTRO.PR}"] =\
            ((1 / random.uniform(700, 732)) * 1000, SM.ASTRO.PMS)   # Period
        self.GC[f"{SM.ASTRO.TP} {SM.GEOG.LOC}"] =\
            (tp_loc, f"{SM.GEOM.XYZ} {SM.ASTRO.GLY}")               # Location

    def generate_cluster(self,
                         p_TP_nm: str = None):
        """Generate data for galatic cluster and for timing pulsar.
        :args:
        - p_TP_nm (str): Optional
        :sets:
        - (dict): self.GC
        """
        gc_loc, gc_dim, gc_axes, gc_rot, gc_bnd =\
            self.set_cluster_loc_and_size()
        gc_vol, gc_mass, gc_de, gc_dm, gc_bm =\
            self.set_cluster_vol_and_mass(gc_axes)

        self.GC[SM.ASTRO.TU] =\
            (self.TU[SM.ASTRO.TU][0], SM.GEOM.CON)       # Container
        self.GC[f"{SM.ASTRO.GC} {SM.GEOG.LOC} {SM.GEOM.VE}"] =\
            (gc_loc, f"{SM.GEOM.DIM} {SM.ASTRO.GLY}")    # Location
        self.GC[f"{SM.GEOM.EL} {SM.GEOM.DIM}"] =\
            (gc_dim, f"{SM.GEOM.XYZ} {SM.ASTRO.PC}")     # Shape dimensions
        self.GC[f"{SM.GEOM.EL} {SM.GEOM.SAX}"] =\
            (gc_axes, f"{SM.GEOM.ABC} {SM.ASTRO.PC}")    # Shape semi-axes
        # Shape rotation
        self.GC[f"{SM.GEOM.EL} {SM.GEOM.ROT}"] =\
            (gc_rot, f"({SM.GEOM.DIR}, {SM.GEOM.ANG}), {SM.GEOM.PYR}")
        self.GC[f"{SM.GEOM.EL} {SM.GEOM.BND}"] =\
            (gc_bnd, f"{SM.GEOM.XYZD} {SM.ASTRO.GLY}")   # Shape bound rect
        self.GC[f"{SM.ASTRO.GC} {SM.GEOM.VL}"] =\
            (gc_vol, SM.ASTRO.PC3)                       # Volume
        self.GC[SM.GEOM.MS] = (gc_mass, SM.GEOM.KG)      # Total Mass kg
        self.GC[SM.ASTRO.DE] = (gc_de, SM.GEOM.KG)       # Dark Energy kg
        self.GC[SM.ASTRO.DM] = (gc_dm, SM.GEOM.KG)       # Dark Matter kg
        self.GC[SM.ASTRO.BM] = (gc_bm, SM.GEOM.KG)       # Baryonic Matter kg

        self.generate_timing_pulsar(p_TP_nm)
        DB.execute_insert('INSERT_CLUSTER_PROC',
                          (self.GC[SM.ASTRO.GC][0],
                           self.TU[SM.ASTRO.TU][0],
                           pickle.dumps(self.GC)))

    def set_xu_name(self,
                    is_new_TU: bool,
                    p_TU_nm: str) -> str:
        """Assign name for a new External Universe object.
        It is the PK on a table, so it has to be unique in INSERT.
        It has a 1:1 relationship with a TU, which it derives from.
        :args:
        - is_new_TU (bool): Flag indicating if it is a new universe
        - p_TU_nm (str): Name of the current Total Universe
        :returns:
        - (str): Either new XU name or name of XU related to p_TU
        """
        def compute_new_xu_nm():
            xu_nm = p_TU_nm.split(" ")[:2]
            xu_nm = " ".join(xu_nm) + " XU"
            xu_nm += "_" + str(round(random.uniform(10, 1000)))
            return xu_nm

        db_xu = DB.execute_select('SELECT_ALL_XUS')
        if is_new_TU:
            xu_nm = compute_new_xu_nm()
            while xu_nm in db_xu['xu_name']:
                xu_nm = compute_new_xu_nm
        else:
            for rx, u_nm in enumerate(db_xu['univ_name_fk']):
                if u_nm == p_TU_nm:
                    xu_nm = db_xu['xu_name'][rx]
                    break
        return xu_nm

    def compute_external_universe(self,
                                  is_new_TU: bool,
                                  is_new_GC: bool,
                                  p_TU: dict) -> dict:
        """Define the External Universe (XU) within the TU.
        XU contains all the mass that is not in the GC.
        XU has to be recomputed whenever a new galactic cluster is added.
        Add new XU record if it is a new universe, otherwise, update
          existing XU record associated with the current TU.
        :args:
        - is_new_TU (bool):    Flag indicating if it is a new universe
        - is_new_GC (bool): Flag indicating if it is a new cluster
        - TU (dict) Data about the Total Universe.
        :returns:
        - XU (dict) Data about the External Universe (new or modified)
        """
        XU = dict()
        de = 0.0
        dm = 0.0
        bm = 0.0
        xu_nm = self.set_xu_name(is_new_TU, p_TU[SM.M.TU][0])
        tu_nm = p_TU[SM.M.TU][0]
        XU[SM.M.XU] = (xu_nm, SM.M.NM)
        XU[SM.M.CON]: (tu_nm, SM.M.TU)
        db_gc = DB.execute_select('SELECT_ALL_CLUSTERS')
        for gx, u_nm in enumerate(db_gc['univ_name_fk']):
            if u_nm == tu_nm:
                GC = pickle.loads(db_gc['cluster_object'][gx])
                de += GC[SM.M.DE][0]
                dm += GC[SM.M.DM][0]
                bm += GC[SM.M.BM][0]
        XU[SM.M.DE] = (((p_TU[SM.M.DE][0] * p_TU[SM.M.MS][0]) - de), SM.M.KG),
        XU[SM.M.DM] = (((p_TU[SM.M.DM][0] * p_TU[SM.M.MS][0]) - dm), SM.M.KG),
        XU[SM.M.BM] = (((p_TU[SM.M.BM][0] * p_TU[SM.M.MS][0]) - bm), SM.M.KG)
        if is_new_TU:
            print(f"New XU created: {xu_nm}")
            DB.execute_insert(
                'INSERT_XU_PROC', (xu_nm, tu_nm, pickle.dumps(XU)))
        elif is_new_GC:
            print(f"Updated existing XU: {xu_nm}")
            DB.execute_insert(
                'UPDATE_XU_PROC', (pickle.dumps(XU), xu_nm))
        else:
            print(f"No changes made to XU: {xu_nm}")
        return XU

# ==================== GalaxyModel =================================

class GalaxyModel:
    """Class for modeling the Game Galaxy (GG).
    """

    def __init__(self,
                 p_TU_nm: str,
                 p_GC_nm: str,
                 p_galaxy_name: str = None,
                 p_galaxy_sz: str = "M"):
        """Initialize class for a Game Galaxy.
        If univ name or cluster name are not found on DB, stop.
        :args:
        - p_TU_nm (str): Name of universe to put GC in
        - p_GC_nm (str): Name of cluster to put GC in
        - p_galaxy_name (str) Optional.  If provided, load existing galaxy.
            Otherwise, generate new gamaing galaxy.
        - p_galazy_size (str) Default = 'M'. Must be S, M or L.
        """
        TU_found, self.GC =\
            self.get_univ_and_galaxy(p_TU_nm, p_GC_nm)
        if TU_found and self.GC is not None:
            new_galaxy, self.GG =\
                self.get_galaxy_name(p_GC_nm, p_galaxy_name)
        if new_galaxy:
            self.GG = self.generate_new_galaxy(p_GC_nm, p_galaxy_sz)
        pp((self.GG))

    def get_univ_and_galaxy(self,
                            p_TU_nm: str,
                            p_GC_nm: str) -> tuple:
        """Retrieve galaxy, cluster and external universe objects from DB.
        :args:
        - p_TU_nm (str): Name of universe to put GC in
        - p_GC_nm (str): Name of cluster to put GC in
        :returns:
        - (bool, dict): (flag indicating TU found or not, GC data)
        """
        tu_found = False
        GC = None
        db = DB.execute_select('SELECT_ALL_UNIVS')
        for x, nm in enumerate(db['univ_name']):
            if nm == p_TU_nm:
                tu_found = True
                break
        db = DB.execute_select('SELECT_ALL_CLUSTERS')
        for x, nm in enumerate(db['cluster_name']):
            if nm == p_GC_nm:
                GC = pickle.loads(db['cluster_object'][x])
                break
        return(tu_found, GC)

    def get_galaxy_name(self,
                        p_GC_nm: str,
                        p_galaxy_name: str = None) -> tuple:
        """Either retrieve existing Game Galaxy object for specified name
        and cluster, or assign a name to a new Galaxy object.
        :args:
        - p_cluster_nm (str) Name of the containing Galactic Cluster.
        - p_galaxy_nm (str) Optional. Name of the Game Galaxy.
        :returns:
        - (bool, dict): (Flag indicating new galaxy or not,
                         Data about the Game Galaxy)
        """
        GG = dict()
        new_galaxy = True
        if p_galaxy_name is not None:
            db = DB.execute_select('SELECT_ALL_GALAXIES')
            for x, nm in enumerate(db['galaxy_name']):
                if nm == p_galaxy_name\
                and db['cluster_name'][x] == p_GC_nm:
                    new_galaxy = False
                    GG = db['galaxy_object'][x]
                    break
            if new_galaxy:
                GG[SM.M.GG] = (p_galaxy_name, SM.M.NM)
        else:
            a1 = random.choice(["Brilliant", "Lustrous", "Twinkling",
                   "Silvery", "Argent", "Glistening"])
            a2 = random.choice(["Way", "Trail", "Cloud",
                   "Wave", "Skyway"])
            n =  random.choice(["Galaxy", "Cosmos", "Nebula",
                   "Megacosm", "Space"])
            GG[SM.M.GG] = (f"{a1} {a2} {n}", SM.M.NM)
        return new_galaxy, GG

    def set_galaxy_dims(self,
                        p_gg_sz: str) -> tuple:
        """Set basic dimensions for galaxy: location, diameter of stars,
          total mass, black hole mass, halo radius, and thickness of stars.
          Compute location relative to center of GC.
          No restrictions (yet) on how close or how far from GC center.
          No attempt to modify angle of the galaxy (roll, yaw, etc.). For now,
          all galaxies are assumed to be "flat" with respect to the galactic
          cluster; and all clusters lie on parallel planes.
        :args:
        - p_gg_sz (str): 'S', 'M' or 'L'
        :returns:
        - (xyz vector; float X 5): (location relative to center of galactic
                cluster;  x-dim of stars structure, total mass of galaxy,
                mass of central black hole, radius of galactic halo,
                thickness (z-dim ?) of star structure)
        """
        x = 0
        y = 1
        z = 2
        loc = self.GC[f"{SM.M.GC} {SM.M.LOC} {SM.M.VE}"][0]
        shp = self.GC[f"{SM.M.EL} {SM.M.SHA}"][0][0][0]
        min_x = round(loc[x] - (shp[x] / 2))
        max_x = round(loc[x] + (shp[x] / 2))
        min_y = round(loc[y] - (shp[y] / 2))
        max_y = round(loc[y] + (shp[y] / 2))
        min_z = round(loc[z] - (shp[z] / 2))
        max_z = round(loc[z] + (shp[z] / 2))
        lx = random.randrange(min_x, max_x)
        ly = random.randrange(min_y, max_y)
        lz = random.randrange(min_z, max_z)
        gg_loc = (lx, ly, lz)
        # compute diameter (x dim), total mass, black hole pct
        dims = {'S': {'diam': random.randrange(100, 501),
                      'mass': random.randrange(50_000, 800_000_001),
                      'bh_pct': random.randrange(50, 71) / 10000},
                'M': {'diam': random.randrange(80_000, 500_001),
                      'mass': random.randrange(500_000_000, 500_000_000_001),
                      'bh_pct': random.randrange(15, 21) / 1000},
                'L': {'diam': random.randrange(2_000_000, 100_000_001),
                      'mass': random.randrange(1_000_000_000_000,
                                               10_000_000_000_001),
                      'bh_pct': random.randrange(18, 27) / 1000}}
        # compute black hole mass, halo radius, depth (z dim)
        bhole_mass = dims[p_gg_sz]['mass'] * dims[p_gg_sz]['bh_pct']
        halo_r = (dims[p_gg_sz]['diam'] / 2) +\
                 (dims[p_gg_sz]['diam'] * (random.randrange(1, 3) / 100))
        # review this. think about it. I think this is actually the Y dim?
        # I suppose it all a matter of perspective. When looked at from
        # "above", then yes this is the z-dimension.
        stars_z = dims[p_gg_sz]['diam'] * (random.randrange(8, 12) / 100)
        return (gg_loc, halo_r, dims[p_gg_sz]['diam'], stars_z,
                dims[p_gg_sz]['mass'], bhole_mass)

    def detect_g_collision(self,
                           p_GC_nm: str,
                           p_gg_loc: tuple,
                           p_halo_r: float) -> bool:
        """Determine if new Galaxy will collide with any existing Galaxies
        within the current Galactic Cluster. Compute roughly using a bounding
        rectangle around the galaxy halo.
        :args:
        - p_GC_nm (str): Name of current Galactic Cluster
        - p_gg_loc (tuple): (x, y, z) location of galaxy center relative to
                            center of Galactic Cluster
        - p_halo_r (float): Radius of Galaxy
        :returns:
        - (bool) True if collision detected, else False
        """
        collision_detected = False
        x = 0
        y = 1
        z = 2
        gc_loc = self.GC[f"{SM.M.GC} {SM.M.LOC} {SM.M.VE}"][0]

        # Define bounding rectangle for new galaxy
        min_x = round(p_gg_loc[x] - p_halo_r)
        max_x = round(p_gg_loc[x] + p_halo_r)
        min_y = round(p_gg_loc[y] - p_halo_r)
        max_y = round(p_gg_loc[y] + p_halo_r)
        min_z = round(p_gg_loc[z] - p_halo_r)
        max_z = round(p_gg_loc[z] + p_halo_r)
        # Find other galaxies in cluster and compare
        db_gg = DB.execute_select('SELECT_ALL_GALAXIES')
        galaxy_bunch = dict()
        for ix, db_c_nm in enumerate(db_gg['cluster_name_fk']):
            if p_GC_nm == db_c_nm:
                g_nm = db_gg['galaxy_name'][ix]
                g = pickle.loads(db_gg['galaxy_object'][ix])
                # Define bounding rect for existing galaxy
                # TODO --
                # Haha! So in this case, EVERYTHING was a collision...
                #  exactly the opposite of what happened with the clusters.
                # Need to review logic in both cases. Go slow. Look at one
                #  case at a time. Examine the location vectors, the sizes,
                #  and the bounding rectangles. It may be helpful to try to
                #  do some simple visualizations, even if only at a 2D level.
                r = g[f"{SM.M.GH} {SM.M.RD}"][0]
                loc = g[f"{SM.M.GG} {SM.M.LOC}"][0]
                g_min_x = round(loc[x] - r)
                g_max_x = round(loc[x] + r)
                g_min_y = round(loc[y] - r)
                g_max_y = round(loc[y] + r)
                g_min_z = round(loc[z] - r)
                g_max_z = round(loc[z] + r)
                if not (max_x < g_min_x or min_x > g_max_x or
                        max_y < g_min_y or min_y > g_max_y or
                        max_z < g_min_z or min_z > g_max_z):
                    collision_detected = True
                    break
        return collision_detected

    def set_galactic_bulge(self,
                           p_sz: str,
                           p_total_m: float,
                           p_bhole_m: float,
                           p_stars_x: float,
                           p_stars_z: float) -> tuple:
        """Compute the size, shape and mass of the galactic bulge.
        :args:
        - p_sz (str): Galaxy size (S, M, L)
        - p_total_m (float): Total galaxy mass
        - p_bhole_m (float): Mass of the black hole
        - p_star_x (float): Diameter (x-dim) of the stars cluster
        - p_star_z (float): Height/thick (z-dim) of stars cluster
        :returns:
        - (str, float X 4): (bulge shape, mass, x, y, z dims)
        """
        if p_sz == 'S':
            b_shape = SM.M.SP
            b_mass = p_bhole_m * 0.8
        else:
            b_shape = random.choice([SM.M.SP, SM.M.EL])
            b_mass = p_bhole_m * 1.1
        if b_shape == SM.M.SP:
            b_x = b_y = b_z = p_stars_z * 0.2
        else:
            dims = {'S': {'x': p_stars_x * 0.1,
                          'z': p_stars_x * 0.1},
                    'M': {'x': p_stars_x * 0.2,
                          'z': p_stars_z * 1.2},
                    'L': {'x': p_stars_x * 0.3,
                          'z': p_stars_z * 1.3}}
            b_x = dims[p_sz]['x']
            b_z = dims[p_sz]['z']
            b_y = b_x * 0.7
        return (b_shape, b_mass, b_x, b_y, b_z)

    def set_galactic_matter_and_shape(self,
                                      p_total_m: float,
                                      p_bhole_m: float,
                                      p_bulge_m: float,
                                      p_stars_x: float,
                                      p_halo_r: float) -> tuple:
        """Compute amount of matter in the galaxy.
           Assign a shape to the galaxy's star cluster.
        :args:
        - p_total_m (float): Total mass/matter in galaxy
        - p_bhole_m (float): Mass of black hole
        - p_bulge_m (float): Mass of galactic bulge
        - p_stars_x (float): Width of stars cluster
        - p_halo_r (float):  Radius of entire galaxy out to halo
        :returns:
        (str, float X 5): (shape of stars cluster, y-dim of stars,
                           mass (kg) of stars, mass (kg) of non-stellar
                           baryonic galactic (globular) matter, vol of
                           galaxy in cubic gigaparsecs, mass (kg) of galaxy)

        @TODO:
        - Take a closer look at these values to see if they make any sense.
        """
        total_stars_m = p_total_m - (p_bhole_m + p_bulge_m)
        stars_m = total_stars_m * (random.randrange(997, 999) / 1000)
        globular_m = total_stars_m - stars_m
        stars_shape = random.choice([SM.M.EL, SM.M.SP])
        if stars_shape == SM.M.EL:
            stars_y = p_stars_x * 0.7
        else:
            stars_y = p_stars_x
        g_vol_gpc3 = (4/3) * math.pi * ((p_halo_r / 3.09e19)**3)
        g_mass_kg = self.GC[SM.M.BM][0] *\
            ((g_vol_gpc3 / self.GC[f"{SM.M.GC} {SM.M.VL}"][0]) * 100)
        return (stars_shape, stars_y, stars_m,
                globular_m, g_vol_gpc3, g_mass_kg)

    def generate_new_galaxy(self,
                            p_GC_nm: str,
                            p_galaxy_sz: str = "M"):
        """
        Populate a new Game Galaxy (GG) object. Parts include:
        - the star cluster within the galaxy, spiral or disk
        - the black hole at center of galaxy
        - the overall halo of the galaxy
        - the concentrated bulge of of stars around the black hole
        :args:
        - p_GC_nm (str): Name of enclosing cluster.
        - p_galaxy_sz (str) Optional. Size of Game Galaxy.
                            Must be in ('S', 'M', 'L').
                            Defaults to 'M'.
        :returns:
        - (dict): Data about the new galaxy

        @TODO:
        - Avoid collisions between galaxies inside the galactic cluster
        - (Maybe?) compute galactic rotation within the galactic cluster
        - Simple visualizations
        """
        GG = self.GG
        g_sz = p_galaxy_sz.upper() if p_galaxy_sz in ('S', 'M', 'L') else 'M'

        galaxy_collision = True
        while galaxy_collision:
            g_loc, halo_r, stars_x, stars_z, total_m, bhole_m =\
                self.set_galaxy_dims(g_sz)
            galaxy_collision = self.detect_g_collision(p_GC_nm,
                                                       g_loc, halo_r)
            if galaxy_collision:
                print("Collision detected. Recomputing galaxy...")
            else:
                print("No collision detected. Proceeding with new galaxy...")

        bulge_shape, bulge_m, b_x, b_y, b_z =\
            self.set_galactic_bulge(g_sz, total_m, bhole_m, stars_x, stars_z)

        stars_shape, stars_y, stars_m, globs_m, g_vol, g_mass =\
            self.set_galactic_matter_and_shape(total_m, bhole_m, bulge_m,
                                            stars_x, halo_r)

        self.GG[SM.M.GC] = (p_GC_nm, SM.M.CON)
        self.GG[f"{SM.M.GG} {SM.M.REL} {SM.M.SZ}"] = (g_sz, SM.M.REL)
        self.GG[f"{SM.M.GG} {SM.M.VL}"] = (g_vol, SM.M.GPC3)
        self.GG[f"{SM.M.GG} {SM.M.BM}"] = (g_mass, SM.M.KG)
        self.GG[f"{SM.M.GH} {SM.M.RD}"] = (halo_r, SM.M.LY)
        self.GG[f"{SM.M.BH} {SM.M.MS}"] = (bhole_m, SM.M.SMS)
        self.GG[f"{SM.M.GB} {SM.M.SHP}"] = (bulge_shape, SM.M.SHP)
        self.GG[f"{SM.M.GB} {SM.M.MS}"] = (bulge_m, SM.M.SMS)
        self.GG[f"{SM.M.GG} {SM.M.LOC}"] = (g_loc, SM.M.DIM)
        self.GG[f"{SM.M.GB} {SM.M.DIM}"] =\
            ((b_x, SM.M.LY), (b_y, SM.M.LY), (b_z, SM.M.LY),
             SM.M.DIM)
        self.GG[f"{SM.M.SC} {SM.M.SHP}"] = (stars_shape, SM.M.SHP)
        self.GG[f"{SM.M.SC} {SM.M.DIM}"] =\
            ((stars_x, SM.M.LY), (stars_y, SM.M.LY), (stars_z, SM.M.LY),
             SM.M.DIM)
        self.GG[f"{SM.M.SC} {SM.M.MS}"] = (stars_m, SM.M.SMS)
        self.GG[f"{SM.M.IG} {SM.M.MS}"] = (globs_m, SM.M.SMS)
        DB.execute_insert(
            'INSERT_GALAXY_PROC', (GG[SM.M.GG][0], p_GC_nm,
                                   pickle.dumps(GG)))
        return self.GG

# ==================== OLD CODE, DESIGN NOTES =================================

class AstroIO(object):
    """Class for astronomical data and methods.
    """
    def __init__(self):
        """Allocate class-level variables.
        """
        self.UNIV = dict()  # UniverseModel() or load from pickle
        self.GALAXY = dict()
        self.STARS = dict()
        self.PLANETS = dict()
        self.MOONS = dict()
        """

        - GG - The Game Galaxy: section of TU that is playable.
        It is one galaxy within the GC. There can be multiple GG's
        within a GC.

        """
        pass

    def define_star(self):
        """Define star/sun (SE) inside a GX structure.

        Stars in the SU need to be yellow dwarfs, and located towards
        the outer edge of the galaxy.
        """
        pass

    def define_planet(self):
        """Define planet (PL) inside a SE structure.
        Large heavenly bodies that orbit a star.

        Within a start system, planets or satellites capable of not only
        sustaining but generating life are rare.  Commonly rocky, with
        a thin atmosphere, and a solid surface & molten core.
        The surface usually includes copious amounts of water.

        On the inner part of the system, not too hot, not too cold.
        """
        pass

    def define_satellite(self):
        """Define satellite (moon or other) (ST) inside a PL structure.
        Objects with a fixed orbit around a planet.
        """
        pass

    def set_moons_file_name(self,
                            p_nm: str = "Full"):
        """Return full name of Full Moons data file.
        """
        p_nm = "" if p_nm is None else p_nm.title() + "_"
        file_nm = "/dev/shm/" + p_nm + "Moons.pickle"
        print("Pickle file name: " + file_nm)
        return file_nm

    def get_moons_file(self,
                       p_nm: str):
        """Retrieve the Moons data file.

        :args: p_db_nm (str) - generic file name
        """
        try:
            with open(self.set_moons_file_name(p_nm), 'rb') as f:
                self.FULL_MOONS = pickle.load(f)
            print("Full Moons data file retrieved.")
        except FileNotFoundError:
            print("No Full Moons data file found.")

    def write_moons_file(self,
                       p_nm: str):
        """Store the Full Moons data in pickled file.
        :args: p_nm (str) - generic file name
        :write:
        - _{name}_Moons.pickle file
        """
        try:
            with open(self.set_moons_file_name(p_nm), 'wb') as f:
                pickle.dump(self.FULL_MOONS, f)
            print("Full Moons data file saved.")
        except Exception as e:
            print(f"Full Moons data file not saved:\n{str(e)}")

    def sort_moons_by(self, p_catg: str):
        """Sort moons by specified characteristic.
        """
        m_moons = list()
        for m_nm, m_data in FI.S["space"].items():
            if m_data["type"] == "MOON":
                v = list(m_data[p_catg][0].values())[0]
                u = list(m_data[p_catg][0].keys())[0]
                m_moons.append([v, u, m_nm])
        m_moons.sort()
        print(p_catg.title() + " of Moons" + "\n" + "-" * 40)
        pp((m_moons))

    def common_lunar_orbits(self):
        """Compute synchronization of lunar orbits.

        @DEV:
        - Try to avoid having huge methods, even if they are organized
          into sub-functions.
        - In may cases, those sub-functions should be more abstrated as
          class-level functions, even if (pseudo)-private ones.
        - Alway think of algorithm design in functional/Haskell-like terms.
        """
        def init_moons_data():
            """Init a local structure for augmenting moon schema data with
            info on how much of the arc of orbit has been completed on a given
            day, and how many orbits have been completed.
            """
            moons_data = dict()
            for m_nm, m_data in FI.S["space"].items():
                if m_data["type"] == "MOON":
                    moons_data[m_nm] = {
                        "daily_arc": round(360/ m_data["orbit"][0]["days"], 2),
                        "arc_done": 0.00, "orbits_done": 0}
            return moons_data

        def compute_orbits(max_days, day_incr, moons_data):
            """Compute lunar orbits.
            :args:
            - max_days: (float)
                Maximum number of days, since Day Zero, for which to compute lunar orbits.
            - day_incr: (float)
                Decimal increment for count of days since Day Zero.
            - moons_data: (dict)  - see init_moons_data()

            Writes data to self.FULL_MOONS when a full moon (orbit completion) occurs.
            Full moon data is grouped by integer day.

            @DEV:
            - Enhance to account for near-conjunctions of moons, say when they are within
                2 degrees or 5 degrees of each other.
            """
            ticker = ""
            prev = math.floor(time.process_time())
            full_moons = dict()
            d_day = 0.00
            while d_day < max_days:
                d_day = round((d_day + day_incr), 2)
                i_day = round(d_day)
                for m_nm, m_data in moons_data.items():
                    arc_done = (m_data["arc_done"] +
                                (m_data["daily_arc"] * day_incr))
                    if arc_done >= 360.00:
                        m_data["orbits_done"] += 1
                        m_data["arc_done"] = 360.00 - arc_done
                        if i_day not in full_moons:
                            full_moons[i_day] = list()
                        full_moons[i_day].append(
                            {m_nm: (m_data['orbits_done'], round(d_day, 2))})
                    else:
                        m_data["arc_done"] = arc_done
                this = math.floor(time.process_time())
                if this > prev:
                    if this % 60 == 0:
                        ticker = '.'
                    else:
                        ticker += "."
                    print(ticker)
                    prev = this
            return full_moons

        def convert_epoch_day_to_agd(full_moons: dict):
            """Convert day number to AGD (Agency Gavoran Date format)

            @DEV:
            I may want to just keep index as Epoch Day if I am going
            to use a single large calendar file to track all days since
            the Catastrophe? Or maybe not. I'm not sure yet. It is easy
            enough to convert to AGD, so I'll do that for now. Though
            averaging out the length of a year to 365.24 days may not be
            precise enough.

            :args:
            - full_moons: (dict) - see compute_orbits()
            """
            for epoch_day, m_data in full_moons.items():
                if len(m_data) >= 0:
                    year = math.floor(epoch_day / 365.24)
                    d_day = epoch_day - (year * 365.24)
                    day = math.floor(d_day)
                    agd = f"{year:05d}.{day:03d}"
                    self.FULL_MOONS[epoch_day] = {'agd': agd, 'data': m_data}

        # common_lunar_orbits() main
        # ==========================
        # print(f"Start Time: {math.floor(time.process_time())} seconds")
        self.FULL_MOONS = dict()
        moons_data = init_moons_data()
        full_moons = compute_orbits(3500000, 0.01, moons_data)
        convert_epoch_day_to_agd(full_moons)
        self.write_moons_file('Full')
        elapsed = math.floor(time.process_time())
        print(f"Elapsed Time: {round((elapsed / 60), 1)} minutes")

    def analyze_full_moons(self,
                           fulls_cnt: int = 1,
                           start_epoch_day: int = 1,
                           end_epoch_day: int = 3509999):
        """Read in the Full Moons pickled data file.
        Run various types of analysis on it.
        - I have backed up file w/data for 10,000 years (3.5 M days) pickled
          to /home/dave/saskan/cache/Full_Moons_3500000.pkl

        :args:
        - fulls_cnt: (int) default = 1
            Greater than zero means: "report for days with any full moons".
            Auto sets to 1 if less than 1.
            One: report on all Full Moons.
            Two: show data for dates when there are 2 or more Full Moons; ..
        - start_epoch_day: (int) default = 1
            Run report starting at specified epoch day
        - end_epoch_day: (int) default = 0
            Run report ending at specified epoch day

        Other report options:
        - Max number of Full Moons on a single day?
        - Pattern of 4 Full Moons? Is there any regularity to it?
        - ..for 2, 3, and 5 Full Moons?
        - Rank moons that appear mot often in conjunction of...
            - 2 full moons; 3; 4; 5

        More complex analysis:
        - Based on cycle(s) of full moon conjunctions, design lunar calendars:
            - Straight arithmetic lunar-only, based on 1, 2, 3, 4 moons.
            - Hybrid lunar-solar calendar based on 1, 2, 3, 4 moons.
        """
        self.get_moons_file('Full')
        full_moons_rpt = dict()
        full_moons_data = dict()
        fulls_cnt = 1 if fulls_cnt < 1\
            else fulls_cnt
        start_epoch_day = 1 if start_epoch_day < 1 or start_epoch_day > 350000\
            else start_epoch_day
        end_epoch_day = 999999 if end_epoch_day < 1 or end_epoch_day > 3509999\
            else end_epoch_day
        full_moons_data = {e_day: data for e_day, data in self.FULL_MOONS.items()
                          if len(data['data']) >= fulls_cnt and
                          e_day >= start_epoch_day and
                          e_day <= end_epoch_day}
        full_moons_rpt = (len(full_moons_data), full_moons_data)
        pp((full_moons_rpt))

        def assign_moon_data(epoch_day):
            """Set data on self.CAL for full moons, if any, on given epoch day.
            For each full moon, get its angular diameter, distance from planet,
            and epoch day with a decimal fraction, which tells us at what time
            during the day the moon is completely full. These values can be
            used by the renderer to draw the moons in the sky.
            """
            if epoch_day in self.FULL_MOONS:
                self.CAL[epoch_day]["moons"] = dict()
                for m_data in self.FULL_MOONS[epoch_day]["data"]:
                    for moon_nm, m_info in m_data.items():
                        self.CAL[epoch_day]["moons"][moon_nm] = {
                            "epoch_day": m_info[1],
                            "ang_diam_dg":
                              FI.S["space"][moon_nm]["angular_diameter"][0]["dg"],
                            "dist_km":
                              FI.S["space"][moon_nm]["distance"][0]["km"]}

        def get_days_in_turn(ft_cycle_turn: int,
                             cal_data: dict,
                             cal_key: str):
            """Get number of days in the current turn.
            :args:
            - ft_cycle_turn: (int) - turn number (1..4) in a FT cycle
            - cal_data: (dict) - calendar data
            - cal_key: (str) - calendar key
            :return:
            - diy: (int) - days in year for selected calendar turn
            """
            diy = round(turns[cal_data[cal_key]["turn_type"]]['diy'])
            if cal_data[cal_key]["leap"] is not None:
                if ft_cycle_turn\
                    % cal_data[cal_key]["leap"]["turn"] == 0:
                        diy += cal_data[cal_key]["leap"]["days"]
            return diy

        def pickle_cal_file(report_day):
            """ Pickle the file, using specified self.CAL data.
            """
            file_range = f"{self.CAL[report_day]['AGD']['turn'] - 3:05d}-" +\
                         f"{self.CAL[report_day]['AGD']['turn']:05d}"
            self.write_cal_file(file_range)
            print(f"\nCalendars file written for {file_range}" +
                  f" with {len(self.CAL)} data records")

    def get_orbit_and_angular_diameter(
            self,
            p_moon: str):
        """Calculate orbital period and angular diameter of moon.
        Compute:
        - Orbital period (T) in seconds
        - Orbital period (T) in days
        - Angular diameter (θ) in radians
        - Angular diameter (θ) in degrees

        :args:
        - p_moon: str index of schema data for Moon
        """
        moon = FI.S["space"][p_moon]
        G = 6.67430e-11  # m^3/kg/s^2 = gravitational constant
        p_mass = FI.S["space"]["Gavor"]["mass"][0]["kg"]
        p_m_distance = moon["distance"][0]["km"] * 1000
        m_diameter = moon["diameter"][0]["km"] * 1000

        # Calculate orbital period (T) in seconds
        orbital_period = math.sqrt(
            (4 * math.pi**2 * p_m_distance**3) / (G * p_mass))
        # Convert seconds to days
        orbital_period_days = orbital_period / (24 * 60 * 60)

        # Calculate angular diameter (θ) in degrees
        angular_diameter_rad =\
            2 * math.atan(m_diameter / (2 * p_m_distance))
        angular_diameter_deg = math.degrees(angular_diameter_rad)

        print("Orbital Period of moon:  ", orbital_period_days, " days")
        print("Angular Diameter of moon:  ", angular_diameter_deg, " degrees")

    def simulate_lunar_orbit(self):
        """Simulate the orbit of a moon around a planet.

        This code was generated by ChatGPT. On my current set up,
        it does not produce an animation. But perhaps this will
        help to get started doing stuff like this using PyGame?
        """

        # Constants
        G = 6.67430e-11  # Gravitational constant in m^3 kg^-1 s^-2

        # Planet properties
        planet_mass = 5.972e24  # kg
        planet_radius = 6371e3  # m

        # Moon properties
        moon_mass = 7.345e22  # kg
        moon_distance = 384400e3  # m
        moon_radius = 3500e3  # m
        moon_orbit_period = 24 * 3600  # seconds (1 day)

        # Initial conditions
        initial_angle = 0
        initial_velocity = np.sqrt((G * planet_mass) / moon_distance)

        # Simulation parameters
        num_steps = 1000
        time_step = moon_orbit_period / num_steps

        # Initialize arrays to store data
        moon_positions = np.zeros((num_steps, 2))  # x, y positions

        # Simulation loop
        angle = initial_angle
        for step in range(num_steps):
            x = moon_distance * np.cos(angle)
            y = moon_distance * np.sin(angle)
            moon_positions[step] = [x, y]

            # Update angle using circular orbit equation
            angular_velocity = initial_velocity / moon_distance
            angle += angular_velocity * time_step

        # Plotting
        fig, ax = plt.subplots()
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel('X Distance (m)')
        ax.set_ylabel('Y Distance (m)')
        ax.set_title('Moon Orbit Simulation')

        orbit_line, = ax.plot([], [], 'r')
        moon_circle = plt.Circle((0, 0), moon_radius, color='blue', fill=False)

        ax.add_artist(orbit_line)
        ax.add_artist(moon_circle)

        def animate(frame):
            orbit_line.set_data(moon_positions[:frame, 0], moon_positions[:frame, 1])
            return orbit_line,

        ani = FuncAnimation(fig, animate, frames=num_steps, interval=50, blit=True)

        plt.show()


    def planetary_congruence(self):
        """When star-gazing, they would
        appear to be aligned probably if wihinin a few degrees
        of one another.

        Furthermore, it is(apparent) congurence as
        occurs from the perspective of Gavor (the planet).

        To get this perspective, figure out the degreees with respect
        to Faton, and then similar for the planets being looked
        at. If the angles are similar within a specified range,
        then (apparent) congruence can be said to occur.

        Note that this will happen much more often than "actual"
        congruence.
        # 1) What is the "margin of error" from Gavor's perspective
        # such that an observer would say congruence is happening?
        # Is it different for each planet? Is it different for
        # plants closer to Faton vs. those farther away? --> +/- 5 degrees.

        # 2) Assuming "counterclocwise" revolutions around Faton,
        # from perfpective of Faton's north pole, and assuming
        # that all planets were at "degree zero" (perfectly aligned)
        # on "Day Zero", what is the degree of each planet as they
        # proceed around Faton? The "days" list identifies their orbital
        # degree. The "diff" list identifies their congruence with Gavor
        # to within plus or minus 5 degrees.
        """
        planets = self.CAL.PLANETS["Faton"]
        for p_nm in planets.keys():
            planets[p_nm]["days"] = []
            planets[p_nm]["diff"] = []
        for day in range(0, 250):
            for p_nm, p_dat in planets.items():
                planets[p_nm]["days"].append(
                    round(((day / p_dat["orbit"]) * 360) % 360, 2))
            gavor_degrees = planets["Gavor"]["days"][day]
            for p_nm in [p for p in planets.keys() if p != "Gavor"]:
                p_degrees = planets[p_nm]["days"][day]
                if gavor_degrees < 6 and p_degrees > 354:
                    p_degrees = p_degrees - 354
                diff = round(abs(gavor_degrees - p_degrees), 2)
                if diff < 5.01:
                    planets[p_nm]["diff"].append("*" + str(diff))
                else:
                    planets[p_nm]["diff"].append(str(diff))
        pp(planets)

    def lunar_phases(self,
                     p_lunar_obj,
                     p_planet_nm: str,
                     p_moon_nm: str):
        """Compute the phases of a moon. The new, quarter,
        and full phases occur on specific days. Waning
        and waxing phases occur between these days.
        The times are computed as fractions of an orbit,
        which is calculated in Gavotan days. The "common"
        reference to the phases should probably extend
        on either side of the computed day/time.

        Note that this algorithm simply defines the phases.
        It does not determine what phase a mmon is in on a
        given date.

        Pass in object names (IDs) rather than the
        object itself.

        Simplify for now to assume the planet is Gavor.

        :args:
        - p_lunar_obj (object): object from CAL class
        - p_planet_nm (str): name of planet around which it orbits
        - p_moon_nm (str): name of moon
        :return: phases (dict) = {phase_nm: day_num, ..}
        """
        orbit = p_lunar_obj[p_planet_nm][p_moon_nm]["orbit"]
        phases = {"new": orbit,
                  "waxing crescent": orbit * 0.125,
                  "1st quarter": orbit * 0.25,
                  "waxing gibbous": orbit * 0.375,
                  "full": orbit * 0.5,
                  "waning gibbous": orbit * 0.625,
                  "3rd quarter": orbit * 0.75,
                  "waning crescent": orbit * 0.875}
        return phases

    def position_zero(self):
        """
        The main conceit is that all the planets and moons
        were in a grand alignment as of year zero. This is
        reckoned as day 0.0 of their orbits, except for the
        moons, when it is their Full (50%) phase of their orbits.
        """
        zero_point_orbits = {
            "planets": {
                "Paulu-Kalur": 0.0,
                "Astra": 0.0,
                "Gavor": 0.0,
                "Petra": 0.0,
                "Kalama": 0.0,
                "Manzana": 0.0,
                "Jemlok": 0.0},
            "moons": {
                "Endor": 16.05,
                "Sella": 11.75}}
        return (zero_point_orbits)
