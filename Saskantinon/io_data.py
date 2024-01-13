"""

:module:    io_data.py
:author:    GM (genuinemerit @ pm.me)

Saskan Data Management middleware.

Provides data mgmt methods for Saskan game app DB and files, 
a middleware layer between GUI and data sources. The more primitive
methods reside in io_db.py and io_file.py. This module is intended
to provide a higher level of abstraction, and to be used by the
GUI layer, saskan_game.py. It is also intended to be used from
the command line, for example, to load data from CSV files.

Along with wrapper calls to io_db and io_file, this module also
defines types and data structures for the game app.

See saskan_math and io_astro. Both could use this module to
set up records and types. It might even make sense to merge
the three modules into one, but want to avoid creating huge
monster modules.

# Reminder that drawing canvas is 2D and not intending to
#  represent a 3D space. So, the "z" coordinate is not really
#  used for drawing. But keep it in the data model
#  to help with modeling and calculations.

:related:
- io_db.py - database access layer
- io_file.py - file system access layer
- io_shell.py - shell access layer
- saskan_math.py - math and geometry functions
- saskan_game.py - game app, GUI layer

:classes:
- SetGameData - methods for inserting and updating values on SASKAN.db
- GetGameData - methods for getting values from SASKAN.db
"""

import pygame as pg
from copy import copy
from pprint import pprint as pp     # noqa: F401, format like pp for files
from pprint import pformat as pf    # noqa: F401, format like pp for files
from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from io_db import DataBase
from io_file import FileIO
from io_shell import ShellIO

DB = DataBase()
FI = FileIO()
SI = ShellIO()

pg.init()                   # Initialize PyGame for use in this module

pydantic_config = ConfigDict(arbitrary_types_allowed = True,
                             from_attributes = True,
                             populate_by_name = True,
                             str_strip_whitespace = True,
                             use_enum_values = True,
                             validate_assignment = True,
                             validate_default = True)

@dataclass(order=True, frozen=True, slots=True, config=pydantic_config)
class Astro():
    """ Astronomical and physics units and conversions.
    """
    # galaxy names
    GADJ = ["Brilliant", "Lustrous", "Twinkling",
           "Silvery", "Argent", "Glistening"]
    GITM = ["Way", "Trail", "Cloud", "Wave", "Skyway"]
    GNAM = ["Galaxy", "Cluster", "Nebula", "Spiral",
            "Starfield",  "Cosmos", "Nebula",
            "Megacosm", "Space"]
    # mass, matter
    DE = "dark energy"
    DM = "dark matter"
    BM = "baryonic matter"
    SMS = "solar mass"
    # objects, astronomical
    BH = "black hole"
    GB = "galactic bulge"
    GC = "galactic cluster"
    GH = "galactic halo"
    GX = "galaxy"
    IG = "interstellar matter"
    SC = "star cluster"
    TP = "timing pulsar"            # saskan
    TU = "total universe"           # saskan
    XU = "external universe"        # saskan
    # time-related, real world and saskan
    GS = "galactic second"          # 'galactic' second; saskan
    GMS = "galactic millisecond"    # 'galactic' millisecond; saskan
    PMS = "pulses per millisecond"  # 'galactic' second as # of pulses
    ET = "elapsed time"             # age, duration, time passed
    GY = "gavoran year"             # saskan
    # rates, speeds, velocities
    ER = "expansion rate"              # of a volume
    UER = "universal expansion rate"
    KSM = "km/s per Mpc"               # km/s per Mpc
    PRO = "period of rotation"
    PRV = "period of revolution"
    PR = "pulse rate"
    # distance
    AU = "astronomical unit"     # distance from Fatune to Gavor
    GLY = "gigalight year"
    GPC = "gigaparsec"
    KPC = "kiloparsec"
    LM = "light minute"
    LS = "light second"
    LY = "light year"
    MPC = "megaparsec"
    PC = "parsec"
    # area, volume
    GLY2 = "square gigalight year"
    GLY3 = "cubic gigalight year"
    GPC2 = "square gigaparsec"
    GPC3 = "cubic gigaparsec"
    PC2 = "square parsec"
    PC3 = "cubic parsec"
    LY2 = "square light year"
    LY3 = "cubic light year"
    # constants
    DEP = 0.683              # dark energy percentage
    DMP = 0.274              # dark matter percentage
    BMP = 0.043              # baryonic matter percentage
    TUV = 415000             # total univ volume in cubic gigalight years
    TUK = 1.5e53             # total universe mass in kg
    UNA = 13.787e9           # age of universe in Gavoran years (turns)
    TUE = 73.3               # expansion rate of universe in km/s per Mpc
    # conversions -- all are multiplicative in the indicated direction
    # For `AA_TO_BB`, BB = AA * value
    # Example: `AU_TO_KM` means `KM = AU * 1.495979e+8`
    AU_TO_KM = 1.495979e+8        # astronomical units -> km
    AU_TO_LM = 5.2596e+16         # astro units -> light minutes
    AU_TO_LS = 0.002004004004     # astro units -> light seconds
    AU_TO_LY = 0.00001581250799   # astro units -> light years
    GLY_TO_LY = 1e+9              # gigalight years -> light years
    GPC_TO_GLY = 3.09             # gigaparsecs -> gigalight years
    GPC_TO_MPC = 1000.0           # gigaparsecs -> megaparsecs
    KM_TO_AU = 0.000006684587122  # kilometers -> astro units
    KPC_TO_MPC = 1000.0           # kiloparsecs -> megaparsecs
    KPC_TO_PC = 1000.0            # kiloparsecs -> parsecs
    LM_TO_AU = 0.00000000000002   # light minutes -> astro units
    LM_TO_LS = 9460730472580800   # light minutes -> light seconds
    LM_TO_LY = 0.000000000000019  # light minutes -> light years
    LS_TO_AU = 499.004783676      # light seconds -> astro units
    LS_TO_LM = 0.000000000000105  # light seconds -> light minutes
    LY_TO_AU = 63240.87           # light years -> astro units
    LY_TO_GLY = 1e-9              # light years -> gigalight years
    LY_TO_LM = 52596000000000000  # light years -> light minutes
    LY_TO_PC = 0.30659817672196   # light years -> parsecs
    MPC_TO_GPC = 0.001            # megaparsecs -> gigaparsecs
    MPC_TO_KPC = 1000.0           # megaparsecs -> kiloparsecs
    GLY_TO_PC = 3.262e6           # gigalight years -> parsecs
    PC_TO_GLY = 3.065603923973023e-07       # parsecs -> gigalight years
    PC_TO_KPC = 0.001             # parsecs -> kiloparsecs
    PC_TO_LY = 3.261598           # parsecs -> light years


@dataclass(order=True, frozen=True, slots=True, config=pydantic_config)
class Colors():
    """Define immutable constants.
    """
    # CLI Colors and accents
    CL_BLUE = '\033[94m'
    CL_BOLD = '\033[1m'
    CL_CYAN = '\033[96m'
    CL_DARKCYAN = '\033[36m'
    CL_END = '\033[0m'
    CL_GREEN = '\033[92m'
    CL_PURPLE = '\033[95m'
    CL_RED = '\033[91m'
    CL_YELLOW = '\033[93m'
    CL_UNDERLINE = '\033[4m'
    
    # PyGame Colors
    CP_BLACK = pg.Color(0, 0, 0)
    CP_BLUE = pg.Color(0, 0, 255)
    CP_BLUEPOWDER = pg.Color(176, 224, 230)
    CP_GRAY = pg.Color(80,80,80)
    CP_GRAY_DARK = pg.Color(20, 20, 20)
    CP_GREEN = pg.Color(0, 255, 0)
    CP_PALEPINK = pg.Color(215, 198, 198)
    CP_RED = pg.Color(255, 0, 0)
    CP_SILVER = pg.Color(192, 192, 192)
    CP_WHITE = pg.Color(255, 255, 255)


@dataclass(order=True, frozen=True, slots=True, config=pydantic_config)
class Geog():
    """Values used to do various computations using
    a variety of units and formulae for measures of
    distance at a human/planetary geographical scale.
    """
    # distance
    CM = "centimeters"
    FT = "feet"
    GA = "gawos"        # saskan
    IN = "inches"
    KA = "katas"        # saskan
    KM = "kilometers"
    M = "meters"
    MI = "miles"
    MM = "millimeters"
    NM = "nautical miles"
    NOB = "nobs"        # saskan
    THWAB = "thwabs"    # saskan
    TWA = "twas"        # saskan
    YUZA = "yuzas"      # saskan
    # area, volume
    M2 = "square meters"
    M3 = "cubic meters"
    # distance, geographical
    DGLAT = "degrees latitude"
    DGLONG = "degrees longitude"
    # direction, geographical
    LOC = "location"
    N = "north"
    E = "east"
    S = "south"
    W = "west"
    NE = "northeast"
    SE = "southeast"
    SW = "southwest"
    NW = "northwest"
    NS = "north-south"
    EW = "east-west"
    # conversions - metric/imperial
    CM_TO_IN = 0.3937007874      # centimeters -> inches
    CM_TO_M = 0.01               # centimeters -> meters
    CM_TO_MM = 10.0              # centimeters -> millimeters
    FT_TO_IN = 12.0              # feet -> inches
    FT_TO_M = 0.3048             # feet -> meters
    IN_TO_CM = 2.54              # inches -> centimeters
    IN_TO_FT = 0.08333333333     # inches -> feet
    IN_TO_MM = 25.4              # inches -> millimeters
    KM_TO_M = 1000.0             # kilometers -> meters
    KM_TO_MI = 0.62137119223733  # kilometers -> miles
    KM_TO_NM = 0.539956803       # kilometers -> nautical miles
    M_TO_CM = 100.0              # meters -> centimeters
    M_TO_FT = 3.280839895        # meters -> feet
    M_TO_KM = 0.001              # meters -> kilometers
    M_TO_KM = 0.001              # meters -> kilometers
    MI_TO_KM = 1.609344          # miles -> kilometers
    MI_TO_NM = 0.868976242       # miles -> nautical miles
    MM_TO_CM = 0.1               # millimeters -> centimeters
    MM_TO_IN = 0.03937007874     # millimeters -> inches
    NM_TO_KM = 1.852             # nautical miles -> kilometers
    NM_TO_MI = 1.150779448       # nautical miles -> miles
    # conversions - saskan/metric
    CM_TO_NOB = 0.64             # centimeters -> nobs
    GABO_TO_MI = 0.636           # gabos -> miles
    GAWO_TO_KATA = 4.0           # gawos -> kata
    GAWO_TO_KM = 1.024           # gawos -> kilometers
    GAWO_TO_M = 1024.0           # gawos -> meters
    IN_TO_NOB = 2.56             # inches -> nobs
    KATA_TO_KM = 0.256           # kata -> kilometers
    KATA_TO_M = 256.0            # kata -> meters
    KATA_TO_MI = 0.159           # ktaa -> miles
    KATA_TO_THWAB = 4.0          # kata -> thwabs
    M_TO_NOB = 64.0              # meters -> nobs
    M_TO_THWAB = 0.015625        # meters -> thwabs (1/64th)
    MM_TO_NOB = 0.0064           # millimeters -> nobs
    NOB_TO_CM = 1.5625           # nobs -> centimeters
    NOB_TO_IN = 0.390625         # nobs -> inches
    NOB_TO_MM = 156.25           # nobs -> millimeters
    THWAB_TO_KATA = 0.25         # thwabs -> kata
    THWAB_TO_M = 64.0            # thwabs -> meters
    THWAB_TO_TWA = 64.0          # thwabs -> twas
    TWA_TO_M = 1.00              # twas -> meters
    TWA_TO_NOB = 64.0            # twas -> nobs
    TWA_TO_THWAB = 0.015625      # twas -> thwabs (1/64th)
    YUZA_TO_GABO = 4.0           # yuzas -> gabos
    YUZA_TO_KM = 4.096           # yuzas -> kilometers
    YUZA_TO_M = 4096.0           # yuzas -> meters
    YUZA_TO_MI = 2.545           # yuzas -> miles
    # conversions, geographical to metric
    DGLAT_TO_KM = 111.2           # degree of latitutde -> kilometers
    DGLONG_TO_KM = 111.32         # degree of longitude -> kilometers
    KM_TO_DGLAT = 0.00898315284   # kilometers -> degree of latitude
    KM_TO_DGLONG = 0.00898311175  # kilometers -> degree of longitude


@dataclass(order=True, frozen=True, slots=True, config=pydantic_config)
class Geom:
    """Types of measurements or objects assigned to a
    meaningful abbreviations and names in English,
    relating generically to geometry and physics.
    """
    # math, general geometry
    ABC = "(a, b, c)"
    ANG = "angle"
    AR = "area"
    BND = "bounding rectangle"
    CNT = "count"
    CON = "container"
    DC = "decimal"
    DI = "diameter"
    DIM = "dimensions"
    DIR = "direction"
    HT = "height"
    INT = "integer"
    LG = "length"
    PCT = "percent"
    PYR = ("pitch, yaw, roll")
    RD = "radius"
    ROT = "rotation"
    SAX = "semi-axes"
    SZ = "size"
    VE = "vector"
    VL = "volume"
    WD = "width"
    XY = "(x, y)"
    XYZD = "((x,x), (y,y), (z,z))"
    XYZ = "(x, y, z)"
    # geometry shapes
    BX = "pg_rect"
    CI = "circle"
    EL = "ellipsoid"
    RC = "rectangle"
    SH = "sphere"
    SHA = "shape"
    SP = "spiral"
    # weight. mass
    GM = "grams"
    KG = "kilograms"
    LB = "pounds"
    MS = "mass"
    OZ = "ounces"
    # energy
    AMP = "amperes (A)"
    OH = "ohms (Ω)"
    V = "volts (V)"
    WA = "watts (W)"
    # names, labels, qualities
    NM = "name"
    REL = "relative"
    SHP = "shape"


@dataclass(order=True, frozen=True, slots=True, config=pydantic_config)
class TS():
    """'Typesetting' helpers
    Also, some fixed values that will eventually move to DB tables
    or be handled as parameters.
    """
    dash16: str = "----------------"
    # This won't work without initializing pygame.
    info = pg.display.Info()
    WIN_W = round(info.current_w * 0.9)
    WIN_H = round(info.current_h * 0.9)
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    GAMEMAP_X = int(round(WIN_W * 0.01))
    GAMEMAP_Y = int(round(WIN_H * 0.06))
    GAMEMAP_W = int(round(WIN_W * 0.8))
    GAMEMAP_H = int(round(WIN_H * 0.9))
    GRID_OFFSET_X = int(round(GAMEMAP_W * 0.01))
    GRID_OFFSET_Y = int(round(GAMEMAP_H * 0.02))
    GRID_ROWS = 32
    GRID_COLS = 46
    GRID_CELL_PX_W =\
        int(round(GAMEMAP_W - GRID_OFFSET_X) / GRID_COLS)
    GRID_CELL_PX_H =\
        int(round(GAMEMAP_H - GRID_OFFSET_Y) / GRID_ROWS)
    GRID_CELL_KM_W = 33
    GRID_CELL_KM_H =\
        int(round(GRID_CELL_KM_W * (GRID_CELL_PX_H / GRID_CELL_PX_W)))
    G_LNS_PX_W = GRID_CELL_PX_W * GRID_COLS
    G_LNS_PX_H = GRID_CELL_PX_H * GRID_ROWS
    G_LNS_KM_W = GRID_CELL_KM_W * GRID_COLS
    G_LNS_KM_H = GRID_CELL_KM_H * GRID_ROWS


# Pydantic models to define complex attributes or records.
# ========================================================
class ColRowIx(BaseModel):
    model_config = ConfigDict(pydantic_config)
    r: int = 0
    c: int = 0


class WidthHeightPx(BaseModel):
    model_config = ConfigDict(pydantic_config)
    w: float = 0.0
    h: float = 0.0


class CoordXYZ(BaseModel):
    model_config = ConfigDict(pydantic_config)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class CoordXY(BaseModel):
    model_config = ConfigDict(pydantic_config)
    x: float = 0.0
    y: float = 0.0


class CoordRect(BaseModel):
    model_config = ConfigDict(pydantic_config)
    top_left: CoordXY
    top_right: CoordXY
    bottom_left: CoordXY
    bottom_right: CoordXY


class CoordABC(BaseModel):
    model_config = ConfigDict(pydantic_config)
    a: float = 0.0
    b: float = 0.0
    c: float = 0.0


class PitchYawRollAngle(BaseModel):
    model_config = ConfigDict(pydantic_config)
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0


class GameRect(BaseModel):
    model_config = ConfigDict(pydantic_config)
    height_width: WidthHeightPx
    coord_rect: CoordRect
    center: CoordXY
    fill: bool = False
    fill_color: pg.Color = Colors.CP_GREEN
    line_color: pg.Color = Colors.CP_BLACK
    box: pg.Rect = pg.Rect(0, 0, 0, 0)


class Cell(BaseModel):
    model_config = ConfigDict(pydantic_config)
    rc: ColRowIx
    wh: WidthHeightPx
    rect: GameRect


class Grid(BaseModel):
    model_config = ConfigDict(pydantic_config)
    RowsCols: ColRowIx
    cells: dict[str, Cell]


# The following models are used to create SQLITE tables.
# A classmethod identifies SQLITE constraints, datatypes
# like BLOB and JSON, and sort order.
# =======================================================
class Universe(BaseModel):
    model_config = ConfigDict(pydantic_config)
    tablename: str = "UNIVERSE"
    univ_nm_pk: str
    radius_gly: float = 0.0
    volume_gly3: float = 0.0
    volume_pc3: float = 0.0
    elapsed_time_gavyr: float = 0.0
    expansion_rate_kmpsec_per_mpc: float = 0.0
    mass_kg: float = 0.0
    dark_energy_kg: float = 0.0
    dark_matter_kg: float = 0.0
    baryonic_matter_kg: float = 0.0

    @classmethod
    def constraints(cls):
        return {
            "PK": ["univ_nm_pk"],
            "ORDER": ["univ_nm_ix ASC"]
        }



class ExternalUniv(BaseModel):
    model_config = ConfigDict(pydantic_config)
    tablename: str = "EXTERNAL_UNIVERSE"
    external_univ_nm_pk: str
    univ_nm_fk: str
    mass_kg: float
    dark_energy_kg: float
    dark_matter_kg: float
    baryonic_matter_kg: float

    @classmethod
    def constraints(cls):
        return {
            "PK": ["external_univ_nm_pk"],
            "FK": {"univ_nm_fk": ("UNIVERSE", "univ_uid_pk")},
            "ORDER": ["univ_nm_fk ASC",
                      "external_univ_nm_pk ASC"]
        }


class GalacticCluster(BaseModel):
    model_config = ConfigDict(pydantic_config)
    tablename: str = "GALACTIC_CLUSTER"
    galactic_cluster_nm_pk: str
    univ_nm_fk: str = ''
    center_from_univ_center_gly: CoordXYZ
    cluster_shape: str = 'ellipsoid'
    volume_pc3: float = 0.0
    mass_kg: float = 0.0
    dark_energy_kg: float = 0.0
    dark_matter_kg: float = 0.0
    baryonic_matter_kg: float = 0.0
    timing_pulsar_pulse_per_ms: float = 0.0
    timing_pulsar_loc_gly: CoordXYZ
    shape_pc: CoordXYZ
    shape_axes: CoordABC
    shape_rot: PitchYawRollAngle
    boundary_gly: GameRect

    @classmethod
    def constraints(cls):
        return {
            "PK": ["galactic_cluster_nm_pk"],
            "FK": {"univ_uid_fk": ("UNIVERSE", "univ_uid_pk")},
            "CK": {"cluster_shape": ['ellipsoid', 'spherical']},
            "DT": {},
            "GROUP": {"center_from_univ_center_gly": CoordXYZ,
                      "timing_pulsar_loc_gly": CoordXYZ,
                      "shape_pc": CoordXYZ,
                      "shape_axes": CoordABC,
                      "shape_rot": PitchYawRollAngle,
                      "boundary_gly": GameRect},
            "ORDER": ["univ_nm_fk ASC",
                      "galactic_cluster_nm_pk ASC"]
        }

class Galaxy(BaseModel):
    model_config = ConfigDict(pydantic_config)
    tablename: str = "GALAXY"
    galaxy_nm_pk: str
    galactic_cluster_nm_fk: str = ''
    relative_size: str = 'medium'
    center_from_univ_center_kpc: CoordXYZ
    halo_radius_pc: float = 0.0
    boundary_pc: GameRect
    volume_gpc3: float = 0.0
    mass_kg: float = 0.0
    bulge_shape: str = 'ellipsoid'
    bulge_dim_from_center_ly: CoordXYZ
    bulge_dim_axes: CoordABC
    bulge_black_hole_mass_kg: float = 0.0
    bulge_volume_gpc3: float = 0.0
    bulge_total_mass_kg: float = 0.0
    star_field_shape: str = 'ellipsoid'
    star_field_dim_from_center_ly: CoordXYZ
    star_field_dim_axes: CoordABC
    star_field_vol_gpc3: float = 0.0
    star_field_mass_kg: float = 0.0
    interstellar_mass_kg: float = 0.0

    @classmethod
    def constraints(cls):
        return {
            "PK": ["galaxy_nm_pk"],
            "FK": {"galactic_cluster_nm_fk": ("GALACTIC_CLUSTER", "galactic_cluster_nm_pk")},
            "CK": {"relative_size": ['small', 'medium', 'large'],
                   "bulge_shape": ['ellipsoid', 'spherical'],
                   "star_field_shape": ['ellipsoid', 'spherical']},
            "GROUP": {"center_from_univ_center_kpc": CoordXYZ,
                      "boundary_pc": GameRect,
                      "bulge_dim_from_center_ly": CoordXYZ,
                      "bulge_dim_axes": CoordABC,
                      "star_field_dim_from_center_ly": CoordXYZ,
                      "star_field_dim_axes": CoordABC},
            "ORDER": ["galactic_cluster_nm_pk ASC",
                      "galaxy_nm_pk ASC"]
        }


class World(BaseModel):
    model_config = ConfigDict(pydantic_config)
    tablename: str = "WORLD"
    world_nm_pk: str
    star_system_name_fk: str
    world_type: str = 'Earth-like'
    obliquity_dg: float = 0.0
    distance_from_star_au: float = 0.0
    distance_from_star_km: float = 0.0
    diameter_km: float = 0.0
    mass_kg: float = 0.0
    gravity_m_per_s_per_s: float = 0.0
    orbit_days: float = 0.0
    orbit_turns: float = 0.0
    rotation_days: float = 0.0
    world_desc: str
    atmosphere: str
    biosphere: str
    sentients: str
    climate: str
    tech_level: str
    terrain: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["world_nm_pk"],
            "FK": {"star_system_nm_fk": ("STAR_SYSTEM", "star_system_nm_pk")},
            "CK": {"world_type": ['Earth-like', 'gas giant', 'rocky', 'desert', 'oceanic', 'ice planet', 'molten','other']},
            "ORDER": ["star_system_nm_fk ASC",
                      "world_nm_pk ASC"]
        }

class InitGameDatabase(object):
    """Methods to:
    - Create set of SQL files to manage the game database (saskan.db).
    - Boot the database by running the SQL files.
    """
    pass

    def __init__(self):
        """Initialize the InitGameDatabase object.
        """
        pass

    def create_sql_files(self):
        """Pass pydantic data object to create SQL files.
        """
        for model in [Universe, ExternalUniv,
                      GalacticCluster, Galaxy, World]:
        # for model in [GalacticCluster]:
            DB.generate_sql(model)


class SetGameData(object):
    """Methods for inserting and updating values on SASKAN.db.
    Initially, just use these from the command line. Eventually,
    intergrate them into the GUI when useful. Avoid a rat-hole of
    overwrought GUI features and functionality. A "magical" editor
    that generates forms based on DB table definitions is unlikely
    to be worth the effort. Keep it simple, stupid.  If command line is
    too tiresome, then use a CSV file or JSON file to load data.
    """
    def __init__(self):
        """Initialize the SetGameData object.
        """
        pass

    @classmethod
    def insert_record(cls,
                      p_sql_nm: str,
                      p_values: list,
                      p_object: dict):
        """Insert a record to SASKAN.db.
        Instead of pickling dicts, use Pydantic data structures
         that are cast to JSON. Little gain by pickling blobs.
        Store as utf-8-encoded bytes in a BLOB data type.
        This will also make it easier to do analysis and so on 
        using a DBMS tool like Beekeeper Studio.
        """
        # DB.execute_insert(p_sql_nm, (p_values, pickle.dumps(p_object)))
        pass


class GetGameData(object):
    """Get and set resources displayed in GAMEMAP and CONSOLE.
    This class is instantiated as GDAT, a global object.
    Notes:
    - "txt" refers to a string of text.
    - "img" refers to a PyGame image object rendered from the txt.
    - "box" refers to a PyGame rectangle object around the img.
    @DEV:
    - Layers of data, zoom-in, zoom-out, other views
    - Ee.g.: a region, a town and environs, a village, a scene, star map
    - GUI controls for scroll, zoom, pan, select-move, etc
    - Event trigger conditions / business rules

    Think about abstracting the formatting from the display media.
    In other words, the data structure should be independent of
    what system (GUI) is going to display it. I can construct and
    format blocks of text and images, then pass them to the GUI.
    
    Don't be assigning fonts and sizes to text in this module.
    Do deliver chunks of text in reasonable sizes.
    Leave rendering logic in the GUI module (saskan_game.py)
    """
    def __init__(self):
        """Dynamically loaded data for GAMEMAP and CONSOLE.
        Values are displayed in CONSOLE but refer to GAMEMAP.
        For G_CELL, static values are read in from PG, then
           data is extended here.
        """
        self.DATASRC = {"actv": False,
                        "catg": None,
                        "item": None}
        self.CONSOLE_REC = {"txt": "",
                            "img": None,
                            "box": None}
        self.CONSOLE_TEXT: list = list()
        self.MAP_BOX = None
        self.G_CELLS = dict()

    def make_grid_key(self,
                      p_col : int,
                      p_row: int) -> str:
        """Convert integer coordinates to string key
           for use in the .grid["G"] (grid data) matrix.
        :args:
        - p_col: int, column number
        - p_row: int, row number
        :returns:
        - str, key for specific grid-cell record, in "0n_0n" format
        """
        return f"{str(p_col).zfill(2)}_{str(p_row).zfill(2)}"

    # Data load methods
    # The current version of these methods assumes a
    #   specific pattern of name:value pairs in data sources.
    # =================
    def set_datasrc(self,
                    p_datasrc: dict):
        """ Set data in .DATASRC structure from sources outside
           the app, like files or services or database.
           Example: geographical data
        :args:
        - p_datasrc (dict): name-value pairs for .DATASRC structure.
        :sets:
        - self.DATASRC (dict): name-value pairs
        """
        for k, v in p_datasrc.items():
            self.DATASRC[k] = v

    def set_label_name(self,
                       p_attr: dict):
        """Set text for a label (l) and name (n), but no type (t) value.
           Example: "type" attribute
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [TS.dash16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['name']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)

    def set_label_name_type(self,
                            p_attr: dict):
        """Set text for a label (l), a name (n), and a type (t).
           Example: "contained_by" attribute
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [TS.dash16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['name']}",
                  f"  {p_attr['type']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)

    def set_proper_names(self,
                         p_attr: dict):
        """Set text for a "name" attribute, which refers to proper
            names. Required value is indexed by "common". Optional
            set of names in various game languages or dialects have
            "other" in key.
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CONSOLE[n]["txt"] (list): strings to render as text
        """
        for t in [TS.dash16,
                  f"{p_attr['label']}:",
                  f"  {p_attr['common']}"]:
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = t
            self.CONSOLE_TEXT.append(rec)
        if "other" in p_attr.keys():
            for k, v in p_attr["other"].items():
                rec = copy(self.CONSOLE_REC)
                rec['txt'] = f"    {k}: {v}"
                self.CONSOLE_TEXT.append(rec)

    def set_map_attr(self,
                     p_attr: dict):
        """Set text for a "map" attribute, referring to game-map data.
           Examples: "distance" or "location" expressed in
              kilometers, degrees, or other in-game measures
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CONSOLE[n]["txt"] (list): strings to render as text
        """
        ky = "distance" if "distance" in p_attr.keys() else\
            "location" if "location" in p_attr.keys() else None
        if ky is not None:
            sub_k = ["height", "width"] if ky == "distance" else\
                ["top", "bottom", "left", "right"]
            rec = copy(self.CONSOLE_REC)
            rec['txt'] = TS.dash16
            self.CONSOLE_TEXT.append(rec)
            rec = copy(self.CONSOLE_REC)
            rec["txt"] =\
                f"{p_attr[ky]['label']}:"
            self.CONSOLE_TEXT.append(rec)
            for s in sub_k:
                rec = copy(self.CONSOLE_REC)
                rec["txt"] =\
                    f"  {p_attr[ky][s]['label']}:  " +\
                    f"{p_attr[ky][s]['amt']} " +\
                    f"{p_attr[ky]['unit']}"
                self.CONSOLE_TEXT.append(rec)

    def set_contains_attr(self,
                          p_attr: dict):
        """Set text for a "contains" attribute, referring to things
            contained by another object.
            Examples: "sub-region", "movement" (i.e, movement paths)
        :attr:
        - p_attr (dict): name-value pairs to format
        :sets:
        - self.CONSOLE[n]["txt"] (list): strings to render as text
        """
        rec = copy(self.CONSOLE_REC)
        rec["txt"] = TS.dash16
        self.CONSOLE_TEXT.append(rec)
        rec = copy(self.CONSOLE_REC)
        rec["txt"] = f"{p_attr['label']}:"
        self.CONSOLE_TEXT.append(rec)

        if "sub-region" in p_attr.keys():
            rec = copy(self.CONSOLE_REC)
            rec["txt"] =\
                f"  {p_attr['sub-region']['label']}:"
            self.CONSOLE_TEXT.append(rec)
            for n in p_attr["sub-region"]["names"]:
                rec = copy(self.CONSOLE_REC)
                rec["txt"] = f"    {n}"
                self.CONSOLE_TEXT.append(rec)

        if "movement" in p_attr.keys():
            # roads, waterways, rivers and lakes
            rec = copy(self.CONSOLE_REC)
            rec["txt"] = f"  {p_attr['movement']['label']}:"
            self.CONSOLE_TEXT.append(rec)
            attr = {k:v for k, v in p_attr["movement"].items()
                    if k != "label"}
            for _, v in attr.items():
                rec = copy(self.CONSOLE_REC)
                rec["txt"] = f"    {v['label']}:"
                self.CONSOLE_TEXT.append(rec)
                for n in v["names"]:
                    rec = copy(self.CONSOLE_REC)
                    rec["txt"] = f"      {n}"
                    self.CONSOLE_TEXT.append(rec)

    # Data rendering methods for CONSOLE
    # ==================================
    # def render_text_lines(self)  -- in saskan_game.py

    def set_console_text(self):
        """Format text lines for display in CONSOLE.
        - "catg" identifies source of config data to format.
        - "item" identifies type of data to format.
        
        @TODO:
        - Move the geo data, etc. into a database.
        - May want to revisit, optimize the methods for formatting
          different types of data. Maybe even store img and box
          objects in the DB, rather than rendering them here?
            - Nah. This only gets called once per data source, when
              the user clicks on a menu item. No point in persisting to DB.
        - Use config files only for install-level customizations, overrides.
        """
        # Don't assume what the GUI container will be...
        self.CONSOLE_TEXT.clear()
        # Contents

        pp((self.DATASRC["catg"], self.DATASRC["item"]))

        if self.DATASRC["catg"] == "geo":
            ci = FI.G[self.DATASRC["catg"]][self.DATASRC["item"]]

            pp((ci))

            if "type" in ci.keys():
                self.set_label_name(ci["type"])
            if "contained_by" in ci.keys():
                self.set_label_name_type(ci["contained_by"])
            if "name" in ci.keys():
                self.set_proper_names(ci["name"])
            if "map" in ci.keys():
                self.set_map_attr(ci["map"])
            if "contains" in ci.keys():
                self.set_contains_attr(ci["contains"])
            # self.render_text_lines()

    def compute_map_scale(self,
                          p_attr: dict):
        """Compute scaling, position for the map and grid.
        :attr:
        - p_attr (dict): 'map' data for the "Saskan Lands" region from
            the saskan_geo.json file.
        :sets:
        - self.G_CELLS['map']: map km dimensions and scaling factors

        - Get km dimensions for entire map rectangle
        - Reject maps that are too big
        - Divide g km by m km to get # of grid-cells for map box
            - This should be a float.
        - Multiply # of grid-cells in the map box by px per grid-cell
          to get line height and width in px for the map box.
        - Center 'map' in the 'grid'; by grid count, by px
        
        @DEV:
        - Assignment of km to grid dimensions should not be hard-coded.
        - We need to have a `grids` database table that provides
          different dimensions for different scenarios, just like 
          we have the `maps` table to define "location" of maps.
        - Once that is in place, then "mapping" between grid and map
          can be abstracted into a class like this one, or in the
          saskan_math module.
        """
        err = ""
        map = {'ln': dict(),
               'cl': dict()}
        # Evaluate map line lengths in kilometers
        map['ln']['km'] =\
            {'w': round(int(p_attr["distance"]["width"]["amt"])),
             'h': round(int(p_attr["distance"]["height"]["amt"]))}
        if map['ln']['km']['w'] > TS.G_LNS_KM_W:
            err = f"Map km w {map['w']} > grid km w {TS.G_LNS_KM_W}"
        if map['ln']['km']['h'] > TS.G_LNS_KM_H:
            err = f"Map km h {map['h']} > grid km h {TS.G_LNS_KM_H}"
        if err != "":
            raise ValueError(err)
        # Verified that the map rect is smaller than the grid rect.
        # Compute a ratio of map to grid.
        # Divide map km w, h by grid km w, h
        map['ln']['ratio'] =\
            {'w': round((map['ln']['km']['w'] / TS.G_LNS_KM_W), 4),
             'h': round((map['ln']['km']['h'] / TS.G_LNS_KM_H), 4)}
        # Compute map line dimensions in px
        # Multiply grid line px w, h by map ratio w, h
        map['ln']['px'] =\
            {'w': int(round(TS.G_LNS_PX_W * map['ln']['ratio']['w'])),
            'h': int(round(TS.G_LNS_PX_H * map['ln']['ratio']['h']))}
        # The map rect needs to be centered in the grid rect.
        #  Compute the offset of the map rect from the grid rect.
        #  Compute topleft of the map in relation to topleft of the grid.
        #  The map top is offset from grid top by half the px difference
        #  between grid height and map height.
        #  The map left is offset from grid left by half the px difference
        #  between grid width and map width.
        # And then adjusted once more for the offset of the grid from the window.
        map['ln']['px']['left'] =\
            int(round((TS.G_LNS_PX_W - map['ln']['px']['w']) / 2) +
                      TS.GRID_OFFSET_X)
        map['ln']['px']['top'] =\
            int(round((TS.G_LNS_PX_H - map['ln']['px']['h']) / 2) +
                      (TS.GRID_OFFSET_Y * 4))  #  not sure why, but I need this
        self.G_CELLS["map"] = map

    def set_map_grid_collisions(self):
        """ Store collisions between G_CELLS and 'map' box.
        """
        cells = {k:v for k, v in self.G_CELLS.items() if k != "map"}
        for ck, crec in cells.items():
            self.G_CELLS[ck]["is_inside"] = False
            self.G_CELLS[ck]["overlaps"] = False
            if SR.rect_contains(
                    self.G_CELLS["map"]["box"], crec["box"]):
                self.G_CELLS[ck]["is_inside"] = True
            elif SR.rect_overlaps(
                    self.G_CELLS["map"]["box"], crec["box"]):
                self.G_CELLS[ck]["overlaps"] = True

    # Set "map" dimensions and other content in G_CELLS
    # =================================================
    def set_gamemap_dims(self,
                         p_attr: dict):
        """This method handles placing/creating/drawing map displays
           over the "grid" on the GAMEMAP display.
        :attr:
        - p_attr (dict): game map name-value pairs from geo config data
            For example, 'map' data for the "Saskan Lands" region from
            the saskan_geo.json file.

        - Compute ratio, offsets of map to g_ width & height.
        - Define saskan rect and pygame box for the map
        - Do collision checks between the map box and grid cells
        """
        self.compute_map_scale(p_attr)
        map_px = self.G_CELLS["map"]["ln"]["px"]
        self.G_CELLS["map"]["s_rect"] =  SR.make_rect(map_px["top"],
                                                      map_px["left"],
                                                      map_px["w"],
                                                      map_px["h"])
        self.G_CELLS["map"]["box"] =\
            self.G_CELLS["map"]["s_rect"]["pg_rect"]
        self.set_map_grid_collisions()

    def set_map_grid(self):
        """
        Based on currently selected .DATASRC["catg"] and .DATASRC["item"]:
        - assign values to G_CELLS for "map".
        Note:
        - For now, only "geo" data (saskan_geo.json) is handled
        """
        if self.DATASRC["catg"] == "geo":
            data = FI.G[self.DATASRC["catg"]][self.DATASRC["item"]]
            if "map" in data.keys():
                self.set_gamemap_dims(data["map"])
