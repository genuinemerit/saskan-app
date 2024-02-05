"""

:module:    io_data.py
:author:    GM (genuinemerit @ pm.me)

Saskan Data Management middleware.
"""

import platform
# from typing import Any
import pygame as pg

from copy import copy
from dataclasses import dataclass, field
from enum import Enum
from pprint import pprint as pp     # noqa: F401
from pprint import pformat as pf    # noqa: F401

from io_db import DataBase
from io_file import FileIO
from io_shell import ShellIO

DB = DataBase()
FI = FileIO()
SI = ShellIO()

pg.init()     # Initialize PyGame for use in this module


def init_color(p_color: str) -> pg.Color:
    """
    Return a PyGame color object.
    :args:
    - p_color: (str) name of color
    :returns:
    - (pg.Color) PyGame color object from SaskanConstants.Colors
    """
    c = p_color.lower()
    if c == "black":
        return Colors.CP_BLACK
    elif c == "blue":
        return Colors.CP_BLUE
    elif c == "bluepowder":
        return Colors.CP_BLUEPOWDER
    elif c == "gray":
        return Colors.CP_GRAY
    elif c == "gray_dark":
        return Colors.CP_GRAY_DARK
    elif c == "green":
        return Colors.CP_GREEN
    elif c == "palepink":
        return Colors.CP_PALEPINK
    elif c == "red":
        return Colors.CP_RED
    elif c == "silver":
        return Colors.CP_SILVER
    elif c == "white":
        return Colors.CP_WHITE


def init_rect(p_rect: tuple = None) -> pg.Rect:
    """
    Return a PyGame Rect object.
    :args:
    - p_rect: (tuple) coordinate of the Rect
      if None, then set to 0, 0, 0, 0
      (top, left, bottom, right)
    :returns:
    - (pg.Rect) PyGame Rect object of specified dimensions
    """
    if p_rect is None:
        return pg.Rect(0, 0, 0, 0)
    else:
        return pg.Rect(p_rect)


class Astro(Enum):
    """Constants:
    Astronomical and physics units and conversions.
    """
    # galaxy names
    GADJ = ["Brilliant", "Lustrous", "Twinkling",
            "Silvery", "Argent", "Glistening"]
    GITM = ["Way", "Trail", "Cloud", "Wave", "Skyway"]
    GNAM = ["Galaxy", "Cluster", "Nebula", "Spiral",
            "Starfield",  "Cosmos", "Nebula",
            "Megacosm", "Space"]
    # mass, matter, energy
    DE = "dark energy"
    DM = "dark matter"
    BM = "baryonic matter"
    LCLS = "luminosity class"
    SMS = "solar mass"
    SL = "solar luminosity"
    # objects, astronomical
    BH = "black hole"
    GB = "galactic bulge"
    GC = "galactic cluster"
    GH = "galactic halo"
    GX = "galaxy"
    IG = "interstellar matter"
    SC = "star cluster"
    SCLS = "star class"
    TP = "timing pulsar"            # saskan
    TU = "total universe"           # saskan
    XU = "external universe"        # saskan
    # time-related, real world and saskan
    GS = "galactic second"          # 'galactic' second; saskan
    GMS = "galactic millisecond"    # 'galactic' millisecond; saskan
    PMS = "pulses per millisecond"  # 'galactic' second as # of pulses
    ET = "elapsed time"             # age, duration, time passed
    GYR = "gavoran year"            # saskan
    GDY = "gavoran day"             # saskan
    # rates, speeds, velocities
    ER = "expansion rate"           # of a volume
    UER = "universal expansion rate"
    KSM = "km/s per Mpc"            # km/s per Mpc
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


class Colors(Enum):
    """Constants for CLI and PyGame colors.
    This provides easy access to ANSI escape codes for
    formatting CLI output, as well as PyGame Color
    objects for rendering graphics.
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
    CP_GRAY = pg.Color(80, 80, 80)
    CP_GRAY_DARK = pg.Color(20, 20, 20)
    CP_GREEN = pg.Color(0, 255, 0)
    CP_PALEPINK = pg.Color(215, 198, 198)
    CP_RED = pg.Color(255, 0, 0)
    CP_SILVER = pg.Color(192, 192, 192)
    CP_WHITE = pg.Color(255, 255, 255)


class Geog(Enum):
    """Constants for computations using variety of units
    and formulae for measures of distance at a human or
    (fantasy) planetary geographical scale.
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


class Geom(Enum):
    """Constants assigned to meaningful abbreviations
    and names relating generically to geometry and physics.
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


class GroupAttribute(object):
    """Base class for grouped attribute data structures.
    These convenience structue have default values,
    but they are mutable.
    """

    class ColumnRowIndex(object):
        """Structure for column and row indexes."""
        r: int = 0
        c: int = 0

    class WidthHeight(object):
        """Structure for width and height measures."""
        w: float = 0.0
        h: float = 0.0

    class CoordXYZ(object):
        """Structure for x, y, z coordinates."""
        x: float = 0.0
        y: float = 0.0
        z: float = 0.0

    class CoordXY(object):
        """Structure for x, y coordinates."""
        x: float = 0.0
        y: float = 0.0

    class AxesABC(object):
        """Structure for a, b, c axes."""
        a: float = 0.0
        b: float = 0.0
        c: float = 0.0

    class PitchYawRollAngle(object):
        """Structure for pitch, yaw,, roll angles."""
        pitch: float = 0.0
        yaw: float = 0.0
        roll: float = 0.0

    class GameLatLong(object):
        """
        Game Lat and Long refer to fantasy world locations;
        cannot use standard Earth-based geo-loc modules.

        Latitudes and longitudes are in decimal degrees.
        Lat north is positive; south is negative.
        East, between the fantasy-planet equivalent of
        universal meridien and international date line,
        is positive; west is negative.
        """
        latitude: float = 0.0
        longitude: float = 0.0

    class GameLocation(object):
        """
        This is a general-purpose, high level location
        data structure.

        GameLocation is primarily planar and rectangular.
        Use degrees as the main specifier for locations,
        then compute km based on scaling to the grid.

        Altitudes are provided in meters, with only
        average, min and max stored, a general sense of
        the 3rd dimension. Detailed heights and depths are
        provided in specialized data structures.

        Avoid storage of values that can easily be
        computed or will likely be scaled.
        """
        latitude_north_dg: float = 0.0
        latitude_south_dg: float = 0.0
        longitude_east_dg: float = 0.0
        longitude_west_dg: float = 0.0
        avg_altitude_m: float = 0.0
        max_altitude_m: float = 0.0
        min_altitude_m: float = 0.0

    class Graphic(object):
        """A data structure for identifying a graphic file."""
        img_surface: pg.Surface = pg.Surface((0, 0))
        img_rect: pg.Rect = pg.Rect(0, 0, 0, 0)
        img_url: str = ''
        img_desc: str = ''


class GamePlane(object):
    """
    GamePlane is a general purpose shape structure.
    It is planar and rectangular, defining only the
    corners of a rectangular space relative to x,y
    coordinates in a containing coordinate system.
    Line and fill attributes may optonally be set.
    A pygame Rect object is also provided, based on
    the rectangular corners.
    """
    def _init__(self,
                p_top_left: GroupAttribute.CoordXY,
                p_top_right: GroupAttribute.CoordXY,
                p_bottom_left: GroupAttribute.CoordXY,
                p_bottom_right: GroupAttribute.CoordXY,
                p_fill: bool = False,
                p_fill_color: pg.Color = pg.Color(0, 0, 0),
                p_line_color: pg.Color = pg.Color(0, 0, 0),
                p_line_width: float = 0.0):
        self.coords =\
            self.set_coords(p_top_left,
                            p_top_right,
                            p_bottom_left,
                            p_bottom_right)
        self.fill =\
            self.set_fill(p_fill,
                          p_fill_color)
        self.life =\
            self.set_line(p_line_color,
                          p_line_width)
        self.set_pygame_rect()

    def set_coords(self,
                   p_top_left,
                   p_top_right,
                   p_bottom_left,
                   p_bottom_right) -> dict:
        """ Set abstract coordinates/location
        relative to x,y in a containing coordinate system.
        """
        return {'top_left': p_top_left,
                'top_right': p_top_right,
                'bottom_left': p_bottom_left,
                'bottom_right': p_bottom_right,
                'left': p_top_left.x,
                'top': p_top_left.y,
                'width': p_top_right.x - p_top_left.x,
                'height': p_bottom_left.y - p_top_left.y,}

    def set_fill(self,
                 p_fill,
                 p_fill_color) -> dict:
        """ Set attributes of the plane fill.
        """
        return {'is_filled': p_fill,
                'fill_color': p_fill_color}

    def set_line(self,
                 p_line_color,
                 p_line_width) -> dict:
        """ Set attributes of the plane line.
        """
        return {'line_color': p_line_color,
                'line_width': p_line_width}

    def set_pygame_rect(self) -> pg.Rect:
        """ Set pygame Rect object.
           (left, top, width, height)
        """
        return pg.Rect(self.coords['left'],
                       self.coords['top'],
                       self.coords['width'],
                       self.coords['height'])


class CompareRect(object):
    """
    Methods for comparing (pygame) rectangles:
    - Check for containment
    - Check for intersections (overlap, collision/union)
    - Check for adjacency/borders (clipline)
    - Check for equality/sameness
    """

    def __init__(self):
        pass

    def rect_contains(self,
                      p_box_a: pg.Rect,
                      p_box_b: pg.Rect) -> bool:
        """Determine if rectangle A contains rectangle B.
        use pygame contains
        :args:
        - p_box_a: (pygame.Rect) rectangle A
        - p_box_b: (pygame.Rect) rectangle B
        """
        if p_box_a.contains(p_box_b):
            return True
        else:
            return False

    def rect_overlaps(self,
                      p_box_a: pg.Rect,
                      p_box_b: pg.Rect) -> bool:
        """Determine if rectangle A and rectangle B overlap.
        xxx use pygame colliderect xxx
        use pygame union
        :args:
        - p_box_a: (pygame.Rect) rectangle A
        - p_box_b: (pygame.Rect) rectangle B
        """
        # if p_box_a.colliderect(p_box_b):
        if p_box_a.union(p_box_b):
            return True
        else:
            return False

    def rect_borders(self,
                     p_rect_a: pg.Rect,
                     p_rect_b: pg.Rect) -> bool:
        """Determine if rectangle A and rectangle B share a border.
        use pygame clipline
        :args:
        - p_box_a: (pygame.Rect) rectangle A
        - p_box_b: (pygame.Rect) rectangle B
        """
        if p_rect_a.clipline(p_rect_b):
            return True
        else:
            return False

    def rect_same(self,
                  p_rect_a: pg.Rect,
                  p_rect_b: pg.Rect) -> bool:
        """Determine if rectangle A and rectangle B occupy exactly
        the same space.
        :args:
        - p_box_a: (pygame.Rect) rectangle A
        - p_box_b: (pygame.Rect) rectangle B
        """
        if p_rect_a.topright == p_rect_b.topright and \
           p_rect_a.bottomleft == p_rect_b.bottomleft:
            return True
        else:
            return False


class GameGridData(object):
    """
    In-game storage structure to holds info for managing
    what to display in each grid cell.
    """
    def _init_(self):
        self.rowscols: GroupAttribute.ColumnRowIndex =\
            self.set_rowscols(p_rows=1, p_cols=1)
        self.cells: dict()

    def set_rowscols(self,
                     p_rows: int,
                     p_cols: int) -> GroupAttribute.ColumnRowIndex:
        """ Set the number of rows and columns.
        """
        return GroupAttribute.ColumnRowIndex(p_rows,
                                             p_cols)

    def set_cell_data(self,
                      p_row: int,
                      p_col: int,
                      p_cell_data: dict) -> None:
        """ Set the data for a cell.
        The content of p_cell can be anything as long as it is
        structured as a python dict.
        """
        self.cells[(p_row, p_col)] = p_cell_data


@dataclass(order=True, slots=True)
class Display():
    """Values related to constructing GUI's, but which do not require
    importing and initialzing PyGame, nor reading values from configs.
    """
    # Typesetting
    # -------------------
    DASH16: str = "-" * 16
    FONT_FXD = 'Courier 10 Pitch'
    FONT_MED_SZ = 30
    FONT_SANS = 'DejaVu Sans'
    FONT_SM_SZ = 24
    FONT_TINY_SZ = 12
    LG_FONT_SZ = 36
    # PyGame Fonts
    # -------------------
    F_SANS_TINY = pg.font.SysFont(FONT_SANS, FONT_TINY_SZ)
    F_SANS_SM = pg.font.SysFont(FONT_SANS, FONT_SM_SZ)
    F_SANS_MED = pg.font.SysFont(FONT_SANS, FONT_MED_SZ)
    F_SANS_LG = pg.font.SysFont(FONT_SANS, LG_FONT_SZ)
    F_FIXED_LG = pg.font.SysFont(FONT_FXD, LG_FONT_SZ)
    # PyGame Cursors
    # -------------------
    CUR_ARROW = pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW)
    CUR_CROSS = pg.cursors.Cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
    CUR_HAND = pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)
    CUR_IBEAM = pg.cursors.Cursor(pg.SYSTEM_CURSOR_IBEAM)
    CUR_WAIT = pg.cursors.Cursor(pg.SYSTEM_CURSOR_WAIT)
    # PyGame Keyboard
    # -------------------
    KY_QUIT = (pg.K_q, pg.K_ESCAPE)
    KY_ANIM = (pg.K_F3, pg.K_F4, pg.K_F5)
    KY_DATA = (pg.K_a, pg.K_l)
    KY_RPT_TYPE = (pg.K_KP1, pg.K_KP2, pg.K_KP3)
    KY_RPT_MODE = (pg.K_UP, pg.K_RIGHT, pg.K_LEFT)
    # Saskan Game Platform
    # -------------------
    info = pg.display.Info()
    FRAME = "game_frame"  # --> c_frame.json
    MENUS = "game_menus"  # --> c_menus.json
    PLATFORM = (
        FI.F[FRAME]["dsc"] +
        #  " | " + platform.platform() +
        #  " | " + platform.architecture()[0] +
        f" | monitor (w, h): {info.current_w}, {info.current_h}" +
        " | Python " + platform.python_version() +
        " | Pygame " + pg.version.ver)
    # Window/overall frame for Saskan Game app
    # -------------------
    WIN_W = round(info.current_w * 0.9)
    WIN_H = round(info.current_h * 0.9)
    WIN_MID = (WIN_W / 2, WIN_H / 2)
    WIN = pg.display.set_mode((WIN_W, WIN_H))
    pg.display.set_caption(FI.F[FRAME]["ttl"])
    info = pg.display.Info()
    KEYMOD_NONE = 4096
    TIMER = pg.time.Clock()
    # Menu bar for Saskan Game app
    # -------------------
    MBAR_X = WIN_W * 0.01
    MBAR_Y = WIN_H * 0.005
    MBAR_H = WIN_H * 0.04
    MBAR_W = (WIN_W - (MBAR_X * 2)) / len(FI.M[MENUS]["menu"])
    MBAR_W = 240 if MBAR_W > 240 else MBAR_W
    MBAR_MARGIN = 6
    # Game Map (grid) window for Saskan game
    # --------------------------------------
    GAMEMAP_TTL = FI.W["game_windows"]["gamemap"]["ttl"]
    GAMEMAP_X = int(round(WIN_W * 0.01))
    GAMEMAP_Y = int(round(WIN_H * 0.06))
    GAMEMAP_W = int(round(WIN_W * 0.8))
    GAMEMAP_H = int(round(WIN_H * 0.9))
    GRID_S_RECT = GamePlane(
        p_top_left=GroupAttribute.CoordXY(GAMEMAP_X, 0),
        p_top_right=GroupAttribute.CoordXY(GAMEMAP_W, 0),
        p_bottom_left=GroupAttribute.CoordXY(GAMEMAP_X, GAMEMAP_H),
        p_bottom_right=GroupAttribute.CoordXY(GAMEMAP_W, GAMEMAP_H))
    GRID_BOX = GRID_S_RECT["box"]
    GRID_OFFSET_X = int(round(GAMEMAP_W * 0.01))
    GRID_OFFSET_Y = int(round(GAMEMAP_H * 0.02))
    # Dynamic (DB) values for the grid:
    GRID_ROWS = 32
    GRID_COLS = 46
    GRID_VISIBLE = False
    GRID_CELL_PX_W = int(round(GAMEMAP_W - GRID_OFFSET_X) / GRID_COLS)
    GRID_CELL_PX_H = int(round(GAMEMAP_H - GRID_OFFSET_Y) / GRID_ROWS)
    GRID_CELL_KM_W = 33
    GRID_CELL_KM_H =\
        int(round(GRID_CELL_KM_W * (GRID_CELL_PX_H / GRID_CELL_PX_W)))
    G_LNS_PX_W = GRID_CELL_PX_W * GRID_COLS
    G_LNS_PX_H = GRID_CELL_PX_H * GRID_ROWS
    G_LNS_KM_W = GRID_CELL_KM_W * GRID_COLS
    G_LNS_KM_H = GRID_CELL_KM_H * GRID_ROWS
    G_LNS_X_LEFT = int(round(GRID_OFFSET_X + GRID_BOX.x))
    G_LNS_X_RGHT = int(round(G_LNS_X_LEFT + G_LNS_PX_W))
    G_LNS_Y_TOP = int(round(GRID_OFFSET_Y + GRID_BOX.y))
    G_LNS_Y_BOT = int(round(G_LNS_Y_TOP + G_LNS_PX_H))
    G_LNS_HZ = list()     # (x1, y1), (x2, y2)
    G_LNS_VT = list()     # (x1, y1), (x2, y2)
    # x,y each horiz or vert line segment
    for hz in range(GRID_ROWS + 1):
        y = G_LNS_Y_TOP + (hz * GRID_CELL_PX_H)
        G_LNS_HZ.append([(G_LNS_X_LEFT, y), (G_LNS_X_RGHT, y)])
    for vt in range(GRID_COLS + 1):
        x = G_LNS_X_LEFT + (vt * GRID_CELL_PX_W)
        G_LNS_VT.append([(x, G_LNS_Y_TOP), (x, G_LNS_Y_BOT)])
    # G_CELL = grid data-cell matrix, a record for each grid-cell
    # The static data for each grid-cell consists of:
    # - KEY: unique string in "0n_0n" format
    # - DATA:
    #   - SaskanRect object for grid-cell
    #   - PyGame Rect object for grid-cell
    # Then will be overloaded as needed based on MAPs, DB recs, etc.
    # --------------------------------------------------------------
    GRID = GameGridData()
    GRID.set_rowscols(p_rows=GRID_ROWS, p_cols=GRID_COLS)
    # Console window for Saskan app
    # -------------------------------
    CONSOLE = FI.W["game_windows"]["console"]
    CONSOLE_X = int(round(GAMEMAP_X + GAMEMAP_W + 20))
    CONSOLE_Y = GAMEMAP_Y
    CONSOLE_W = int(round(WIN_W * 0.15))
    CONSOLE_H = GAMEMAP_H
    CONSOLE_BOX = pg.Rect(CONSOLE_X, CONSOLE_Y,
                          CONSOLE_W, CONSOLE_H)
    # For now, the header/title on CONSOLE is static
    CONSOLE_TTL_TXT = FI.W["game_windows"]["console"]["ttl"]
    CONSOLE_TTL_IMG =\
        F_SANS_MED.render(CONSOLE_TTL_TXT, True,
                          Colors.CP_BLUEPOWDER,
                          Colors.CP_BLACK)
    CONSOLE_TTL_BOX = CONSOLE_TTL_IMG.get_rect()
    CONSOLE_TTL_BOX.topleft = (CONSOLE_X + 5, CONSOLE_Y + 5)
    # Inf Bar for Saskan app
    # -------------------------------
    IBAR_LOC = (GAMEMAP_X, int(round(WIN_H * 0.97)))
    # Help Pages -- external web pages, displayed in a browser
    # ----
    WHTM = FI.U["uri"]["help"]  # links to web pages / help pages


# =============================================================
# DB/ORM table definitions
#
# The following models are used to create SQLITE tables and
#   standard/generic SQL commands (INSERT, UPDATE, SELECT).
# A classmethod identifies:
# - SQLITE constraints,
# - GROUPed types derived from Pydantic data types defined above,
# - sort order for SELECT queries.
# =======================================================
class Backup(object):

    tablename: str = "BACKUP"
    bkup_nm: str
    bkup_dttm: str
    bkup_type: str
    file_from: str
    file_to: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["bkup_nm", "bkup_dttm"],
            "ORDER": ["bkup_dttm DESC", "bkup_nm ASC"]
        }


class Universe(object):

    tablename: str = "UNIVERSE"
    univ_nm_pk: str
    radius_gly: float = 0.0
    volume_gly3: float = 0.0
    volume_pc3: float = 0.0
    elapsed_time_gyr: float = 0.0
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


class ExternalUniv(object):

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


class GalacticCluster(object):

    tablename: str = "GALACTIC_CLUSTER"
    galactic_cluster_nm_pk: str
    univ_nm_fk: str = ''
    center_from_univ_center_gly: GroupAttribute.CoordXYZ
    boundary_gly: pg.Rect
    cluster_shape: str = 'ellipsoid'
    shape_pc: GroupAttribute.CoordXYZ
    shape_axes: GroupAttribute.AxesABC
    shape_rot: GroupAttribute.PitchYawRollAngle
    volume_pc3: float = 0.0
    mass_kg: float = 0.0
    dark_energy_kg: float = 0.0
    dark_matter_kg: float = 0.0
    baryonic_matter_kg: float = 0.0
    timing_pulsar_pulse_per_ms: float = 0.0
    timing_pulsar_loc_gly: GroupAttribute.CoordXYZ

    @classmethod
    def constraints(cls):
        return {
            "PK": ["galactic_cluster_nm_pk"],
            "FK": {"univ_nm_fk": ("UNIVERSE", "univ_nm_pk")},
            "CK": {"cluster_shape": ['ellipsoid', 'spherical']},
            "DT": {},
            "GROUP": {"center_from_univ_center_gly":
                      GroupAttribute.CoordXYZ,
                      "timing_pulsar_loc_gly":
                      GroupAttribute.CoordXYZ,
                      "shape_pc": GroupAttribute.CoordXYZ,
                      "shape_axes": GroupAttribute.AxesABC,
                      "shape_rot":
                      GroupAttribute.PitchYawRollAngle},
            "ORDER": ["univ_nm_fk ASC",
                      "galactic_cluster_nm_pk ASC"]
        }


class Galaxy(object):

    tablename: str = "GALAXY"
    galaxy_nm_pk: str
    galactic_cluster_nm_fk: str = ''
    relative_size: str = 'medium'
    center_from_univ_center_kpc: GroupAttribute.CoordXYZ
    halo_radius_pc: float = 0.0
    boundary_pc: pg.Rect
    volume_gpc3: float = 0.0
    mass_kg: float = 0.0
    bulge_shape: str = 'ellipsoid'
    bulge_center_from_center_ly: GroupAttribute.CoordXYZ
    bulge_dim_axes: GroupAttribute.AxesABC
    bulge_black_hole_mass_kg: float = 0.0
    bulge_volume_gpc3: float = 0.0
    bulge_total_mass_kg: float = 0.0
    star_field_shape: str = 'ellipsoid'
    star_field_dim_from_center_ly: GroupAttribute.CoordXYZ
    star_field_dim_axes: GroupAttribute.AxesABC
    star_field_vol_gpc3: float = 0.0
    star_field_mass_kg: float = 0.0
    interstellar_mass_kg: float = 0.0

    @classmethod
    def constraints(cls):
        return {
            "PK": ["galaxy_nm_pk"],
            "FK": {"galactic_cluster_nm_fk":
                   ("GALACTIC_CLUSTER",
                    "galactic_cluster_nm_pk")},
            "CK": {"relative_size": ['small', 'medium', 'large'],
                   "bulge_shape": ['ellipsoid', 'spherical'],
                   "star_field_shape": ['ellipsoid', 'spherical']},
            "GROUP": {"center_from_univ_center_kpc":
                      GroupAttribute.CoordXYZ,
                      "bulge_center_from_center_ly":
                      GroupAttribute.CoordXYZ,
                      "bulge_dim_axes": GroupAttribute.AxesABC,
                      "star_field_dim_from_center_ly":
                      GroupAttribute.CoordXYZ,
                      "star_field_dim_axes":
                      GroupAttribute.AxesABC},
            "ORDER": ["galactic_cluster_nm_fk ASC",
                      "galaxy_nm_pk ASC"]
        }


"""
Notes for generating star systems, planets, and other objects.

For a simplified star system generation algorithm that balances storytelling
and basic simulation, consider the following critical data elements:

    Star Type:
        Spectral Class: O, B, A, F, G, K, M (from hottest to coolest).
        O - Blue
        B - Blue-White
        A - White
        F - Yellow-White
        G - Yellow (like the Sun)
        K - Orange
        M - Red
        Luminosity: Brightness of the star.
        I - Supergiant = 1000-10000Ls
        II - Bright Giant = 100-1000Ls
        III - Giant = 10-100Ls
        IV - Subgiant = 1-10Ls
        V - Main Sequence = ~1Ls (Ls = Luminosity of the Sun)

    Planetary Orbits:
        Habitable Zone: Distance range from the star where conditions could
        support liquid water.
        Distribution of Planets: Inner rocky planets, outer gas giants.
        Orbital Eccentricity: How elliptical or circular the orbits are.

    Planetary Characteristics:
        Size and Mass: Determines gravity and atmosphere retention.
        Atmosphere Composition: Essential for life support.
        Surface Conditions: Temperature, pressure, and climate.
        Axial Tilt: Influences seasons and climate variations.
        Natural Satellites: Presence of moons.

    Asteroid Belts and Comets:
        Distribution: Inner, outer, or multiple belts.
        Density: Sparse or dense with potential impact events.

    Star System Dynamics:
        Binary/Multiple Star Systems:
          Presence of companion stars.
        Stability: Long-term stability of planetary orbits.
        Age of the Star: Influences the evolution of planets
        and potential for life.
            Spectral types O, B, and A represent "young" stars.
                years? 1-10 million years
            Spectral types F, G, and K represent
            "middle-aged" stars.
                years? 1-10 billion years
            Spectral type M represents "old" stars.
                years? 1-10 trillion years

    Exotic Elements:
        Presence of Anomalies: Unusual phenomena, e.g.,
        pulsars, black holes.
        Unstable Conditions: Solar flares, intense radiation.

    Historical Events:
        Past Catastrophes: Previous asteroid impacts, major
        events.
        Evolutionary Factors: Historical conditions affecting
        life evolution.

    Special Conditions:
        Tidally Locked Planets: Planets with one side
        permanently facing the star.
        Rogue Planets: Unbound to any star.

    Metadata for Storytelling:
        Dominant Species: If there is intelligent life, their
        characteristics.
        Cultural Factors: Influences on civilizations.
        Current State: Technological level, conflicts,
        alliances.

    Visual Characteristics:
        Sky Colors: Affected by atmospheric composition.
        Day/Night Lengths: Influences daily life.
"""


class StarSystem(object):

    tablename: str = "STAR_SYSTEM"
    star_system_nm_pk: str
    galaxy_nm_fk: str
    nearest_pulsar_nm_fk: str = ''
    nearest_black_hole_nm_fk: str = ''
    binary_star_system_nm_fk: str = ''
    is_black_hole: bool = False
    is_pulsar: bool = False
    center_from_galaxy_center_pc: GroupAttribute.CoordXYZ
    boundary_pc: pg.Rect
    volume_pc3: float = 0.0
    mass_kg: float = 0.0
    system_shape: str = 'ellipsoid'
    relative_size: str = 'medium'
    spectral_class: str = 'G'
    aprox_age_gyr: float = 0.0
    luminosity_class: str = 'V'
    frequency_of_flares: str = 'rare'
    intensity_of_flares: str = 'low'
    frequency_of_comets: str = 'rare'
    unbound_planets_cnt: int = 0
    orbiting_planets_cnt: int = 0
    inner_habitable_boundary_au: float = 0.0
    outer_habitable_boundary_au: float = 0.0
    planetary_orbits_shape: str = 'circular'
    orbital_stability: str = 'stable'
    asteroid_belt_density: str = 'sparse'
    asteroid_belt_loc: str = 'inner'

    @classmethod
    def constraints(cls):
        return {
            "PK": ["star_system_nm_pk"],
            "FK": {"galaxy_nm_fk": ("GALAXY", "galaxy_nm_pk"),
                   "binary_star_system_nm_fk":
                   ("STAR_SYSTEM", "star_system_nm_pk"),
                   "nearest_pulsar_nm_fk":
                   ("STAR_SYSTEM", "star_system_nm_pk"),
                   "nearest_black_hole_nm_fk":
                   ("STAR_SYSTEM", "star_system_nm_pk")},
            "CK": {"relative_size": ['small', 'medium', 'large'],
                   "spectral_class":
                   ['O', 'B', 'A', 'F', 'G', 'K', 'M'],
                   'luminosity_class':
                   ['I', 'II', 'III', 'IV', 'V'],
                   "system_shape": ['ellipsoid', 'spherical'],
                   "planetary_orbits_shape":
                   ['circular', 'elliptical'],
                   "orbital_stability": ['stable', 'unstable'],
                   "asteroid_belt_density": ['sparse', 'dense'],
                   'asteroid_belt_loc':
                   ['inner', 'outer', 'multiple'],
                   "frequency_of_flares":
                   ['rare', 'occasional', 'frequent'],
                   "intensity_of_flares":
                   ['low', 'medium', 'high'],
                   "frequency_of_comets": ['rare', 'occasional', 'frequent']},
            "GROUP": {"center_from_galaxy_center_pc":
                      GroupAttribute.CoordXYZ,
                      "bulge_dim_from_center_ly":
                      GroupAttribute.CoordXYZ,
                      "bulge_dim_axes":
                      GroupAttribute.AxesABC,
                      "star_field_dim_from_center_ly":
                      GroupAttribute.CoordXYZ,
                      "star_field_dim_axes":
                      GroupAttribute.AxesABC},
            "ORDER": ["galaxy_nm_fk ASC",
                      "star_system_nm_pk ASC"]
        }


"""
Planetary charts, indicating the path of 'wanderers' and their
'congruences', and so on as seen from the perspective of a given
world, will be tracked on a separate table or set of tables.
Such charts would include the path of comets and rogue planets,
unless I decide to track those on a separate table or set of tables.

Tracking of seasons and accounting of calendars is also
handled on separate tables.  The same is true for tracking
of eclipses and other astronomical events.
"""


class World(object):
    """
    @DEV:
    It may not be possible to assign a default value to what
    will become a BLOB. If so, then just leave off the default
    assignment and make sure that the code assigns the
    desired values.
    """

    tablename: str = "WORLD"
    world_nm_pk: str
    star_system_nm_fk: str
    world_type: str = 'habitable'
    obliquity_dg: float = 0.0    # a/k/a axial tilt
    distance_from_star_au: float = 0.0
    distance_from_star_km: float = 0.0
    radius_km: float = 0.0
    mass_kg: float = 0.0
    gravity_m_per_s_per_s: float = 0.0
    orbit_gdy: float = 0.0
    orbit_gyr: float = 0.0
    tidally_locked: bool = False
    rotation_gdy: float = 0.0
    rotation_direction: str = 'prograde'
    orbit_direction: str = 'prograde'
    moons_cnt: int = 0
    world_desc: str
    atmosphere: str
    sky_color: pg.Color = Colors.CP_BLUE
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
            "CK": {"world_type":
                   ['habitable', 'gas giant', 'rocky',
                    'desert', 'oceanic', 'ice planet',
                    'molten', 'other'],
                   "rotation_direction": ['prograde', 'retrograde'],
                   "orbit_direction": ['prograde', 'retrograde']},
            "ORDER": ["star_system_nm_fk ASC",
                      "world_nm_pk ASC"]
        }


"""
Lunar charts, indicating full moons, new moons, other phases,
and so on will be tracked on a separate table or set of tables.
"""


class Moon(object):

    tablename: str = "MOON"
    moon_nm_pk: str
    world_nm_fk: str
    center_from_world_center_km: GroupAttribute.CoordXYZ
    mass_kg: float = 0.0
    radius_km: float = 0.0
    obliquity_dg: float = 0.0    # a/k/a axial tilt
    tidally_locked: bool = True
    rotation_direction: str = 'prograde'
    orbit_direction: str = 'prograde'
    orbit_world_days: float = 0.0
    rotation_world_days: float = 0.0
    initial_velocity: float = 0.0
    angular_velocity: float = 0.0

    @classmethod
    def constraints(cls):
        return {
            "PK": ["moon_nm_pk"],
            "FK": {"world_nm_fk": ("WORLD", "world_nm_pk")},
            "CK": {"rotation_direction":
                   ['prograde', 'retrograde'],
                   "orbit_direction":
                   ['prograde', 'retrograde']},
            "GROUP": {"center_from_world_center_km":
                      GroupAttribute.CoordXYZ},
            "ORDER": ["world_nm_fk ASC",
                      "moon_nm_pk ASC"]
        }


class Map(object):
    """
    Foreign key --
    - MAP (1) contains <-- MAPs (n)   and
      MAPs (n) are contained by --> MAP (1).

    /* A map is always a rectangle.
       This structure is for defining 'templates' of maps
         that lay over a grid. For example, there might be
         a map_name that is associated with provinces and
         a different one that is associated with regions.
         There could also be multiple variations of, say,
         county-level maps, depending on large or small, for
         example.
       It will be associated with table w/ more detailed info
       relating to things like:
         - geography (continents, regions, mountains, hills, rivers,
              lakes, seas, oceans, etc.)
         - political boundaries (countries, provinces, states, counties, etc.)
         - roads, paths, trails, waterways, bodies of water, etc.
         - cities, towns, villages, neighborhoods, etc.
         - other points of interest (ruins, temples, etc.)
         - natural resources (mines, quarries, etc.)
         - demographics (population density, etc.)
    */
    """

    tablename: str = "MAP"
    map_nm_pk: str
    container_map_nm_fk: str = ''
    map_loc: GroupAttribute.GameLocation

    @classmethod
    def constraints(cls):
        return {
            "PK": ["map_nm_pk"],
            "FK": {"container_map_nm_fk": ("MAP", "map_nm_pk")},
            "GROUP": {"map_loc": GroupAttribute.GameLocation},
            "ORDER": ["map_nm_pk ASC"]
        }


class MapXMap(object):
    """
    Associative keys --
    - MAPs (n) overlap <--> MAPs (n)
    - MAPs (n) border <--> MAPs (n)
    PK is a composite key of map_nm_1_fk and map_nm_2_fk
    """

    tablename: str = "MAP_X_MAP"
    map_nm_1_fk: str
    map_nm_2_fk: str
    touch_type: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["map_nm_1_fk", "map_nm_2_fk"],
            "FK": {"map_nm_1_fk": ("MAP", "map_nm_pk"),
                   "map_nm_2_fk": ("MAP", "map_nm_pk")},
            "CK": {"touch_type": ['borders', 'overlaps']},
            "ORDER": ["map_nm_1_fk ASC", "map_nm_2_fk ASC"]
        }


class Grid(object):
    """
    Define the size of a grid (r, c), the dim of the cells (w, h)
    in PyGame px, and the dim of each cell in km (w, h).
    The z layers are provided for future use, e.g. in case I want to
    use them to track altitude, depth, or elevation in a 3D game, or
    with maps that provide z-level data.

    @DEV:
    - Consider other grid types, such as hexagonal, triangular, etc.
    """

    tablename: str = "GRID"
    grid_nm_pk: str
    row_cnt: int
    col_cnt: int
    z_up_cnt: int
    z_down_cnt: int
    width_px: float
    height_px: float
    width_km: float
    height_km: float
    z_up_m: float
    z_down_m: float

    @classmethod
    def constraints(cls):
        return {
            "PK": ["grid_nm_pk"],
            "ORDER": ["grid_nm_pk ASC"]
        }


class GridXMap(object):
    """
    Associative keys --
    - GRIDs (n) <--> MAPs (n)
    PK is a composite key of grid_nm_fk and map_nm_fk
    """

    tablename: str = "GRID_X_MAP"
    grid_nm_fk: str
    map_nm_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["grid_nm_fk", "map_nm_fk"],
            "FK": {"grid_nm_fk": ("GRID", "grid_nm_pk"),
                   "map_nm_fk": ("MAP", "map_nm_pk")},
            "ORDER": ["grid_nm_fk ASC", "map_nm_fk ASC"]
        }


"""
The language elements may be an area where I might want to
start investigating the use of an integrated AI system.  Advantage
could be that fairly complex rules can be expressed in natural
language and the AI can take care of the details of generating
the language elements, refining the rules.
"""


class CharMember(object):
    """
    Describes the individual characters in a character set.
    Where the character is not represented in Unicode, a picture
    of the character (BLOB) and its name is stored, along with
    a description.
    Member types are defined by the type of writing system
    (character set) they belong to. But further categorizations
    are possible for numerics, punctuation, and so on.
    """

    tablename: str = "CHAR_MEMBER"
    char_member_id_pk: int
    char_member_nm: str
    char_set_nm_fk: str
    char_member: GroupAttribute.Graphic
    char_member_desc: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["char_member_id_pk"],
            "UQ": ["char_member_nm"],
            "FK": {"char_set_nm_fk":
                   ("CHAR_SET", "char_set_nm_pk")},
            "CK": {"char_set_type": ['alphabet', 'abjad',
                                     'abugida', 'syllabary', 'ideogram']},
            "GROUP": {"char_member": GroupAttribute.Graphic},
            "ORDER": ["char_set_nm_fk ASC", "char_member_nm ASC"]
        }


class CharSet(object):
    """
    Description of a set of characters used in a language.
    An alphabet represents consonants and vowels each
    separately as individual letters.
    An abjad represents consonants only as distinct letters;
    vowels are represented as diacritics. In some cases, the
    vowels may be omitted entirely, and are implied from
    context .
    An abugida represents consonants as separate letters, but
    the glyph used also implies a “default” vowel, and deletion
    or change of vowel is represented with modifications of the
    glyph, in a fashion similar to diacritics, but not the same.
    A syllabary represents a syllable of the language - usually
    but not invariably in the form CV (consonant followed by
    vowel) - as a single glyph; there is no necessary
    relationship between glyphs that carry the same consonant,
    or the same vowel.
    Ideograms use a single - often complex - glyph to represent
    a word or concept. In some languages, the ideogram may
    actually be compound, with one portion signalling the
    pronunciation, and another portion signalling the meaning.
    """

    tablename: str = "CHAR_SET"
    char_set_nm_pk: str
    char_set_type: str = 'alphabet'
    char_set_desc: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["char_set_nm_pk"],
            "CK": {"char_set_type":
                   ['alphabet', 'abjad', 'abugida',
                    'syllabary', 'ideogram']},
            "ORDER": ["char_set_nm_pk ASC"]
        }


class LangFamily(object):
    """
    Describe basic features of a language family, without getting too
    complicated.
    - desc: overview
    - phonetics: how the language sounds, e.g. guttural, nasal, etc.
    - cultural influences: e.g. from other languages, or from
      historical events, migration patterns, etc.
    NB: 'baric' is an in-game construct, not a real-world one.
    """

    tablename: str = "LANG_FAMILY"
    lang_family_nm_pk: str
    char_set_nm_fk: str = 'baric'
    lang_family_desc: str = ''
    phonetics: str = ''
    cultural_influences: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["lang_family_nm_pk"],
            "FK": {"char_set_nm_fk": ("CHAR_SET", "char_set_nm_pk")},
            "CK": {"char_set_nm_fk":
                   ['baric', 'runic', 'gromik',
                    'arshk', 'other']},
            "ORDER": ["lang_family_nm_pk ASC"]
        }


class Language(object):
    """
    Describe basic features of a language, without getting too
    complicated.
    - desc: overiew
    - gramatics: how phrases are generally structured,
        e.g. subject-verb-object
    - lexicals: major sources of lexicon, for example, lots of
        words relating to the sea, or to the sky, or to the
        land, or to the stars, or to the gods, etc.
    - social influences: e.g. from other languages, or from
        class, trade, migration patterns, etc.
    - word formations:  how words are generally structured,
        e.g. single-syllable-only, consonant-vowel-consonant,
        multiples by prefix, etc.
    More possible features:
/*
lang_object structure:
{"glossary":
    {"phrase": "definition", ...},
 "lexicon":
    {"word": "definition", ...},
 "grammar":
    # the entire structure of a language, includes most of the
    following,
    # as well as things like rules for making plurals, etc.
    {"rule": "explanation", ...},
 "phonology":
   # distribtution of phonemes (sounds) in a language
    {"rule": "explanation", ...},
 "morphology":
   # how words are constructed from morphemes (smallest units
   of meaning)
    {"rule": "explanation", ...},
 "syntax":
    # how words are combined into phrases and sentences
    {"rule": "explanation", ...},
 "semantics":
    {"rule": "explanation", ...},
 "pragmatics":
   # how context affects meaning, for example, intention,
   social status, etc.
    {"rule": "explanation", ...},
 "orthography":
   # how a language is written, for example, alphabet,
   syllabary, etc.
    {"rule": "explanation", ...},
    {"letter": "pronunciation", ...},
 "phonotactics":
    # how sounds are combined into syllables and words
     {"rule": "explanation", ...},
    {"rule": "explanation", ...},
*/
    """

    tablename: str = "LANGUAGE"
    lang_nm_pk: str
    lang_family_nm_fk: str
    lang_desc: str = ''
    gramatics: str = ''
    lexicals: str = ''
    social_influences: str = ''
    word_formations: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["lang_nm_pk"],
            "FK": {"lang_family_nm_fk":
                   ("LANG_FAMILY", "lang_family_nm_pk")},
            "ORDER": ["lang_family_nm_fk ASC", "lang_nm_pk ASC"]
        }


class LangDialect(object):
    """
    Describe basic features of a dialect, without getting too
    complicated.
    - divergence_factors: how the dialect differs from the
      main language, e.g. pronunciation, vocabulary, etc.
    - syncretic_factors: how the dialect is similar to or borrows
      from neighboring languages, e.g. pronunciation, vocabulary, ..
    - preservation_factors: how the dialect preserves old features
      of the main language which are no longer standard
    """

    tablename: str = "LANG_DIALECT"
    dialect_nm_pk: str
    lang_nm_fk: str
    dialect_desc: str = ''
    divergence_factors: str = ''
    syncretic_factors: str = ''
    preservation_factors: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["dialect_nm_pk"],
            "FK": {"lang_nm_fk":
                   ("LANGUAGE", "lang_nm_pk")},
            "ORDER": ["lang_fnm_fk ASC", "dialect_nm_pk ASC"]
        }


class Glossary(object):
    """
    The glossary is a multi-lingual dictionary of sorts.
    It is a collection of words and phrases , and their
    translations
    into other languages. A glossary unit is assigned a
    gloss_uid.
    That value is shared by entries in the glossary for the same
    concept.  For example, the gloss_uid for the concept of of
    "bear"
    (in the "common" language, e.g. English) might be 13453.
    Then entries for the word meaning "bear" in the various
    game languages and dialects would all have the same
    gloss_uid. May eventually want to look into using the
    sqlite CREATE INDEX command to optimize lookups.
    Remember that the gloss_uid is neither a PK nor an FK.
    """

    tablename: str = "GLOSSARY"
    gloss_uid: int
    lang_nm_fk: str
    dialect_nm_fk: str = ''
    gloss_value: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["gloss_uid", "lang_nm_fk", "dialect_nm_fk"],
            "FK": {"lang_nm_fk": ("LANGUAGE", "lang_nm_pk"),
                   "dialect_nm_fk": ("LANG_DIALECT", "lang_nm_pk")},
            "ORDER": ["gloss_uid ASC", "gloss_value ASC",
                      "lang_nm_fk ASC", "dialect_nm_fk ASC"]
        }


class Lake(object):
    """
    Geographic features, e.g. lakes, rivers, mountains, etc. are
    named by reference to a gloss_uid. It is a PK on this table,
    but not on the GLOSSARY table. This may be an area where a VIEW
    could come in handy, but do that later.

    Most geo features have a complex line defined by a series of points,
    preferably defined by a tuple of latitude and longitude.
    The more points are added, the more precise the curve or lines.
    Points stored as JSON.  No Pydantic model  since they have an
    undetermined length. SQL generator code identifies them via a
    classmethod "constraint" keyed by "JSON".

    catchment_area_radius_m: The area of land where rainfall is
    collected and drained into the lake. This is not the same as
    the area of the lake itself. For game purposes,
    let's assume it is a circle with a radius.

    accessibility: How easy it is to reach the lake, whether
    there are roads, trails, or settlements nearby. This can likely
    be quantified in other ways, but keep this attribute to help
    with design

    special_features: Any unique or notable features, like islands,
    underwater caves, or geothermal activity

    lake_usage:  fishing, recreation, transportation, as a water
    source for nearby settlements. could expand to more attributes
    like resevoir.

    conservation_status: Efforts to protect or preserve the lake

    current_conditions: water quality, temperature, frozen, etc.

    JSON:
    lake_shorline_points: [GameLatLong, ..]
    """

    tablename: str = "LAKE"
    lake_nm_gloss_uid_pk: int
    lake_shoreline_points: str
    lake_size: str = "medium"
    water_type: str = "freshwater"
    lake_type: str = "lake"
    tidal_influence: bool = False
    lake_surface_m2: float
    max_depth_m: float
    avg_depth_m: float
    lake_altitude_m: float
    catchment_area_radius_m: float

    lake_origin: str = ''
    flora_and_fauna: str = ''
    water_color: str = ''
    accessibility: str = ''
    special_features: str = ''
    lake_usage: str = ''
    legends_or_myths: str = ''
    lake_history: str = ''
    conservation_status: str = ''
    current_conditions: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["lake_nm_gloss_uid_pk"],
            "FK": {"lake_nm_gloss_uid_pk": ("GLOSSARY", "gloss_uid_pk")},
            "CK": {"lake_size": ['small', 'medium', 'large'],
                   "water_type": ['freshwater', 'saline', 'brackish'],
                   "lake_type": ['lake', 'reservoir', 'pond',
                                 'pool', 'loch', 'hot spring',
                                 'swamp', 'marsh', 'mill pond',
                                 'oxbow lake', 'spring', 'sinkhole',
                                 'acquifer', 'vernal pool', 'wadi']},
            "JSON": ["lake_shoreline_points"],
            "ORDER": ["lake_nm_gloss_uid_pk ASC"]
        }


class LakeXMap(object):
    """
    Associative keys --
    - LAKEs (n) <--> MAPs (n)
    PK is a composite key of lake_nm_fk and map_nm_fk
    """

    tablename: str = "LAKE_X_MAP"
    lake_nm_gloss_uid_fk: str
    map_nm_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["lake_nm_gloss_uid_fk", "map_nm_fk"],
            "FK": {"lake_nm_gloss_uid_fk":
                   ("LAKE", "lake_nm_gloss_uid_pk"),
                   "map_nm_fk": ("MAP", "map_nm_pk")},
            "ORDER":
            ["lake_nm_gloss_uid_fk ASC", "map_nm_fk ASC"]
        }


class River(object):
    """
    drainage_basin_m: Avg area of land where rainfall is
    collected and drained into the river on each bank. For game
    purposes, just select a number of meters from center of
    river.

    avg_velocity_m_per_h: Meters per hour on average. This is
    not the same as the max velocity, which is likely to be
    much higher.

    JSON:
    river_course_points: [GameLatLong, ..]
    river_bank_points: [GameLatLong, ..]
    "hazards":
    [{"uid": int, "type": <'rapids', 'wreckage', 'sandbar',
                                      'waterfall', 'shallow',
                                      'dam',
                                      'weir'. 'habitat'>,
                 "loc": GameLatLong}, ...],
    "features":
    [{"uid": int, "type": <'lock', 'delta', 'bridge',
                                       'crossing', 'footbridge',
                                       'pier', 'marina',
                                       'boathouse',
                                       'habitat'>,
                   "loc": GameLatLong}, ...]
    """
    tablename: str = "RIVER"
    river_nm_gloss_uid_fk: int
    river_course_points: str
    river_bank_points: str
    sea_to_gloss_uid_fk: int = 0
    lake_to_gloss_uid_fk: int = 0
    river_to_gloss_uid_fk: int = 0
    river_type: str = 'perrenial'
    avg_width_m: float
    avg_depth_m: float
    total_length_km: float
    drainage_basin_km: float = 0.0
    avg_velocity_m_per_h: float = 0.0
    gradient_m_per_km: float = 0.0
    hazards: str = ''
    features: str = ''

    navigation_type: str = 'none'
    flora_and_fauna: str = ''
    water_quality: str = ''
    historical_events: str = ''
    current_conditions: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["river_nm_gloss_uid_fk"],
            "FK": {"river_nm_gloss_uid_fk":
                   ("GLOSSARY", "gloss_uid_fk"),
                   "sea_to_gloss_uid_fk":
                   ("SEA", "sea_nm_gloss_uid_fk"),
                   "lake_to_gloss_uid_fk":
                   ("LAKE", "lake_nm_gloss_uid_fk"),
                   "river_to_gloss_uid_fk":
                   ("RIVER", "river_nm_gloss_uid_fk")},
            "CK": {"river_type":
                   ['perrenial', 'periodic', 'episodic',
                    'exotic', 'tributary', 'distributary',
                    'underground', 'aqueduct', 'canal',
                    'rapids', 'winding', 'stream',
                    'glacier'],
                   "navigation_type":
                   ["small craft", "large craft", "none"]},
            "JSON": ["river_course_points", "river_bank_points",
                     "hazards", "features"],
            "ORDER": ["river_nm_gloss_uid_fk ASC"]
        }


class RiverXMap(object):
    """
    Associative keys --
    - RIVERs (n) <--> MAPs (n)
    """

    tablename: str = "RIVER_X_MAP"
    river_nm_gloss_uid_fk: str
    map_nm_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["river_nm_gloss_uid_fk", "map_nm_fk"],
            "FK": {"river_nm_gloss_uid_fk":
                   ("RIVER", "river_nm_gloss_uid_fk"),
                   "map_nm_fk": ("MAP", "map_nm_pk")},
            "ORDER": ["river_nm_gloss_uid_fk ASC", "map_nm_fk ASC"]
        }


class WaterBody(object):
    """
    If it works out, may use this instead of LAKE.
    And maybe RIVER.
    But will keep them for now.
    This is intended to be used mainly
    for bodies of water associated with oceans or great lakes.
    """
    tablename: str = "WATER_BODY"
    body_nm_gloss_uid_pk: int
    body_shoreline_points: str
    is_coastal: bool = True
    is_frozen: bool = False
    body_type: str
    water_type: str
    tidal_influence: bool = False
    tidal_flows_per_day: int = 0
    avg_high_tide_m: float = 0.0
    avg_low_tide_m: float = 0.0
    max_high_tide_m: float = 0.0
    wave_type: str
    body_surface_area_m2: float
    body_surface_altitude_m: float
    max_depth_m: float
    avg_depth_m: float

    hazards: str = ''
    features: str = ''

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_gloss_uid_pk"],
            "FK": {"body_nm_gloss_uid_pk":
                   ("GLOSSARY", "gloss_uid_pk")},
            "CK": {"water_type": ['salinated', 'brackish', 'freshwater'],
                   "body_type":
                   ['fjord', 'sea', 'ocean', 'harbor',
                    'lagoon', 'bay', 'gulf', 'sound',
                    'bight', 'delta', 'estuary', 'strait',
                    'ice field', 'ice sheet', 'ice shelf',
                    'iceberg', 'ice floe', 'ice pack',
                    'roadstead', 'tidal pool',
                    'salt marsh'],
                   "wave_type":
                   ['low', 'medium', 'high', 'none']},
            "JSON": ["body_shoreline_points", "hazards", "features"],
            "ORDER": ["body_nm_gloss_uid_fk ASC"]
        }


class WaterBodyXMap(object):
    """
    Associative keys --
    - WATER_BODYs (n) <--> MAPs (n)
    """

    tablename: str = "WATER_BODY_X_MAP"
    body_nm_gloss_uid_fk: str
    map_nm_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_gloss_uid_fk", "map_nm_fk"],
            "FK": {"body_nm_gloss_uid_fk":
                   ("WATER_BODY", "body_nm_gloss_uid_fk"),
                   "map_nm_fk": ("MAP", "map_nm_pk")},
            "ORDER": ["body_nm_gloss_uid_fk ASC", "map_nm_fk ASC"]
        }


class WaterBodyXRiver(object):
    """
    Associative keys --
    - WATER_BODYs (n) <--> RIVERs (n)
    """

    tablename: str = "WATER_BODY_X_RIVER"
    body_nm_gloss_uid_fk: str
    river_nm_gloss_uid_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK":
            ["body_nm_gloss_uid_fk", "river_nm_gloss_uid_fk"],
            "FK": {"body_nm_gloss_uid_fk":
                   ("WATER_BODY", "body_nm_gloss_uid_fk"),
                   "river_nm_gloss_uid_fk":
                       ("RIVER", "river_nm_gloss_uid_fk")},
            "ORDER": ["body_nm_gloss_uid_fk ASC",
                      "river_nm_gloss_uid_fk ASC"]
        }


class LandBody(object):
    """
    Use this for geographic features that are not water.
    Including: continents, islands, geographic regions.
    """
    tablename: str = "LAND_BODY"
    body_nm_gloss_uid_pk: int
    body_shoreline_points: str
    body_landline_points: str
    body_type: str
    body_surface_area_m2: float
    body_surface_avg_altitude_m: float
    max_altitude_m: float
    min_altitude_m: float

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_gloss_uid_pk"],
            "FK": {"body_nm_gloss_uid_pk":
                   ("GLOSSARY", "gloss_uid_pk")},
            "CK": {"body_type": ['island', 'continent',
                                 'sub-continent', 'region'],
                   "wave_type": ['low', 'medium', 'high', 'none']},
            "JSON": ["body_shoreline_points",
                     "body_landline_points"],
            "ORDER": ["body_nm_gloss_uid_fk ASC"]
        }


class LandBodyXMap(object):
    """
    Associative keys --
    - LAND_BODYs (n) <--> MAPs (n)
    """

    tablename: str = "LAND_BODY_X_MAP"
    body_nm_gloss_uid_fk: str
    map_nm_fk: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_gloss_uid_fk", "map_nm_fk"],
            "FK": {"body_nm_gloss_uid_fk":
                   ("LAND_BODY", "body_nm_gloss_uid_fk"),
                   "map_nm_fk": ("MAP", "map_nm_pk")},
            "ORDER": ["body_nm_gloss_uid_fk ASC", "map_nm_fk ASC"]
        }


class LandBodyXLandBody(object):
    """
    Associative keys --
    - LAND_BODYs (n) <--> LAND_BODYs (n)
    - relation:
        - body 1 --> body 2
    """

    tablename: str = "LAND_BODY_X_LAND_BODY"
    body_nm_1_gloss_uid_fk: str
    body_nm_2_gloss_uid_fk: str
    body_relation_type: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_1_gloss_uid_fk",
                   "body_nm_2_gloss_uid_fk"],
            "FK": {"body_nm_1_gloss_uid_fk":
                   ("LAND_BODY", "body_nm_gloss_uid_fk"),
                   "body_nm_2_gloss_uid_fk":
                   ("LAND_BODY", "body_nm_gloss_uid_fk")},
            "CK": {"body_relation_type":
                   ['borders', 'overlaps',
                    'contains', 'contained by'],
                   "wave_type": ['low', 'medium', 'high', 'none']},
            "ORDER": ["body_nm_1_gloss_uid_fk ASC",
                      "body_nm_2_gloss_uid_fk ASC"]
        }


class LandBodyXWaterBody(object):
    """
    Associative keys --
    - LAND_BODYs (n) <--> WATER_BODYs (n)
    - relation:
        - body 1 --> body 2
    """

    tablename: str = "LAND_BODY_X_WATER_BODY"
    body_nm_1_gloss_uid_fk: str
    body_nm_2_gloss_uid_fk: str
    body_relation_type: str

    @classmethod
    def constraints(cls):
        return {
            "PK": ["body_nm_1_gloss_uid_fk",
                   "body_nm_2_gloss_uid_fk"],
            "FK": {"body_nm_1_gloss_uid_fk":
                   ("LAND_BODY", "body_nm_gloss_uid_fk"),
                   "body_nm_2_gloss_uid_fk":
                   ("WATER_BODY", "body_nm_gloss_uid_fk")},
            "CK": {"body_relation_type":
                   ['borders', 'overlaps',
                    'contains', 'contained by'],
                   "wave_type": ['low', 'medium', 'high', 'none']},
            "ORDER": ["body_nm_1_gloss_uid_fk ASC",
                      "body_nm_2_gloss_uid_fk ASC"]
        }


"""
Next:
- Define tables for:
    - GridTemplate
    - MapxGridTemplate
    - Various demographic tables and associations to
      each other and to Map tables, e.g.
      - species (sentients, animals, plants, etc.)\
      x languages
      X glossaries
      X continents
      X world sections
      X regions
      X lakes
      X rivers
      X canals
      X islands
      - roads
      - paths
      - trails
      - sea lanes
      - mountains
      - hills
      - mines
      - quarries
      - caverns
      - forests
      - undersea domains
      - populations
      - belief systems
      - countries (over time...)
      - federations
      - provinces
      - towns
      - counties, cantons and departments
      - towns
      - villages
      - estates and communes
      - tribal lands
      - neighborhoods and precincts
      - farms and fields
      - ruins
      - temples
      - scenes
      - buildings
        - etc.
    And before defining ALL of those tables, do a few, then
    make sure the actual database generation works as well as
    the SQL generation.  Review the astronomical algorithms in
    light of these new structures. Generate calendars, lunar
    and planetary charts, and so on; and store results in DB
    instead of files.
    Then do some more work on generating displays in the GUI.
    After a solid iteration, then come back and do more tables,
    more content-generation alogrithms, and so on.
"""


class InitGameDatabase(object):
    """Methods to:
    - Create set of SQL files to manage the game database.
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
        for model in [Backup,
                      Universe, ExternalUniv,
                      GalacticCluster, Galaxy, StarSystem, World, Moon,
                      Map, MapXMap, Grid, GridXMap,
                      CharSet, CharMember,
                      LangFamily, Language, LangDialect,
                      Glossary,
                      Lake, LakeXMap, River, RiverXMap,
                      WaterBody, WaterBodyXMap, WaterBodyXRiver,
                      LandBody, LandBodyXMap, LandBodyXLandBody,
                      LandBodyXWaterBody]:
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
                      p_col: int,
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
        for t in [Display.DASH16,
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
        for t in [Display.DASH16,
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
        for t in [Display.DASH16,
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
            rec['txt'] = Display.DASH16
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
        rec["txt"] = Display.DASH16
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
            attr = {k: v for k, v in p_attr["movement"].items()
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
        - p_attr (dict): 'map' data for the "Saskan Lands"
        region from the saskan_geo.json file.
        :sets:
        - self.G_CELLS['map']: map km dimensions and scaling factors
        - Get km dimensions for entire map rectangle
        - Reject maps that are too big
        - Divide g km by m km to get # of grid-cells for map box
            - This should be a float.
        - Multiply # of grid-cells in the map box by
        px per grid-cell
          to get line height and width in px for the map box.
        - Center 'map' in the 'grid'; by grid count, by px
        @DEV:
        - Assignment of km to grid dimensions should not be
        hard-coded.
        - We need to have a `grids` database table that provides
          different dimensions for different scenarios, just
          like we have the `maps` table to define "location" of
          maps.
        - Once that is in place, then "mapping" between grid
        and map can be abstracted into a class like this one,
        or in the saskan_math module.
        """
        err = ""
        map = {'ln': dict(),
               'cl': dict()}
        # Evaluate map line lengths in kilometers
        map['ln']['km'] =\
            {'w': round(int(p_attr["distance"]["width"]["amt"])),
             'h': round(int(p_attr["distance"]["height"]["amt"]))}
        if map['ln']['km']['w'] > Display.G_LNS_KM_W:
            err = f"Map km w {map['w']} > grid km w {Display.G_LNS_KM_W}"
        if map['ln']['km']['h'] > Display.G_LNS_KM_H:
            err = f"Map km h {map['h']} > grid km h {Display.G_LNS_KM_H}"
        if err != "":
            raise ValueError(err)
        # Verified that the map rect is smaller than the grid rect.
        # Compute a ratio of map to grid.
        # Divide map km w, h by grid km w, h
        map['ln']['ratio'] =\
            {'w': round((map['ln']['km']['w'] / Display.G_LNS_KM_W), 4),
             'h': round((map['ln']['km']['h'] / Display.G_LNS_KM_H), 4)}
        # Compute map line dimensions in px
        # Multiply grid line px w, h by map ratio w, h
        map['ln']['px'] =\
            {'w': int(round(Display.G_LNS_PX_W * map['ln']['ratio']['w'])),
             'h': int(round(Display.G_LNS_PX_H * map['ln']['ratio']['h']))}
        # The map rect needs to be centered in the grid rect.
        #  Compute the offset of the map rect from grid rect.
        #  Compute topleft of the map in relation to topleft of
        # the grid.
        #  The map top is offset from grid top by half the px
        # difference
        #  between grid height and map height.
        #  The map left is offset from grid left by half the
        #  difference
        #  between grid width and map width.
        # And then adjusted once more for the offset of the
        # grid from the window.
        map['ln']['px']['left'] =\
            int(round((Display.G_LNS_PX_W - map['ln']['px']['w']) / 2) +
                Display.GRID_OFFSET_X)
        map['ln']['px']['top'] =\
            int(round((Display.G_LNS_PX_H - map['ln']['px']['h']) / 2) +
                (Display.GRID_OFFSET_Y * 4))
        self.G_CELLS["map"] = map

    def set_map_grid_collisions(self):
        """ Store collisions between G_CELLS and 'map' box.
        """
        cells = {k: v for k, v in self.G_CELLS.items() if k != "map"}
        for ck, crec in cells.items():
            self.G_CELLS[ck]["is_inside"] = False
            self.G_CELLS[ck]["overlaps"] = False
            if SaskanRect.rect_contains(
                    self.G_CELLS["map"]["box"], crec["box"]):
                self.G_CELLS[ck]["is_inside"] = True
            elif SaskanRect.rect_overlaps(
                    self.G_CELLS["map"]["box"], crec["box"]):
                self.G_CELLS[ck]["overlaps"] = True

    # Set "map" dimensions and other content in G_CELLS
    # =================================================
    def set_gamemap_dims(self,
                         p_attr: dict):
        """This method handles placing/creating/drawing map
        displays
           over the "grid" on the GAMEMAP Display.
        :attr:
        - p_attr (dict): game map name-value pairs from geo
        config data
            For example, 'map' data for the "Saskan Lands"
            region from the saskan_geo.json file.

        - Compute ratio, offsets of map to g_ width & height.
        - Define saskan rect and pygame box for the map
        - Do collision checks between the map box and grid cells
        """
        self.compute_map_scale(p_attr)
        map_px = self.G_CELLS["map"]["ln"]["px"]
        self.G_CELLS["map"]["s_rect"] =\
            SaskanRect.set_rect(map_px["top"], map_px["left"],
                                 map_px["w"], map_px["h"])
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
