#!python
"""
:module:    saskan_math.py

:author:    GM (genuinemerit @ pm.me)

:classes:
- SaskanRect - Manage extended rectangle functions, buidling on pygame.Rect
- SaskanMath - Game-related conversions and calculations

Transforms, conversions, calculations, algorithms useful to the game,
including use of game units and terminology.

Units are as follows unless otherwise noted:
- distance => kilometers, or gigaparsecs
- mass => kilograms
- day => 1 rotation of planet Gavor
- year a/k/a turn => 1 orbit of Gavor around its star, Faton
- rotation => multiple or fraction of Gavoran days; or galactic seconds
- orbit => revolution of Gavor around Faton:
    multiple, fractional Gavoran years (turns); or galactic seconds
"""

# import matplotlib.colors as mColors

from dataclasses import dataclass   # fields
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401
from pygame import Rect


class SaskanRect(object):
    """Manage extended rectangle functions, buidling on the pygame.Rect class.

    - Create and modify rectangles
        - top, left, bottom, right
        - width, height
        - top_left, top_right, bottom_left, bottom_right
        - center
    - Check for intersections
    - Check for containment
    - Check for adjacency
    - Check for equality
    - Check for overlap/collision
    """

    def __init__(self):
        """Initialize a Saskan rectangle object.

        For matplotlib.patches.Rectangle and colors:
        See: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html   # noqa: E501
        and https://matplotlib.org/stable/tutorials/colors/colors.html
        """
        self.rect = {
            "bottom": 0.0,
            "right": 0.0,
            "h": 0.0,
            "w": 0.0,
            "t": 0.0,
            "y": 0.0,
            "l": 0.0,
            "x": 0.0,
            "b": 0.0,
            "r": 0.0,
            "top_left": (0.0, 0.0),      # (x, y)
            "top_right": (0.0, 0.0),     # (x, y)
            "bottom_left": (0.0, 0.0),   # (x, y)
            "bottom_right": (0.0, 0.0),  # (x, y)
            "center": (0.0, 0.0),        # (x, y)
            "center_w": 0.0,             # (x)
            "center_x": 0.0,             # (x)
            "center_h": 0.0,             # (y)
            "center_y": 0.0,             # (y)
            "fill": False,
            "fill_color": None,
            "line_width": 0.0,
            "line_color": None,
            "box": None     # Pygame Rect
        }

    def make_rect(self,
                  p_top: float,
                  p_left: float,
                  p_width: float,
                  p_height: float,
                  p_line_width: float = 0.0,
                  p_fill: bool = False,
                  p_fill_color=None,
                  p_line_color=None) -> dict:
        """Create a rectangle from top, left, width, height.
        Units are in whatever coordinate system makes sense, such as,
        pixels, meters, kilometers, etc. This class makes no assumptions
        about what the units represent.
        :args:
        - top: (float) top of rectangle (y)
        - left: (float) left of rectangle (x)
        - width: (float) width (w) of rectangle
        - height: (float) height (h) of rectangle
        - line_width: (float) width of rectangle border
        - fill: (bool) fill the rectangle with color, default False
        - fill_color: (matplotlib.colors) color to fill rectangle
        - line_color: (matplotlib.colors) color of rectangle border
        :return: (dict) proprietary rectangle data structure, with pygame
          Rect object referenced by "box" key

        N.B.:
        - Order of arguments is y, x, w, h, not x, y, w, h.

        Color definitions are pygame colors, as defined in pygame.Color.
        :args:
        - top: (float) top of rectangle (y)
        - left: (float) left of rectangle (x)
        - width: (float) width (w) of rectangle
        - height: (float) height (h) of rectangle
        - line_width: (float) width of rectangle border
        - fill: (bool) fill the rectangle with color, default False
        - fill_color: (matplotlib.colors) color to fill rectangle
        - line_color: (matplotlib.colors) color of rectangle border
        :return: (dict) rectangle data structure
        """
        self.rect["top"] = self.rect["t"] = self.rect["y"] = p_top
        self.rect["left"] = self.rect["l"] = self.rect["x"] = p_left
        self.rect["width"] = self.rect["w"] = p_width
        self.rect["height"] = self.rect["h"] = p_height
        self.rect["bottom"] = self.rect["b"] = p_top + p_height
        self.rect["right"] = self.rect["r"] = p_left + p_width
        self.rect["top_left"] = (p_left, p_top)                 # (x, y)
        self.rect["top_right"] = (self.rect["right"], p_top)
        self.rect["bottom_left"] = (p_left, self.rect["bottom"])
        self.rect["bottom_right"] = (self.rect["right"], self.rect["bottom"])
        self.rect["fill"] = p_fill
        if p_fill_color is not None:
            self.rect["fill_color"] = p_fill_color
        if p_line_width > 0.0:
            self.rect["line_width"] = p_line_width
            if p_line_color is not None:
                self.rect["line_color"] = p_line_color
        self.rect["center_w"] = self.rect["center_x"] = p_width / 2.0
        self.rect["center_h"] = self.rect["center_y"] = p_height / 2.0
        self.rect["center"] = (self.rect["center_x"], self.rect["center_y"])
        # This is the pygame rectangle:
        self.rect["box"] = Rect((p_left, p_top), (p_width, p_height))
        return self.rect

    def rect_contains(self,
                      p_box_a: Rect,
                      p_box_b: Rect) -> bool:
        """Determine if rectangle A contains rectangle B.
        use pygame contains
        """
        if p_box_a.contains(p_box_b):
            return True
        else:
            return False

    def rect_overlaps(self,
                      p_box_a: Rect,
                      p_box_b: Rect) -> bool:
        """Determine if rectangle A and rectangle B overlap.
        use pygame colliderect
        """
        if p_box_a.colliderect(p_box_b):
            return True
        else:
            return False

    def rect_borders(self, p_rect_a: dict, p_rect_b: dict) -> tuple:
        """Determine if rectangle A and rectangle B share a border.
        use pygame clipline
        """
        pass


class SaskanMath(object):
    """Class for game-related conversions and calculations.
       Includes templates for map grids.
    """
    def __init__(self):
        """Manage measurements and conversion relevant to
        context of the game. This includes both real world
        units as well as some unique to the 'saskan' game world.
        """
        pass

    @dataclass
    class GEOM():
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
        BX = "box"
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

    @dataclass
    class GEOG():
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

    @dataclass
    class ASTRO():
        """ Astronomical and physics units and conversions.
        """
        # mass, matter
        DE = "dark energy"
        DM = "dark matter"
        BM = "baryonic matter"
        SMS = "solar mass"
        # objects, astronomical
        BH = "black hole"
        GG = "galaxy"
        GB = "galactic bulge"
        GC = "galactic cluster"
        GH = "galactic halo"
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
        DEP = 0.683                 # dark energy percentage
        DMP = 0.274                 # dark matter percentage
        BMP = 0.043                 # baryonic matter percentage
        TUV = 415000             # total univ volume in cubic gigalight years
        TUK = 1.5e53             # total universe mass in kg
        UNA = 13.787e9           # age of universe in Gavoran years (turns)
        TUE = 73.3               # expansion rate of universe in km/s per Mpc
        # conversions -- all are multiplicative in the indicated direction
        # AA_TO_BB, so AA -> BB as AA * AA_TO_BB = BB
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

    @dataclass
    class MAP():
        """Map/grid template dimensions
        grid template names refer to its mathematical character.
        For example, km_43.75_sq has square grids that are 43.75
        km per side, a template I like to use to represent a
        region-level map.

        map template names refer to a specific use of a grid,
        providing its:
        - either a grid_type or another map_name
        - its name as the index
        - North-West corner in degrees
        - its grid sizes in degrees
        - its height and width in grid units
        - if it is a sub-map (a map_name rather than a grid_type
          is used), then provide grids offset from top
          and from left of the parent map, along with grid w and
          h, but omit degree info.
        - Use decimal values to get finer-grained placements

        This fits better in the saskan_game.py module and in config
        data. See GameData class in saskan_game and saskan_geo config data.
        """
        grids = {"km_43.75":
                 {"_name": "region",
                  "_type": "square",
                  "grid_km": 43.75}}
        maps = {"saskan_grid":
                {"grid_id": "km_43.75",
                 "edge_dg": {"N": 37.69, "W": -106.66},
                 "grid_dg": {"EW": 0.397, "NS": 0.393},
                 "grid_cnt": {"h": 30, "w": 40}},
                "Borded Federation":
                {"parent_nm": "saskan_grid",
                 "grid_cnt": {"h": 10, "w": 12},
                 "grid_off": {"l": 3, "t":3}},
                "Borded":
                {"parent_nm": "Borded Federation",
                 "grid_cnt": {"h": 0.4, "w": 0.5},
                 "grid_off": {"l": 5, "t": 3}}}

    def dec_to_pct(self, p_decimal: float) -> str:
        """Convert decimal to percentage.
        """
        dec = float(p_decimal)
        pct = f'{round(dec * 100, 5):,}' + " %"
        return pct

    def pct_to_dec(self, p_percent: str) -> float:
        """Convert percentage to decimal factor.
        """
        pct_s = str(p_percent).replace("%", "").strip()
        pct_d = round(float(pct_s) / 100, 5)
        return pct_d

    def diam_to_radius(self, p_diameter: float) -> float:
        """Convert diameter to radius.
        """
        radius = float(p_diameter) / 2
        return radius

    def radius_to_diam(self, p_radius: float) -> float:
        """Convert radius to diameter.
        """
        diam = round(float(p_radius) * 2, 5)
        return diam

    def grams_to_kilos(self,
                       p_grams: float,
                       p_round: bool = True) -> float:
        """Convert grams to kilos."""
        if p_round:
            kilos = round(float(p_grams) * 0.001, 5)
        else:
            kilos = float(p_grams) * 0.001
        return kilos

    def kilos_to_grams(self,
                       p_kilos: float) -> float:
        """Convert kilos to grams."""
        grams = round(float(p_kilos) * 1000, 5)
        return grams

    def kilos_to_pounds(self,
                        p_kilos: float) -> float:
        """Convert kilos to pounds."""
        pounds = round(float(p_kilos) * 2.20462262185, 5)
        return pounds

    def pounds_to_kilos(self,
                        p_pounds: float) -> float:
        """Convert pounds to kilos."""
        kilos = round(float(p_pounds) * 0.45359237, 5)
        return kilos

    def pounds_to_oz(self,
                     p_pounds: float) -> float:
        """Convert pounds to ounces."""
        oz = round(float(p_pounds) * 16, 5)
        return oz

    def oz_to_pounds(self,
                     p_oz: float) -> float:
        """Convert ounces to pounds."""
        pounds = round(float(p_oz) / 16, 5)
        return pounds

    def oz_to_grams(self,
                    p_oz: float) -> float:
        """Convert ounces to grams."""
        grams = float(p_oz) * 28.349523125
        return grams

    def grams_to_oz(self,
                    p_grams: float) -> float:
        """Convert grams to ounces."""
        oz = round(float(p_grams) * 0.03527396195, 5)
        return oz

    def kilos_to_sm(self,
                    p_kilos: float,
                    p_round: bool = True) -> float:
        """Convert kilos to solar mass."""
        if p_round:
            sm = round(float(p_kilos) * 5.97219e-31, 5)
        else:
            sm = float(p_kilos) * 5.97219e-31
        return sm

    def sm_to_kilos(self,
                    p_sm: float) -> float:
        """Convert solar mass to kilos."""
        kilos = round(float(p_sm) * 1.98847e+30, 5)
        return kilos

    def cm_to_inches(self,
                     p_cm: float) -> float:
        """Convert centimeters to inches."""
        inches = round(float(p_cm) * 0.3937007874, 5)
        return inches

    def inches_to_cm(self,
                        p_inches: float) -> float:
        """Convert inches to centimeters."""
        cm = round(float(p_inches) * 2.54, 5)
        return cm

    def ft_to_meters(self,
                     p_ft: float) -> float:
        """Convert feet to meters."""
        meters = round(float(p_ft) * 0.3048, 5)
        return meters

    def meters_to_ft(self,
                     p_meters: float) -> float:
        """Convert meters to feet."""
        ft = round(float(p_meters) * 3.280839895, 5)
        return ft

    def ft_to_inches(self,
                     p_ft: float) -> float:
        """Convert feet to inches."""
        inches = round(float(p_ft) * 12, 5)
        return inches

    def inches_to_ft(self,
                     p_inches: float,
                     p_round: bool=True) -> float:
        """Convert inches to feet."""
        if p_round:
            ft = round(float(p_inches) * 0.08333333333, 5)
        else:
            ft = float(p_inches) * 0.08333333333
        return ft

    def cm_to_meters(self,
                     p_cm: float,
                     p_round: bool=True) -> float:
        """Convert centimeters to meters."""
        if p_round:
            meters = round(float(p_cm) * 0.01, 5)
        else:
            meters = float(p_cm) * 0.01
        return meters

    def meters_to_cm(self,
                     p_meters: float,
                     p_round: bool=True) -> float:
        """Convert meters to centimeters."""
        if p_round:
            cm = round(float(p_meters) * 100, 5)
        else:
            cm = float(p_meters) * 100
        return cm

    def cm_to_mm(self,
                 p_cm: float,
                    p_round: bool=True) -> float:
        """Convert centimeters to millimeters."""
        if p_round:
            mm = round(float(p_cm) * 10, 5)
        else:
            mm = float(p_cm) * 10
        return mm

    def km_to_mi(self,
                 p_km: float,
                 p_round: bool=True) -> float:
        """Convert kilometers to miles."""
        if p_round:
            mi = round(float(p_km) * 0.62137119223733, 5)
        else:
            mi = float(p_km) * 0.62137119223733
        return mi

    def km_to_ka(self,
                 p_km: float,
                 p_round: bool=True) -> float:
        """Convert kilometers to katas,
        a game world measurement where 1 kata = 0.256 km."""
        if p_round:
            ka = round(float(p_km) / 0.256, 5)
        else:
            ka = float(p_km) / 0.256
        return ka

        # GAWO_TO_KM = 1.024           # gawos -> kilometers

    def km_to_ga(self,
                 p_km: float,
                 p_round: bool=True) -> float:
        """Convert kilometers to gawos,
        a game world measurement where 1 gawo = 1.024 km."""
        if p_round:
            ga = round(float(p_km) / 1.024, 5)
        else:
            ga = float(p_km) / 1.024
        return ga

    # carrry on adding these simple functions as needed,
    # but do it when they are needed, 'cuz this is f'n boring

        # IN_TO_MM = 25.4              # inches -> millimeters
        # MM_TO_IN = 0.03937007874     # millimeters -> inches
        # CM_TO_MM = 10.0              # centimeters -> millimeters
        # MM_TO_CM = 0.1               # millimeters -> centimeters
        # KM_TO_M = 1000.0             # kilometers -> meters
        # M_TO_KM = 0.001              # meters -> kilometers

        # MI_TO_NM = 0.868976242       # miles -> nautical miles
        # NM_TO_MI = 1.150779448       # nautical miles -> miles
        # MI_TO_KM = 1.609344          # miles -> kilometers
        # KM_TO_NM = 0.539956803       # kilometers -> nautical miles
        # NM_TO_KM = 1.852             # nautical miles -> kilometers

        # distance - saskan/metric
        # come up with something smaller than a nob, say, a pik
        # CM_TO_NOB = 0.64             # centimeters -> nobs
        # GAWO_TO_MI = 0.636           # gawos -> miles
        # GAWO_TO_KATA = 4.0           # gawos -> kata
        # GAWO_TO_KM = 1.024           # gawos -> kilometers
        # GAWO_TO_M = 1024.0           # gawos -> meters
        # IN_TO_NOB = 2.56             # inches -> nobs
        # KATA_TO_KM = 0.256           # kata -> kilometers
        # KATA_TO_M = 256.0            # kata -> meters
        # KATA_TO_MI = 0.159           # ktaa -> miles
        # KATA_TO_THWAB = 4.0          # kata -> thwabs
        # M_TO_NOB = 64.0              # meters -> nobs
        # M_TO_THWAB = 0.015625        # meters -> thwabs (1/64th)
        # MM_TO_NOB = 0.0064           # millimeters -> nobs
        # NOB_TO_CM = 1.5625           # nobs -> centimeters
        # NOB_TO_IN = 0.390625         # nobs -> inches
        # NOB_TO_MM = 156.25           # nobs -> millimeters
        # THWAB_TO_KATA = 0.25         # thwabs -> kata
        # THWAB_TO_M = 64.0            # thwabs -> meters
        # THWAB_TO_TWA = 64.0          # thwabs -> twas
        # TWA_TO_M = 1.00              # twas -> meters
        # TWA_TO_NOB = 64.0            # twas -> nobs
        # TWA_TO_THWAB = 0.015625      # twas -> thwabs (1/64th)
        # YUZA_TO_GABO = 4.0           # yuzas -> gabos
        # YUZA_TO_KM = 4.096           # yuzas -> kilometers
        # YUZA_TO_M = 4096.0           # yuzas -> meters
        # YUZA_TO_MI = 2.545           # yuzas -> miles

    def collision_2d_rect(self,
                          p_rect1: Rect,
                          p_rect2: Rect) -> bool:
        """Collision detection for 2d rectangles."""
        pass
