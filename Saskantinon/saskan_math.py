#!python
"""
:module:    saskan_math.py

:author:    GM (genuinemerit @ pm.me)

Transforms, conversions, calculations useful to the game,
including use of game units and terminology.
"""

import math
import json
import pickle

from dataclasses import dataclass   # fields
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401


class SaskanMath(object):
    """Class for game-related conversions and calculations.
       Includes templates for map grids.
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
        self.S_MAP: dict = dict()

    @dataclass
    class M():
        """Names of measurements assigned to a meaningful
        variable or abbreviation.
        """
        # math, geometry, currency
        AR = "area"
        DC = "decimal"
        DI = "diameter"
        INT = "integer"
        PCT = "percent"
        RD = "radius"
        VL = "volume"
        # weight
        GM = "grams"
        KG = "kilograms"
        LB = "pounds"
        OZ = "ounces"
        # mass
        BA = "baryonic"
        MS = "mass"
        SM = "solar mass"
        # distance & area, metric, imperial, saskan
        CM = "centimeters"
        FT = "feet"
        GAWO = "gawos"
        IN = "inches"
        KATA = "katas"
        KM = "kilometers"
        M = "meters"
        M2 = "square meters"
        M3 = "cubic meters"
        MI = "miles"
        MM = "millimeters"
        NM = "nautical miles"
        NOB = "nobs"
        THWAB = "thwabs"
        TWA = "twas"
        YUZA = "yuzas"
        # distance, geographical
        DGLAT = "degrees latitude"
        DGLONG = "degrees longitude"
        # direction
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
        # distance and area, astronomical
        AU = "astronomical units"
        GLY = "gigalight years"
        GLY2 = "square gigalight years"
        GLY3 = "cubic gigalight years"
        GPC = "gigaparsec"
        GPC2 = "square gigaparsecs"
        GPC3 = "cubic gigaparsecs"
        KPC = "kiloparsec"
        LM = "light minutes"
        LS = "light seconds"
        LY = "light years"
        LY2 = "square light years"
        LY3 = "cubic light years"
        MPC = "megaparsec"
        PC = "parsec"
        TU = "total universe"

    @dataclass
    class C():
        """Values used to do various computations using
        a variety of units and formulae.
        """
        # math, geometry, currency
        # Fill in using real and game currenncies
        # distance - metric/imperial
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
        # distance - saskan/metric
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
        # distance, geographical to metric
        DGLAT_TO_KM = 111.2           # degree of latitutde -> kilometers
        DGLONG_TO_KM = 111.32         # degree of longitude -> kilometers
        KM_TO_DGLAT = 0.00898315284   # kilometers -> degree of latitude
        KM_TO_DGLONG = 0.00898311175  # kilometers -> degree of longitude
        # astronomical units
        AU_TO_KM = 1.495979e+8        # astronomical units -> km
        AU_TO_LM = 5.2596e+16         # astro units -> light minutes
        AU_TO_LS = 0.002004004004     # astro units -> light seconds
        AU_TO_LY = 0.00001581250799   # astro units -> light years
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
        LY_TO_LM = 52596000000000000  # light years -> light minutes
        LY_TO_PC = 0.30659817672196   # light years -> parsecs
        LY_TO_GLY = 1e-9              # light years -> gigalight years
        GLY_TO_LY = 1e+9              # gigalight years -> light years
        MPC_TO_GPC = 0.001            # megaparsecs -> gigaparsecs
        MPC_TO_KPC = 1000.0           # megaparsecs -> kiloparsecs
        PC_TO_KPC = 0.001             # parsecs -> kiloparsecs
        PC_TO_LY = 3.261598           # parsecs -> light years

    @dataclass
    class MAP():
        """Map/grid template dimensions
        The template names refer to the grid size in kilometers.
        For example, m_4375 has grids that are 43.75 km-sq.
        """
        grids = {"m_4375":
                 {"edge_dg": {"N": 37.69, "W": -106.66},
                  "grid_dg": {"NS": 0.393, "EW": 0.397},
                  "grid_km": 43.75}}

    # Consider putting all my transforms into a separate class.
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
                       p_rounding: bool = True) -> float:
        """Convert grams to kilos."""
        if p_rounding:
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
                    p_rounding: bool = True) -> float:
        """Convert kilos to solar mass."""
        if p_rounding:
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
                     p_rounding: bool=True) -> float:
        """Convert inches to feet."""
        if p_rounding:
            ft = round(float(p_inches) * 0.08333333333, 5)
        else:
            ft = float(p_inches) * 0.08333333333
        return ft

    def cm_to_meters(self,
                     p_cm: float,
                     p_rounding: bool=True) -> float:
        """Convert centimeters to meters."""
        if p_rounding:
            meters = round(float(p_cm) * 0.01, 5)
        else:
            meters = float(p_cm) * 0.01
        return meters

    def meters_to_cm(self,
                     p_meters: float,
                     p_rounding: bool=True) -> float:
        """Convert meters to centimeters."""
        if p_rounding:
            cm = round(float(p_meters) * 100, 5)
        else:
            cm = float(p_meters) * 100
        return cm

    def cm_to_mm(self,
                 p_cm: float,
                    p_rounding: bool=True) -> float:
        """Convert centimeters to millimeters."""
        if p_rounding:
            mm = round(float(p_cm) * 10, 5)
        else:
            mm = float(p_cm) * 10
        return mm

    # carrry on adding these simple functions as needed,
    # but do it when they are needed...

        # IN_TO_MM = 25.4              # inches -> millimeters
        # MM_TO_IN = 0.03937007874     # millimeters -> inches
        # CM_TO_MM = 10.0              # centimeters -> millimeters
        # MM_TO_CM = 0.1               # millimeters -> centimeters
        # KM_TO_M = 1000.0             # kilometers -> meters
        # M_TO_KM = 0.001              # meters -> kilometers

        # MI_TO_NM = 0.868976242       # miles -> nautical miles
        # NM_TO_MI = 1.150779448       # nautical miles -> miles
        # KM_TO_MI = 0.62137119223733  # kilometers -> miles
        # MI_TO_KM = 1.609344          # miles -> kilometers
        # KM_TO_NM = 0.539956803       # kilometers -> nautical miles
        # NM_TO_KM = 1.852             # nautical miles -> kilometers

        # distance - saskan/metric
        # come up with something smaller than a nob, say, a pik
        # CM_TO_NOB = 0.64             # centimeters -> nobs
        # GABO_TO_MI = 0.636           # gabos -> miles
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
