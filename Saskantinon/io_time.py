#!python
"""
:module:    io_time.py

:author:    GM (genuinemerit @ pm.me)

Prototype definitions of astro-temporal events
in a game world's local star system. Define calendars
for the passage of time, including era, epoch, year,
season, month, day, noon, midnight, sunrise, sunset,
phases of moons, timing of planetary conjunctions.

Currently a single time zone that
encompasses the lands of the game, spread over 2182031 km^2.
(1660 km east-west, 1310 km north-south), located in the
northern hemisphere. So, two major time zones would be
appropriate. And given the low technology level, more
local and regional variations would be appropriate.


@DEV:
- Static Values were hard-coded in first prototype.
    - Abstract them into a combo of config JSON file +
      algo-driven data.
- Provide tweaks to alter local time settings in various ways.
- Provide a way to set a time zone, for example, or to allow
  for oddball variations in terminology and accuracy.
- Rather than hard-coding the Moons data, provide an algorithm to
  compute their mass, rotation, revolution, position, relative
  to the planet. In any case, have more than two moons.
- Try to come up with some kind of algorithm to estimate tides
  on the major shores and river deltas of the game world.
- Do the same for planets.
- All of this implies brings a geo data set into the mix.
    - May be useful to use io_graphs to visualize the geo data.
    - Use the places spreadsheet as a starting point, but store
      as JSON this time.
- If really feeling ambitious, do something similar for stars
  in the local galaxy and galaxies in the local cluster.
- See ontology lab (universe.py, region.py) for ideas.
- See map_build.py and other prototype modules for ideas.
- See schema/places_data.ods for ideas about data.
- Try to use accurate-ish formulae for the calculations,
  but don't get too wrapped up in it. The point is to have
  something that is amusing and fun to play with.
"""

import json
import pickle

from dataclasses import dataclass   # fields
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

# from io_config import ConfigIO          # type: ignore
from io_file import FileIO              # type: ignore

# CI = ConfigIO()
FI = FileIO()


class TimeIO(object):
    """Class for Calendar-related data and methods.
    Includes astronomical data as well as temporal/calendrical
    data and algorithms. It necessarily intersects with geographical
    data as well in some respects.

    Eventually will want to kind of align it to an io_geo or
    saskan_mapping class.
    """
    def __init__(self):
        """Manage time, calendar and astronomical data.
        Store data in a pickled dict: CALENDAR_DB.

        To save the CALENDAR_DB pickle, call:
            self.set_time_db(p_db_nm)
        To retieve it, call:
            self.get_time_db(p_db_nm)

        :args: p_db_nm: str
            - Generic name of time data file object
            - Example: "time_data"
        """
        self.S_CAL: dict = dict()
        self.S_SEASON: dict = dict()
        self.S_ASTRO: dict = dict()
        self.S_GEO: dict = dict()

    @dataclass
    class C():
        """Values used to do various computations using
        a variety of units and formulae.
        """
        # weight, mass - metric/imperial
        KG_TO_LB = 2.20462262185     # kilos -> pounds
        LB_TO_KG = 0.45359237        # pounds -> kilos
        G_TO_KG = 0.001              # grams -> kilos
        KG_TO_G = 1000.0             # kilos -> grams
        # distance - metric/imperial
        MM_TO_CM = 0.1               # millimeters -> centimeters
        CM_TO_MM = 10.0              # centimeters -> millimeters
        MM_TO_IN = 0.03937007874     # millimeters -> inches
        IN_TO_MM = 25.4              # inches -> millimeters
        CM_TO_IN = 0.3937007874      # centimeters -> inches
        IN_TO_CM = 2.54              # inches -> centimeters
        CM_TO_M = 0.01               # centimeters -> meters
        M_TO_CM = 100.0              # meters -> centimeters
        FT_TO_IN = 12.0              # feet -> inches
        IN_TO_FT = 0.08333333333     # inches -> feet
        M_TO_FT = 3.280839895        # meters -> feet
        FT_TO_M = 0.3048             # feet -> meters
        M_TO_KM = 0.001              # meters -> kilometers
        KM_TO_MI = 0.62137119223733  # kilometers -> miles
        MI_TO_KM = 1.609344          # miles -> kilometers
        NM_TO_MI = 1.150779448       # nautical miles -> miles
        MI_TO_NM = 0.868976242       # miles -> nautical miles
        NM_TO_KM = 1.852             # nautical miles -> kilometers
        KM_TO_NM = 0.539956803       # kilometers -> nautical miles
        # distance - saskan/metric
        CM_TO_NOB = 0.64             # centimeters -> nobs
        MM_TO_NOB = 0.0064           # millimeters -> nobs
        IN_TO_NOB = 2.56             # inches -> nobs
        NOB_TO_IN = 0.390625         # nobs -> inches
        NOB_TO_MM = 156.25           # nobs -> millimeters
        NOB_TO_CM = 1.5625           # nobs -> centimeters
        TWA_TO_M = 1.00              # twas -> meters
        M_TO_NOB = 64.0              # meters -> nobs
        TWA_TO_NOB = 64.0            # twas -> nobs
        THWAB_TO_TWA = 64.0          # thwabs -> twas
        TWA_TO_THWAB = 0.015625      # twas -> thwabs (1/64th)
        THWAB_TO_M = 64.0            # thwabs -> meters
        M_TO_THWAB = 0.015625        # meters -> thwabs (1/64th)
        KATA_TO_THWAB = 4.0          # kata -> thwabs
        THWAB_TO_KATA = 0.25         # thwabs -> kata
        KATA_TO_M = 256.0            # kata -> meters
        KATA_TO_KM = 0.256           # kata -> kilometers
        KATA_TO_MI = 0.159           # ktaa -> miles
        GAWO_TO_KATA = 4.0           # gawos -> kata
        GAWO_TO_M = 1024.0           # gawos -> meters
        GAWO_TO_KM = 1.024           # gawos -> kilometers
        GABO_TO_MI = 0.636           # gabos -> miles
        YUZA_TO_GABO = 4.0           # yuzas -> gabos
        YUZA_TO_M = 4096.0           # yuzas -> meters
        YUZA_TO_KM = 4.096           # yuzas -> kilometers
        YUZA_TO_MI = 2.545           # yuzas -> miles
        # distance, geographical to metric
        DG_LAT_TO_KM = 111.2           # degree of latitutde -> kilometers
        KM_TO_DG_LAT = 0.00898315284   # kilometers -> degree of latitude
        DG_LONG_TO_KM = 111.32         # degree of longitude -> kilometers
        KM_TO_DG_LONG = 0.00898311175  # kilometers -> degree of longitude
        # astronomical units
        AU_TO_KM = 149597870.7        # astronomical units -> km
        KM_TO_AU = 0.000006684587122  # kilometers -> astro units
        LY_TO_AU = 63241.0771         # light years -> astro units
        AU_TO_LY = 0.00001581250799   # astro units -> light years
        LS_TO_AU = 499.004783676      # light seconds -> astro units
        AU_TO_LS = 0.002004004004     # astro units -> light seconds
        LM_TO_AU = 0.00000000000002   # light minutes -> astro units
        AU_TO_LM = 52596000000000000  # astro units -> light minutes
        LS_TO_LM = 0.000000000000105  # light seconds -> light minutes
        LM_TO_LS = 9460730472580800   # light minutes -> light seconds
        LY_TO_LM = 52596000000000000  # light years -> light minutes
        LM_TO_LY = 0.000000000000019  # light minutes -> light years
        PC_TO_LY = 0.000000000000000  # parsecs -> light years
        LY_TO_PC = 0.000000000000000  # light years -> parsecs
        KPC_TO_PC = 1000.0            # kiloparsecs -> parsecs
        PC_TO_KPC = 0.001             # parsecs -> kiloparsecs
        KPC_TO_MPC = 1000.0           # kiloparsecs -> megaparsecs
        MPC_TO_KPC = 0.001            # megaparsecs -> kiloparsecs
        GPC_TO_MPC = 1000.0           # gigaparsecs -> megaparsecs
        MPC_TO_GPC = 0.001            # megaparsecs -> gigaparsecs

    @dataclass
    class CAL:
        """Define static compoments of CALENDAR_DB.
        Initialize time dict if one does not yet exist,
        to start a new one, or to wipe current one.

        This class should be immutable.

        Units are as follows unless otherwise noted:
        - distance => kilometers
        - mass => kilograms
        - day => 1 rotation of planet Gavor
        - year => 1 orbit of Gavor around its star, Faton
        - rotation => multiple or fraction of Gavoran days
        - orbit => revolution of Gavor around Faton:
           multiple, fractional Gavoran years

        Objects defined by a container name which references
        parent object type. Then define objects within container.
        For example: planets contained in a star; moons in a planet.
        """
        STARS = {
            "Galactic Center": {
                "Faton": {"diameter": 1.390473e+6,
                          "rotation": 36.0,
                          "type": "G-type main-seq star",
                          "mass": 2.10e30}
                }
            }
        PLANETS = {
            "Faton": {
                "Paulu-Kalur": {"orbit": 92.85},
                "Astra": {"orbit": 232.0},
                "Gavor": {"orbit": 366.33},
                "Petra": {"orbit": 602.0},
                "Kalama": {"orbit": 3920.0},
                "Manzana": {"orbit": 10812.0},
                "Jemlok": {"orbit": 30772.0}
                }
            }
        # Add a bunch more moons
        MOONS = {
            "Gavor": {
                "Endor": {"orbit": 32.1,
                          "mass": 1.00346e23},
                "Sella": {"orbit": 23.5,
                          "mass": 0.53779e23}}}
        PARTS = {
            # 24 hours = a day
            # 288 wayts = a day
            "day": {"time": {
                "midnight": 0.0,
                "sunrise": 0.25,
                "noon": 0.5,
                "sunset": 0.75},
                    "duration": {
                        "hour": 0.041666666666666664,
                        "wayt": 0.003472222222222222}},
            # 12 wayts = 1 hour
            # 648 ticks = 1 hour
            "hour": {"time": {"half": 0.5},
                     "duration": {"watch": 4.0,
                                  "wayt": 0.8333333333333334,
                                  "tick": 0.0555555555549995}}}
        SEASON = {
            "days": 91.75,
            "winter": {
                "rel": {"forward": 0, "reverse": 0},
                "events": [{"day": 1, "name": "solstice"},
                           {"day": 45.75, "name": "midwinter"}]},
            "spring": {
                "rel": {"forward": 1, "reverse": 3},
                "events": [{"day": 1, "name": "equinox"}]},
            "summer": {
                "rel": {"forward": 2, "reverse": 2},
                "events": [{"day": 1, "name": "solstice"},
                           {"day": 45.75, "name": "midsummer"}]},
            "autumn": {
                "rel": {"forward": 3, "reverse": 1},
                "events": [{"day": 1, "name": "equinox"}]}}
        CALENDAR = {
            "AG": {"name": "Astro-Gavorian",
                   "type": ["solar", "arithmetic"],
                   "desc": "Year count begins with an " +
                           "estimate of when life " +
                           "began on Gavor. Used only by " +
                           "space-faring characters.",
                   "day": {"start": "midnight"},
                   "months": None,
                   "year": {"start": {
                       "season": "winter",
                       "event": "solstice"},
                            "days": 366,
                            "zero": 4396234934},
                   "leap": {"period": 3,
                            "days": 1,
                            "rule": ["add_to_year_end"]}},
            "SAG": {"name": "Short Astro-Gavorian",
                    "type": ["solar", "arithmetic"],
                    "desc": "Year count is AG minus 4396230000. " +
                            "Rosetta stone calendar. All " +
                            "dates relative to this. " +
                            "Used by Agency on Gavor.",
                    "day": {"start": "midnight"},
                    "months": None,
                    "year": {"start": {
                        "season": "winter",
                        "event": "solstice"},
                            "days": 366,
                            "zero": 4934},
                    "leap": {"period": 3,
                             "days": 1,
                             "rule": ["add_to_year_end"]}},
            "Juuj": {"name": "Juujian",
                     "type": ["solar", "arithmetic"],
                     "desc": "Oldest Helioptic calendar",
                     "day": {"start": "noon"},
                     "months": {"days": [
                         6, 30, 30, 30, 30, 30, 30, 30,
                         30, 30, 30, 30, 30]},
                     "year": {"start": {
                                "season": "summer",
                                "event": "solstice"},
                              "days": 366,
                              "zero": 0},
                     "leap": {"period": 9,
                              "days": 3,
                              "rule": [
                                  "insert_month", 0]}},
            "Beshq": {"name": "Beshquoise",
                      "type": ["solar", "arithmetic"],
                      "desc": "Reformed Helioptic calendar",
                      "day": {"start": "noon"},
                      "months": {"days": [
                          6, 30, 30, 30, 30, 30, 30, 30,
                          30, 30, 30, 30, 30]},
                      "year": {"start": {
                          "season": "summer",
                          "event": "solstice"},
                            "days": 366,
                            "zero": 1},
                      "leap": {"period": 3,
                               "days": 1,
                               "rule": [
                                  "extend_month", 1]}},
            "Bye": {"name": "Byenungik",
                    "type": ["solar", "arithmetic"],
                    "desc": "Traditional Bynenungik " +
                            "calendar",
                    "day": {"start": "noon"},
                    "months": {"days": [
                        30, 31, 30, 31, 30, 31,
                        30, 31, 30, 31, 30, 31]},
                    "year": {"start": {
                        "season": "summer",
                        "event": "solstice"},
                            "days": 366,
                            "zero": 0},
                    "leap": {"period": 3,
                             "days": 1,
                             "rule": [
                                 "extend_month", 12]}},
            "Nye": {"name": "Nyelik",
                    "type": ["solar", "arithmetic"],
                    "desc": "Traditional Nyelik " +
                            "calendar, reflecting belief " +
                            "that Nyeliks were the first " +
                            "people to settle the Saskan " +
                            "Lands.",
                    "day": {"start": "noon"},
                    "months": {"days": [
                        28, 28, 28, 28, 28, 28,
                        28, 28, 28, 28, 28, 28, 30]},
                    "year": {"start": {
                        "season": "spring",
                        "event": "equinox"},
                            "days": 366,
                            "zero": 212},
                    "leap": {"period": 3,
                             "days": 1,
                             "rule": [
                                 "extend_month", 2]}},
            "Mobal": {"name": "Mobalbeqan",
                      "type": ["solar", "arithmetic"],
                      "desc": "Traditional Mobalbeqan " +
                              "calendar, reflecting belief " +
                              "that Mobalbeshqi were first " +
                              "people to settle the Saskan " +
                              "Lands.",
                      "day": {"start": "noon"},
                      "months": {"days": [
                          29, 29, 29, 6, 29, 29, 29, 6,
                          29, 29, 29, 6, 29, 29, 29]},
                      "year": {"start": {
                                "season": "spring",
                                "event": "equinox"},
                               "days": 366,
                               "zero": 576},
                      "leap": {"period": 3,
                               "days": 1,
                               "rule": [
                                   "extend_month", 7]}},
            "Settan": {"name": "Settan",
                       "type": ["lunar", "astronomical"],
                       "desc": "Traditional Settan " +
                               "calendar, reflecting belief " +
                               "that Setta arrived long ago.",
                       "day": {"start": "sunset"},
                       "months": {"days": [
                           23, 32, 23, 32, 24, 32, 23, 32,
                           24, 32, 23, 32, 24, 32, 24, 20,
                           32, 24, 32, 24, 32, 24, 32, 20,
                           23, 32, 24, 23]},
                       "year": {"start": {
                           "event": "full",
                           "moons": ["Endor", "Sella"]},
                            "days": 754,
                            "zero": 166399},
                       "leap": {"period": 3,
                                "days": 1,
                                "rule": [
                                    "extend_month", 1]}},
            "Ter": {"name": "Terrapin",
                    "type": ["solar", "arithmetic"],
                    "desc": "Traditional Terrapin " +
                            "calendar, reflecting belief " +
                            "that Terrapins arrived long ago.",
                    "day": {"start": "sunrise"},
                    "months": {"days": [
                        26, 26, 26, 26, 26, 26, 26, 26,
                        26, 26, 26, 26, 26, 26, 26, 26,
                        26, 26, 26, 26, 26, 26, 26, 26,
                        26, 26, 26, 26, 26, 26, 26, 26,
                        26, 26, 26, 26, 26, 26, 26, 26,
                        26, 26, 26]},
                    "year": {"start": {
                        "season": "spring",
                        "event": "equinox"},
                            "days": 1092,
                            "zero": 360000},
                    "leap": {"period": 3,
                             "days": 1,
                             "rule": [
                                 "extend_month", 7]}},
            "Jack": {"name": "Jackalope",
                     "type": ["arithmetic"],
                     "desc": "Jackalope calendar does not " +
                             "count years sequentially. " +
                             "Instead, it defines an age and " +
                             "counts years within the age.",
                     "day": {"start": "sunrise"},
                     "months": {"days": [
                         32, 32, 32, 32, 32,
                         32, 32, 32, 32, 33]},
                     "year": {"start": {"day": 1},
                              "days": 321,
                              "zero": [1, "Age of Dust"]},
                     "leap": None},
            "K'kol": {"name": "Kahilakol",
                      "type": ["solar", "arithmetic"],
                      "desc": "Kahilakol calendar starts at " +
                              "estimated arrival of Kahila " +
                              "folk in Saskan Lands.",
                      "day": {"start": "midnight"},
                      "months": {"days": [
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29]},
                      "year": {"start": {"day": 1},
                               "days": 754,
                               "zero": -801},
                      "leap": None},
            "K'beq": {"name": "Kahilabeq",
                      "type": ["solar", "arithmetic"],
                      "desc": "Kahilabeq calendar starts at " +
                              "estimated arrival of Kahila " +
                              "folk in Saskan Lands.",
                      "day": {"start": "midnight"},
                      "months": {"days": [
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29, 29, 29,
                          29, 29, 29, 29, 29]},
                      "year": {"start": {"day": 1},
                               "days": 754,
                               "zero": -826},
                      "leap": None},
            "Empa": {"name": "Empafarasi",
                     "type": ["stellar", "arithmetic"],
                     "desc": "Empafarasi calendar starts at " +
                             "founding of the House of the " +
                             "Empafarasi.",
                     "day": {"start": "midnight"},
                     "months": {"days": [
                         29, 29, 29, 29,
                         29, 29, 29, 29]},
                     "year": {"start": {
                         "event": "congruence",
                         "planets": ["Gavor", "Astra"]},
                            "days": 232,
                            "zero": -2862},
                     "leap": None}}

    @dataclass
    class M():
        """Map dimensions
        """
        km_per_grid: float = 43.75
        dg_per_grid_NS: float = 0.393
        dg_per_grid_WE: float = 0.397
        dg_north_edge: float = 37.69
        dg_west_edge: float = -106.65

    def get_map_dim(self,
                    p_map_w: float,
                    p_map_h: float,
                    p_map_n_offset: float,
                    p_map_w_offset: float) -> tuple:
        """Return map dimensions.
        This is used to compute dimensions for a rectangular
        map segment contained within a large map grid.
        Use default values to compute km-sq and
        degrees for a the map segment.
        It assumes (for now) that the map segment is
        located in the northern hemisphere and east of
        zero degrees longitude.

        :args:
        - p_map_w (float) - map width in grid squares
        - p_map_h (float) - map height in grid squares
        - p_map_n_offset (float) - map grids from north edge
        - p_map_w_offset (float) - map grids from west edge

        :returns:
        - map_dim (tuple (dict, str)) - map dimensions (dict, json)
        """
        map_dim = {"map": {
            "rect": {
                "e_w_km": p_map_w * self.M.km_per_grid,
                "n_s_km": p_map_h * self.M.km_per_grid},
            "degrees": {
                "n_lat": round(self.M.dg_north_edge -
                               (p_map_n_offset *
                                self.M.dg_per_grid_NS), 3),
                "s_lat": round(self.M.dg_north_edge -
                               (p_map_n_offset *
                                self.M.dg_per_grid_NS) -
                               (p_map_h * self.M.dg_per_grid_NS), 3),
                "w_long": round(self.M.dg_west_edge +
                                (p_map_w_offset * self.M.dg_per_grid_WE), 3),
                "e_long": round(self.M.dg_west_edge +
                                (p_map_w_offset * self.M.dg_per_grid_WE) +
                                (p_map_w * self.M.dg_per_grid_WE), 3)
                }}}
        return (map_dim, json.dumps(map_dim))

    def define_universe(self):
        """Define universe. Drawing on some of the concepts in the old
        'universe.py' module (see ontology_lab), concepts in
        defining the game space include the following. This grand scheme
        for context may be overkill, but it could also be useful for
        when game play expands to include other galaxies, universes, etc..

        - Total Universe (TU): a sphere measured in gigaparsecs, the
          largest possible unit I have defined.
          The diameter of the known universe is about 28.5 gigaparsecs;
          radius is 14.25 gigaparsecs. This will be fairly constant,
          with only minor changes for each generation, and will fluctuate
          as the universe expands.

          Age of the TU is 13.787±0.020 billion years, give or take, with
          only Agency calendars going back more than 4,000 Gavoran years
          or so.

          For unit measurement conversions, see the 'C' dataclass.

          The origin point at the center of the sphere is where this known
          universe began, its big bang point. Or in game terms, where the
          last game universe ended and a new one began.

          It is exapanding in all directions at a rate of 73.3 kilometers
          per second per megaparsec.

          Dark Energy comprisees 68.3% of the universe, Dark Matter 27.4%,
          remaining 4.3% is baryonic matter (stars, planets, life, etc.).

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

         A common measure of mass is the solar mass, which is the mass of
         our Sun, Sol. In the game world, of Fatun. In either case, it
         is unit. The mass of the Sun is 1.9891 x 10^30 kg. But one solar
         mass is 1.0.

        - External Universe (XU): section(s) of TU that is not playable;
          no detailed star systems.  Simulate some forces, movement,
          but not any inhabited systems.

        - Internal Universe (IU): section(s) of TU that is playable;
          should be no larger than a galactic cluster, but preferably
          one galaxy or smaller.

        - Simulated Universe (SU): section(s) of IU where start systems
          and planets are simulated. Preferbly quite small. May eventually
          want to have scaled SU's.

          The SU should be about 1/3 of the way to a galactic core. Any
          closer and destruction by supernovae is likely.  Star systems
          expected to have life-bearing planets should include at least
          two gas giants, not just one, so that they can tug on each other
          and prevent the rocky planets from being sucked into the sun
          along with the gas giant.

          The sun should be relatively small but large enough to warm
          the inner planets.  The sun should be a yellow dwarf, not a
          red dwarf, so that it can support life.
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

    def define_second(self):
        """
        cesium-133 which vibrates exactly 9,192,631,770 times per second.
        That is a meausrement of frequency which could be reproduced
        anywhere in the universe. But it is still culturally-bound in
        that the second itself is derived from the planet Earth's
        relationship to it Sun.

        Time dilation is a phenomenon that occurs when a reference
        frame is moving relative to another reference frame. In the
        case of very fast travel, especially near the speed of light,
        time itself will slow down for the traveler. Also, space-time
        is curved in gravity wells like solar systems.

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
        """
        pass

    def set_file_name(self,
                      p_db_nm: str):
        """Return full name of calendar DB file.
        For now, store it in shared memory.
        Later, persist it to Redis.
        """
        file_nm = "/dev/shm" + p_db_nm + "_calendar.pickle"
        return file_nm

    def get_time_db(self,
                    p_db_nm: str):
        """Retrieve the calendar database

        :args: p_db_nm (str) - generic file name
        """
        try:
            with open(self.set_file_name(p_db_nm), 'rb') as f:
                self.CAL_DB = pickle.load(f)
            pp(self.CAL_DB)
        except FileNotFoundError:
            print("No calendar database found.")

    def set_time_db(self,
                    p_db_nm: str):
        """Store the calendar database.
        :args: p_db_nm (str) - generic file name
        :write:
        - _calendar.pickle file
        """
        try:
            with open(self.set_file_name(p_db_nm), 'wb') as f:
                pickle.dump(self.CAL_DB, f)
            print("Calendar database saved.")
        except Exception as e:
            print("Error writing calendar database. " + str(e))

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

    def year_zero(self,
                  p_cal_nm: str):
        """Provide starting point for time calculations.
        Based on the calendar type, the starting point is
        adjusted for season (year start) and time (day start),
        relative to the SAG starting point.

        The point of this method is to provide a common
        starting point when computing dates and times. May
        also want to have a "calendar" that is simply day count
        since day zero/year zero.

        :args: p_cal_nm (str): name of calendar

        :return: dict = year zero date according to calendar
        """
        sag_start = {
            "season":
                self.S_CAL["SAG"]["year"]["start"]["season"],
            "event":
                self.S_CAL["SAG"]["year"]["start"]["event"],
            "day": 1,
            "time": self.S_CAL["SAG"]["day"]["start"]
        }
        cal_start = {
            "year": self.S_CAL[p_cal_nm]["year"]["zero"],
            "month_count": None,
            "day_count": None,
            "month_day": None,
            "season": None
        }
        # If a start season is defined, adjust the start date
        # (day number) as offset to winter solstice, season #4.
        # The CAL SEASONS object's "reverse" attribute tells
        # how many seasons before Winter that season is.

        # Solar calendars should always have an explicit start day.
        # Lunar and Stellar calendars are based on conjuctions.
        # In game world, the era started with full conjuctions, so
        # they always start on day #1 of the year.
        cal_y_start = self.S_CAL[p_cal_nm]["year"]["start"]
        if "season" in cal_y_start:
            cal_start["season"] = cal_y_start["season"]
            days_before_winter =\
                self.S_SEASON[cal_start["season"]]["rel"]["reverse"] *\
                self.S_SEASON["days"]
            cal_start["day_count"] = int(round(sag_start["day"] +
                                         days_before_winter))
        elif "event" in cal_y_start and cal_y_start["event"] == "full":
            cal_start["day_count"] = 1
        elif "event" in cal_y_start and cal_y_start["event"] == "congruence":
            cal_start["day_count"] = 1
        elif "day" in cal_y_start and cal_y_start["day"] is not None:
            cal_start["day_count"] = cal_y_start["day"]
        else:
            print("No explicit start day found....")
            pp(self.S_CAL[p_cal_nm])
        # Set the season to match the SAG calendar.
        cal_start["season"] = sag_start["season"]
        # Non-SQG day-starts occur AFTER SAG day start time of midnight.
        # So.. no need to adjust day count based on day-start time.
        # Determine if start year is a leap year. Leap year rules:
        # - add_to_year_end
        # - insert_month, @month_index
        # - extend_month, @month_index <-- this is the only one relevant.
        #   Other two are not affected by year-zero algo.
        cal_months = self.S_CAL[p_cal_nm]["months"]
        cal_leap = self.S_CAL[p_cal_nm]["leap"]
        extend_month = None
        if cal_months is not None:
            if cal_leap is not None and cal_start["year"] > 1 and\
                    cal_start["year"] % cal_leap["period"] == 0:
                extend_month = cal_leap["rule"][1]
                cal_months["days"][extend_month - 1] += cal_leap["days"]
            cal_start["month_count"] = 1
            # If the calendar uses months, compute the start
            # month and day of the month.
            day_count = cal_start["day_count"]
            for m_days in cal_months["days"]:
                if day_count > m_days:
                    day_count -= m_days
                    cal_start["month_count"] += 1
                else:
                    cal_start["month_day"] = day_count
                    break

        return (self.S_CAL[p_cal_nm]["name"], cal_start)

    def get_day_part(self,
                     p_day_t):
        """Determine if time/day clock starts before or after noon, etc.

        :args: p_day_t (float): time of day, as decimal portion of day
        """
        day_part = None
        for part in ["midnight", "sunrise", "noon", "sunset"]:
            if p_day_t >= self.CAL.PARTS["day"]["time"][part]:
                day_part = part
        return day_part

    def get_day_hour(self,
                     p_cal_nm: str,
                     p_day_t):
        """Convert hour of the day, for specified calendar, with
        respect to "standard" day start time of Midnight.

        :args:
        - p_cal_nm (str): index to static calender data
        - p_day_t (float): time of day, as decimal portion of day
        """
        # For day starting at midnight:
        hour = int(p_day_t / self.CAL.PARTS["day"]["duration"]["hour"])
        day_start = self.S_CAL[p_cal_nm]["day"]["start"]
        if day_start == "sunrise":
            hour -= 6
        elif day_start == "noon":
            hour -= 12
        elif day_start == "sunset":
            hour -= 18
        return hour

    def get_day_watch(self,
                      p_day_h: int):
        """Determine the watch and wayt for specified calendar-hour.
        Work on other conversions. Everything should be relative to
        "standard" clock parts.

        Needs work. See notes on hours, wayts and watches.
        Consider providing variations between calendars.
        Adjust at minimum for day-start times.

        :args:
        - p_cal_nm (str): index to static calender data
        - p_day_h (int): hour of the day, calendar-specific
        """
        watch = int(p_day_h / self.CAL.PARTS["hour"]["duration"]["watch"]
                    + 1)
        return watch

    def get_date_time(self,
                      p_day_n,
                      p_roll_n=0.0):
        """Compute the date from the day number.
        If only day num provided, return that date.
        If roll number, then return day num plus roll num date.
        Use negative roll number to roll backwards.
        Fractions of days expressed as decimals in the arguments,
        returned as watches, hours, wayts and ticks.
        Count SAG day zero at midnight as day number 0.

        Results are saved in a dictionary, keyed by SAG day number.

        Needs work. Things to consider:
        - Having a "calendar" that is simply day-count from Day Zero.
        - OR.. adjust the SAG to be this.
        - Define what I mean by "roll number".
        - That should work forward and backward.
        - Ideally, input terms from any calendar, convert to standard,
          then convert to target(s) or to all.

        :args:
        - p_day_n (float): day number
        - p_roll_n (float): roll number - optional
        :return: date (str) = date and time in format for each cal

            "SAG": {"name": "Short Astro-Gavorian",
                    "type": "[solar, arithmetic]",
                    "desc": "Year count is AG minus " +
                            "4396230000. This is the " +
                            "rosetta stone calendar. Compute " +
                            "all dates relative to this one. " +
                            "Used by the Agency on Gavor.",
                    "day": {"start": "midnight"},
                    "months": None,
                    "year": {"start": {
                        "season": "winter",
                        "event": "solstice"},
                            "days": 366,
                            "zero": 4934},
                    "leap": {"period": 3,
                             "days": 1,
                             "rule": ["add_to_year_end"]}},

        PARTS = {
            # 24 hours = a day
            # 288 wayts = a day
            "day": {"time": {
                "midnight": 0.0, "sunrise": 0.25,
                "noon": 0.5, "sunset": 0.75},
                    "duration": {
                        "hour": 0.041666666666666664,
                        "wayt": 0.003472222222222222}},
            # 12 wayts = 1 hour
            # 648 ticks = 1 hour
            "hour": {"time": {"half": 0.5},
                     "duration": {"watch": 4.0,
                                  "wayt":
                                      0.8333333333333334,
                                  "tick":
                                      0.0555555555549995}}}
        """
        if p_day_n not in self.CAL_DB:
            sag_year = int((p_day_n / 366.33) +
                           self.S_CAL["SAG"]["year"]["zero"])
            self.CAL_DB[p_day_n] = dict()
            for cal_nm in self.S_CAL.keys():
                day_time = p_day_n % 1
                day_part = self.get_day_part(day_time)
                day_hour = self.get_day_hour(cal_nm, day_time)
                day_watch = self.get_day_watch(day_hour)
                self.CAL_DB[p_day_n][cal_nm] = {
                    "sag_year": sag_year,
                    "day_time": day_time,
                    "day_part": day_part,
                    "day_hour": day_hour,
                    "day_watch": day_watch}

        if p_roll_n != 0.0:
            # compute roll_day cals and add to CAL_DB
            roll_day = p_day_n + p_roll_n
            if roll_day not in self.CAL_DB:
                pass

        return self.CAL_DB[p_day_n]
