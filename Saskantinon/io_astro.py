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
- may add in use of SASKAN_DB database also
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import pendulum
import pickle
import random
import time

from os import path
from matplotlib.animation import FuncAnimation
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_file import FileIO              # type: ignore
from saskan_math import SaskanMath      # type: ignore

FI = FileIO()
SM = SaskanMath()


class UniverseModel:
    """Class for modeling a universe.
    - TU = Total Universe
    - GC = Galactic Cluster in which the game is played
    - TP = Timing Pulsar (neutron star) in the GC which
           regulates time measurements within the GC.
    - XU = External Universe, outside of the GC

    All values are defined as a 2-tuple where
    [0] = value and [1] = type of measurement unit, as defined
    by the SaskanMath() class. The type of object, i.e., what
    is being measured, is also identified via reference
    to a value defined in SaskanMath()'s "M" dataclass.

    For the purposes of the game, we consider mass and matter to
    be the same thing. Antimatter equals matter at the big bang, but
    then almost entirely vanishes. No one know why. Theoretically,
    the universe should not exist since matter and antimatter should
    have annihilated each other. But it does. So, we will assume that
    the universe is made of matter, not antimatter, and that the
    antimatter "went somewhere".
    
    For game purposes, the Total Universe is considered to be a sphere.
    The origin point at the center of the sphere is where this known
    universe began, its big bang point. Or in game terms, where the
    last game universe ended and a new one began.

    Volume of known universe: 3.566 x 10^80 cubic meters
    Another estimate is 415,065 Glyr3  (cubic gigalight years)
    """
    def __init__(self,
                 p_load_model_nm: str = None,
                 p_randomize: bool = False,
                 p_univ_name: str = None,
                 p_cluster_name: str = None,
                 p_pulsar_name: str = None,
                 p_random_seed: int = None):
        """Load or create Total Universe, External Universe,
           Galactic Cluster and Timing Pulsar.
        :args:
        - p_load_model_nm (optional). If provided, load object from
          pickled file with this name. Ignore all other parameters.
          If not provided, pass all other params to generate_universe().
        """
        if p_load_model_nm is not None:
            model_nm = p_load_model_nm if '.pkl' in p_load_model_nm\
                else p_load_model_nm + '.pkl'
            file_path = path.join(FI.D['APP'],
                                  FI.D['ADIRS']['SAV'],
                                  model_nm)
            self.UNIV = FI.get_pickle(file_path)
        else:
            self.generate_universe(p_randomize,
                                   p_univ_name,
                                   p_cluster_name,
                                   p_pulsar_name,
                                   p_random_seed)
        pp((self.UNIV))

    def generate_universe(self,
                          p_randomize: bool = False,
                          p_univ_name: str = None,
                          p_cluster_name: str = None,
                          p_pulsar_name: str = None,
                          p_random_seed: int = None):
        """Define data for a new Total Universe, External Universe,
           Galactic Cluster and Timing Pulsar. Use standard estimates
           for known universe, with small tweaks for variety.
        :args:
        - p_randomize (optional). If true, randomize size of TU.
        - p_univ_name (optional). If provided, name of Total Universe.
        - p_cluster_name (optional). If provided, name of Galactic Cluster.
        - p_pulsar_name (optional). If provided, name of Timing Pulsar.
        - p_random_seed (optional). If provided, use to seed randomization.
        """
        self.randomize = p_randomize
        self.random_seed = p_random_seed
        TU = dict()
        if self.randomize:
            # Generate random TU size within predefined constraints
            TU[SM.M.RD] = self.generate_random_radius()
            variance = TU[SM.M.RD][0] / 14.25e9
        else:
            # Use predefined size for TU
            TU[SM.M.RD] = (14.25e9, SM.M.GPC)  # 14.25 gigaparsecs
            variance = 1.00
        # Volume of known universe: 3.566 x 10^80 cubic meters
        # or 415,065 cubic giga lightyears
        TU[SM.M.VL] = (415065 * variance, SM.M.GLY3)
        # Age of TU in Gavoran years
        TU[SM.M.ET] = (13.787e9, SM.M.GY)
        # Expansion rate: km/s per Mpc
        TU[SM.M.ER] = (73.3, SM.M.UE)
        # Total matter in TU: 1.5 x 10^53 kg
        TU[SM.M.MS] = (1.5e53 * variance, SM.M.KG)
        # Dark Energy: 68.3%, of total matter in TU
        TU[SM.M.DE] = (TU[SM.M.MS][0] * 0.683, SM.M.KG)
        # Dark Matter: 27.4%, of total matter in TU
        TU[SM.M.DM] = (TU[SM.M.MS][0] * 0.274, SM.M.KG)
        # Baryonic Matter: 4.3%, of total matter in TU
        TU[SM.M.BM] = (TU[SM.M.MS][0] * 0.043, SM.M.KG)
        tu_nm = p_univ_name 
        if p_univ_name is None:
            tu_nm = f"{pendulum.now().to_iso8601_string()}"
            tu_nm = tu_nm.replace('-', '').replace(':', '')[:15]
            tu_nm = "UNIV_" + tu_nm.replace('T', '_')
        else:
            tu_nm = p_univ_name 
        TU[SM.M.TU] = (tu_nm, SM.M.NM)
        # Define the GC and TP within the TU
        GC = self.generate_galactic_cluster(TU, p_cluster_name)
        TP = self.generate_timing_pulsar(GC, p_cluster_name)
        XU = self.generate_external_universe(TU, GC)
        self.UNIV = {'tu': TU, 'xu': XU, 'gc': GC, 'tp': TP}

    def generate_random_radius(self) -> tuple:
        """Generate a random TU radius within predefined constraints.
        :returns:
        - (float, int) - radius, unit of measurement (gigaparsecs)
        """
        if self.random_seed is not None:
            random.seed(self.random_seed)

        # Generate a random radius within a predefined range
        min_radius = 14.0e9
        max_radius = 14.5e9
        return (random.uniform(min_radius, max_radius), SM.M.GPC)

    def generate_galactic_cluster(self,
                                  p_TU: dict,
                                  p_cluster_name: str = None,) -> dict:
        """
        Define the Galactic Cluster (GC) within the TU.

        :args:
        - p_TU (dict) - data for the Total Universe
        - p_cluster_name (str) - (optional) name of the galactic cluster
        :returns:
        - (dict) - data defining the galactic cluster

        Generate a random location vector (x, y, z) in megaparsecs
        locating the GC center as a random point within the TU
        in relation to the TU center (center of the universe)
        Ensure that x, y, and z are at least 2/3 of the TU radius.

        Shaped like a thick flattened sphere, like a chubby pancake.
        A standard geometric formula for defining the shape of a
        flattened sphere can be based on the equation of an ellipsoid.
        An ellipsoid is a three-dimensional shape that can represent a
        flattened or stretched sphere. The formula for an ellipsoid is:
        frac{{x^2}}{{a^2}} + \frac{{y^2}}{{b^2}} + \frac{{z^2}}{{c^2}} = 1

        Where:
        - a represents the semi-major axis, controls extent along the x-axis.
        - b represents the semi-minor axis, controls extent along the y-axis.
        - c represents the semi-minor axis, controls extent along the z-axis.

        To create a flattened sphere shape, set a and b to equal each other
        but smaller (?) than c. This results in an ellipsoid that is flattened
        along one axis (z-axis) compared to a perfect sphere.

        Specific values of a, b, and c will determine exact shape and degree
        of flattening of the ellipsoid.  A typical value is for a, b and c
        to be 1/2 the value of x, y, and z respectively.

        To get a better sense of the shape of an ellipsoid, plot it in
        three dimensions, then use matplotlib for a rough visualization.
        For a more accurate visualization, use a 3D modeling program like
        Blender or Maya.

        The volume of an ellipsoid is given by:

        V=4/3 X π X a X b X c
         where a, b, and c are the semi-axes of the ellipsoid.

        """
        # Name
        cluster_name = p_cluster_name
        if cluster_name is None:
            cluster_name = self.generate_random_cluster_name()
        # location of galactic cluster center relative to TU center
        min_distance = (2/3) * p_TU[SM.M.RD][0]
        while True:
            lx = random.uniform(-p_TU[SM.M.RD][0], p_TU[SM.M.RD][0])
            ly = random.uniform(-p_TU[SM.M.RD][0], p_TU[SM.M.RD][0])
            lz = random.uniform(-p_TU[SM.M.RD][0], p_TU[SM.M.RD][0])
            distance = (lx**2 + ly**2 + lz**2)**0.5
            if distance >= min_distance:
                break
        # Generate a random sized ellipsoid in parsecs
        min_size = 1e6  # 1 million parsecs
        max_size = 1e7  # 10 million parsecs
        x = random.uniform(min_size, max_size)
        y = x * random.uniform(0.5, 0.8)
        z = y * random.uniform(0.1, 0.2)
        a = x / 2
        b = y / 2
        c = z / 2
        # Calculate the volume of the ellipsoid
        volume = (4/3) * 3.14159265359 * a * b * c
        # Generate a GC mass as a pct of the total baryonic matter in TU
        # This will produce a denser or less dense galatic cluster.
        min_mass_pct = 0.01  # 1% - smaller cluster
        max_mass_pct = 0.05  # 5% - larger cluster
        mass_pct = random.uniform(min_mass_pct, max_mass_pct)
        gc_data = {
            "galactic cluster": (cluster_name, SM.M.NM),
            "container": ("", SM.M.TU),
            f"location {SM.M.VE}":  ((lx, ly, lz), SM.M.GPC),
            "shape": ((((x, y, z), SM.M.DIM),
                       ((a, b, c), SM.M.AX)), SM.M.EL),
            SM.M.DE:
            (mass_pct * p_TU[SM.M.DE][0] * p_TU[SM.M.MS][0], SM.M.KG),
            SM.M.DM:
            (mass_pct * p_TU[SM.M.DM][0] * p_TU[SM.M.MS][0], SM.M.KG),
            SM.M.BM:
            (mass_pct * p_TU[SM.M.BM][0] * p_TU[SM.M.MS][0], SM.M.KG),
            SM.M.VL: (volume, SM.M.GPC3)}
        return gc_data

    def generate_random_cluster_name(self) -> str:
        """Generate a random name for the Galactic Cluster
        May want to add logic to come up with a name that is
        based on coordinates, or other legendary names,
        including in-game legends and myths.
        :returns:
        - (str) Name assigned to the GalacticCluster.
        """
        cluster_names = ["Crius Cluster", "Themis Cluster",
                         "Iapetus Cluster", "Cronus Cluster"]
        return random.choice(cluster_names)

    def generate_timing_pulsar(self,
                               p_GC: dict,
                               p_cluster_nm: str,
                               p_pulsar_nm: str = None) -> dict:
        """Define the timing pulsar within the GC.
        :args:
        - p_GC (dict) Data about the Galactic Cluster
        - p_cluster_nm (str) Name of containing cluster
        - p_pulsar_nm (str) Optional. Name of neutron star / timing pulsar
        :returns:
        - (dict) Data about the Timing Pulsar

        Compute a location within the GC that is
        a random distance from the GC center but
        relatively close (inner 1/3rd of the ellipsoid)
        to the core/center of the galactic cluster.
        Cluster shape is ellipsoid, not a sphere; so
        calculuation is more complex than just using
        one radius value.

        cesium-133 vibrates exactly 9,192,631,770 times per second.
        That is a meausre of frequency which could be reproduced
        anywhere in the universe. But it is still culturally-bound in
        that the second itself is derived from the planet Earth's
        relationship to it Sun. This type of time measure is referred
        to as an atomic clock.
        To be more precise, an atomic second related to the unperturbed
        ground state hyperfine transition frequency of the caesium-133 atom.

        Meausuring the rate of pulsar pulses is also very reliable,
        and is the basis for some navigation systems. Not all pulsars
        have the same frequency, but they are all very regular.
        See: https://link.springer.com/article/10.1007/s11214-017-0459-0

        Although observing and correctly measuring the frequency of the
        pulses of a pulsar is technolgically complex, it is very accurate
        and has been proposed as a superior method of timekeeping for
        autonomous spacecraft navigation.  A reference location (that is,
        a particular mature rotation-based pulsar) must be selected.
        This could be the basis for a universal time standard,
        a "galactic clock" that is used, in the game context, by the Agency.

        A pulsar is a highly magnetized rotating neutron star that emits
        beams of electromagnetic radiation out of its magnetic poles.
        Sort of like a galatic lighthouse. The periods range from
        milliseconds to seconds.  The fastest known pulsar, PSR J1748-2446ad,
        rotates 716 times per second, so its period is 1.4 milliseconds.
        Pulsars can be more accurate, consistent than atomic clocks.

        For the game purposes, we'll define the pulsar rate as close to
        716 times per second.

        The idea for the game is to make up a pulsar llike PSR J1748-2446ad,
        assign it a very regular period, and use it as a universal time
        in reference to all other units.

        Time dilation is a phenomenon that occurs when a reference
        frame is moving relative to another reference frame. In the
        case of very fast travel, especially near the speed of light,
        time itself will slow down for the traveler. Also, space-time
        is curved in gravity wells like solar systems. This will need
        to be accounted for if interstellar travel and/or near-light-speed
        or (so-called) warp speed travel is allowed in the game.
        """
        # Generate a random radius within a predefined range
        min_rate = 700  # pulses (rotational frequency) per 'galactic second'
        max_rate = 732
        pulse_rate = random.uniform(min_rate, max_rate)
        # Compute the period in milliseconds
        period_ms = (1 / pulse_rate) * 1000
        # Determine pulsar location
        gc_x = p_GC["shape"][0][0][0][0]
        gc_y = p_GC["shape"][0][0][0][1]
        gc_z = p_GC["shape"][0][0][0][2]
        max_x = (gc_x / 2) * 0.33
        max_y = (gc_y / 2) * 0.33
        max_z = (gc_z / 2) * 0.33
        while True:
            lx = random.uniform(-gc_x, gc_x)
            if lx <= max_x:
                break
        while True:
            ly = random.uniform(-gc_y, gc_y)
            if ly <= max_y:
                break
        while True:
            lz = random.uniform(-gc_z, gc_z)
            if lz <= max_z:
                break
        # Set star name
        star_names = [(f"N_{str(lx)[:5].replace('-', '').replace(',', '')}_" +
                      f"{str(ly)[:5].replace('-', '').replace(',', '')}_" +
                      f"{str(lz)[:5].replace('-', '').replace(',', '')}"),
                      "Timing Pulsar", "Celestial Chrono", "Luminous Sentry",
                      "Eternal Beacon", "Pendula Galaxia", "Nova Clock",
                      "Star Clock"]
        star_nm = p_pulsar_nm if p_pulsar_nm is not None\
            else random.choice(star_names)
        tp_data = {
            SM.M.TP: (star_nm, SM.M.NM),
            "container": (p_cluster_nm, SM.M.GC),
            f"location {SM.M.VE}":  ((lx, ly, lz), SM.M.GPC),
            SM.M.GS: (pulse_rate, SM.M.PS),
            SM.M.PR: (period_ms, SM.M.GMS)
        }
        return tp_data

    def generate_external_universe(self,
                                   p_TU: dict,
                                   p_GC: dict) -> dict:
        """Define the External Universe (XU) within the TU.
        :args:
        - TU (dict) Data about the Total Universe.
        - GC (dict) Data about the Galacti Cluster.

        XU contains all the mass that is not in the GC.
        """
        xu_data = {
            SM.M.XU: ("Beyond the Rim", SM.M.NM),
            "container": ("", SM.M.TU),
            SM.M.DE: (((p_TU[SM.M.DE][0] * p_TU[SM.M.MS][0]) -
                       p_GC[SM.M.DE][0]), SM.M.KG),
            SM.M.DM: (((p_TU[SM.M.DM][0] * p_TU[SM.M.MS][0]) -
                       p_GC[SM.M.DM][0]), SM.M.KG),
            SM.M.BM: (((p_TU[SM.M.BM][0] * p_TU[SM.M.MS][0]) -
                       p_GC[SM.M.BM][0]), SM.M.KG)
        }
        return xu_data

    def save_universe(self):
        """Pickle UNIV object and write to a file."""
        file_path = path.join(FI.D['APP'],
                              FI.D['ADIRS']['SAV'],
                              self.UNIV['tu'][SM.M.TU][0] + '.pkl')
        FI.write_pickle(file_path, self.UNIV)
        print(f"UniverseModel saved to {str(file_path)}")

    # Example usage:
    # Create a UniverseModel instance and generate a random Galactic Cluster
    # model = UniverseModel(randomize=True)
    # gc = model.generate_galactic_cluster()
    # print(gc)

    # Use standard io_file() methods instead....
    # def save_to_file(self, filename):
    #     # Save the model to a file using pickle
    #     with open(filename, "wb") as file:
    #         pickle.dump(self, file)

    # @classmethod
    # def load_from_file(cls, filename):
    #     # Load the model from a file using pickle
    #     with open(filename, "rb") as file:
    #         return pickle.load(file)

    # Example usage:
    # Create a UniverseModel instance and save it to a file
    # model = UniverseModel(randomize=True)
    # model.save_to_file("universe_model.pkl")

    # Load the model (instantiated class object) from a file
    # Take note -- a class object can be instantiated from a pickle...
    # loaded_model = UniverseModel.load_from_file("universe_model.pkl")


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

    def set_astro_file_name(self,
                            p_schema: str) -> path:
        """Return full path to an Astro data file.
        They are stored in $APP/cache/
        :args:
        - p_schema (str) - like 'universe', 'galaxy',
            'star', 'planet', or 'moon'
        """
        file_nm = path.join(
            FI.D["APP"], FI.D["ADIRS"]["SAV"],
            f"astro_{p_schema}.pickle")
        return file_nm

    def define_universe(self,
                        p_smaller: bool = False,
                        p_larger: bool = False) -> dict:
        """Define universe. Drawing on some of the concepts in the old
        'universe.py' module (see ontology_lab).

        Concepts defining the game space include the following.

        There should be callable python methods for each of these,
        building on the previous one and accepting parameters.


        - TU = The Total Universe. The entire game universe. Most of it
        will be non-playable. For game purposes, define it as a sphere
        with a radius close to 14.25 gigaparsecs, expanding at a rate of 73.3 kilometers per second per megaparsec, in all directions.

        It is the largest astronomical  unit  defined for game play.  Size
        should be fairly constant, with only minor changes for each newly
        created object; then should fluctuates as the game universe expands during game time (only relevant for very long-lasting scenarios).

        Age of a TU at start of a game is 13.787±0.020 billion years, give or take.  The game software can generate multiple universes, but each
        is assumed to "occupy" the same space and time as the others and
        they do not interact with each other.

        The origin point at the center of the sphere is where this known
        universe began, its big bang point. Or in game terms, where the
        last game universe ended and a new one began. This may be used in
        a ludic context related to generations of "karma" and so on, but
        has no actual physical model.

        Dark Energy comprisees 68.3% of the universe, Dark Matter 27.4%,
        remaining 4.3% is baryonic matter (stars, planets, life, etc.),
        also referred to as "ordinary matter".

        Ordinary matter/mass = approximately 1.5×10^53 kg
        For game purposes, take 4.3% as the approximate area of
        the TU sphere that contains galaxies, stars, planets, etc.

        It is exapanding in all directions at a rate of 73.3 kilometers
        per second per megaparsec.

        Dark Energy comprisees 68.3% of the universe, Dark Matter 27.4%,
        remaining 4.3% is baryonic matter (stars, planets, life, etc.),
        also referred to as "ordinary matter".

        Ordinary matter/mass = 1.5×10^53 kg
        For game purposes, I will take 4.3% as the approximate area of
        the TU sphere that contains galaxies, stars, planets, etc.

        The universe may be infinite. We guess at measure of the
        __observable__ universe. Being accurate is hard since no one
        really knows its shape, and it is expanding, and that expansion
        will limited by the mass of all the matter in the universe, and
        the nature of that mass is also a bit of a mystery.
        We can use these numbers, and vary them a little, just for fun!

        - GC - The Game galaxy Cluster which contains the playable galaxy.
        It is located in the XU, but is named and defined in a bit more
        detail, including have some of its galaxies identified. It's
        definition includes info about the galactic core.

        - TP = The timing pulsar. Within a GC define a pulsar that is
        used to measure time by space-traveling civilizations within that
        cluster. It is a very regular pulsar, and is used as a universal time
        standard. It is not the only pulsar in the cluster, but is the one
        that is used for timekeeping.

        - XU - External Universe: section(s) of TU that are not playable;
        no detailed galactic clusters.  Everything outside of the GC.
        Simulate some forces, movement, but not any inhabited systems.
        Situate some supernovae, black holes, galaxy cluster, etc. in
        the XU.

        Angular diameter is the apparent size of an object as
        seen from a point of view, i.e., how big a moon appears
        in the sky. Given the distance (d) and diameter (D) of
        an object, its angular diameter (δ) can be calculated
        as follows:
        δ = 2 × arctan(D/2d)

        In this class, we want to focus on
        - actual and apparent (from Gavor) sizes
        - mass and gravity
        - distance from Gavor
        - relative motion (speed, direction)
        Try to avoid:
        - Jumping into time units.
            - See section of defining a second in non-relative terms.
            - Think of days as rotations of planet or moon, years as orbits.
        - Making the math too complex
        - Hard-coding values too much, even in schema

        Math...

        The area of a sphere is 4 * Pi * radius squared (4 * pi * r**2).

        The distance between two points (x1, y1), (x2, y2) on a plane is:
        the square root of (x2 - x1) squared plus (y2 - y1) squared,
        that is:  sqrt((x2 - x1)**2 + (y2 - y1)**2)

        The distance between two points in xyz-space is square root of
        sum of the squares of the differences between coordinates.
        That is,
            given P1 = (x1,y1,z1) and P2 = (x2,y2,z2),
            the distance between P1 and P2 is given by
            d(P1,P2) = sqrt ((x2 - x1)2 + (y2 - y1)2 + (z2 - z1)2).

        This measures will come into play when we start to define bodies
        in space and the graviational effect they have on each other.

        A common measure of mass is the solar mass, which is the mass of
        our Sun, Sol. In the game world, of Fatun. In either case, it
        is unit. The mass of the Sun is 1.9891 x 10^30 kg. But one solar
        mass is 1.0.

        Define one or more python methods, organized in a class module,
        to generate a model TU for game play  purposes. It should indicate
        size, mass, rate of expansion, etc., using center of sphere as
        (rough) reference point to identify TU, XU, and GC boundaries and
        characteristics, including the total baryonic mass available to work
        with in the GC and location of the TP within the GC.

        Parameters:  allow for either accepting  a random diameter within
        pre-defined constraints, or for a simple input indicating to
        generate the model of a slightly larger or slightly smaller
        universe, in relationship to the predefined constraints.

        Return the model as an instantiated class object. Include methods
        to save the model to a file, such as a pickled file, and to load it
        from a file.

        - GG - The Game Galaxy: section of TU that is playable.
        It is one galaxy within the GC. There can be multiple GG's
        within a GC.

        - SSG - Simulated Star Systems Group is a section of the GG where
        multiple star systems are simulated, including their planets and
        the planets' satellites. It begins with describing the star only.
        Fill in other details only as needed. The SSG is a defined playable
        area of the GG.

        There can be multiple SSG's within a GG.

        - SSS - Simulated Star System. A section of the SSG where a star
        and its planets are simulated. It begins with describing the star
        only. Fill in other details only as needed. The SSS is a defined
        playable area of the SG. There can be multiple SSS's within a SG.

        The SSS needs to be about 1/3 of the way towards the galactic core
        from the rim of the GG. Any closer and destruction by supernovae
        is likely.  Star systems expected to have life-bearing planets
        should include at least two gas giants, not just one, so that
        they can tug on each other and prevent the rocky planets from
        being sucked into the sun along with the gas giant.

        Other scenarios are possible, but this is the most common one.

        An SSS sun should be relatively small but large enough to warm
        the inner planets.  The sun should be a yellow dwarf, not a
        red dwarf, so that it can support life.



        SPS - Simulated Planetary System. A section of the SSS where
        a planet and its satellites are simulated. It begins with the
        planet. Fill in other details only as needed. The SPS is a
        defined playable area of the SSS. There can -- and really should
        be multiple SPS's within a SSS.

        If the SPS is intended to support organic life, it should be
        relatively close to the star, but not too close, or be a moon
        of a gas giant and have its own atmosphere.

        Based on inputs and rules, return dimensions, mass, rate of
        expansion, etc. for each section of such a play Universe.
        """
        pass

    def define_pulsar(self):
        """
        cesium-133 vibrates exactly 9,192,631,770 times per second.
        That is a meausrement of frequency which could be reproduced
        anywhere in the universe. But it is still culturally-bound in
        that the second itself is derived from the planet Earth's
        relationship to it Sun. This type of time measure is referred
        to as an atomic clock.
        To be more precise, an atomic second related to the unperturbed
        ground state hyperfine transition frequency of the caesium-133 atom.


        Meausuring the rate of pulsar pulses is also very reliable,
        and is the basis for some navigation systems. Not all pulsars
        have the same frequency, but they are all very regular.
        See: https://link.springer.com/article/10.1007/s11214-017-0459-0

        Although observing and correctly measuring the frequency of the
        pulses of a pulsar is technolgically complex, it is very accurate
        and has been proposed as a superior method of timekeeping for
        autonomous spacecraft navigation.  A reference location (that is,
        a particular mature rotation-based pulsar) must be selected.
        This could be the basis for a universal time standard,
        a "celestial clock" that is used by the Agency.

        A pulsar is a highly magnetized rotating neutron star that emits
        beams of electromagnetic radiation out of its magnetic poles.
        Sort of like a galatic lighthouse. The periods range from
        milliseconds to seconds.  The fastest known pulsar, PSR J1748-2446ad,
        rotates 716 times per second, so its period is 1.4 milliseconds.
        Pulsars can be more accurate, consistent than atomic clocks.

        The idea for the game is to make up a pulsar llike PSR J1748-2446ad,
        assign it a very regular period, and use it as a universal time
        in reference to all other units.


        Time dilation is a phenomenon that occurs when a reference
        frame is moving relative to another reference frame. In the
        case of very fast travel, especially near the speed of light,
        time itself will slow down for the traveler. Also, space-time
        is curved in gravity wells like solar systems. This will need
        to be accounted for if interstellar travel and/or near-light-speed
        or (so-called) warp speed travel is allowed in the game.
        """
        pass

    def define_galactic_cluster(self):
        """Define galactic cluster (GC) inside an IU structure.
        """
        pass

    def define_galaxy(self):
        """Define galaxy (GX) inside a GC structure.

        Galaxies in the SU need to be suitably distant from each other.
        Galactic collisions/mergers are common in the TU, but would be
        problematic in the SU.
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
