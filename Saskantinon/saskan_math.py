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
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401
from pygame import Rect

from io_data import GameRect


class SaskanRect(object):
    """Manage extended rectangle functions, wrapping the pygame.Rect class.

    - Create and modify rectangles and specify their attributes
    - Check for containment
    - Check for intersections (overlap, collision)
    - Check for adjacency (clipline)
    - Check for equality
    """

    def __init__(self):
        """Initialize a Saskan rectangle object.

        For matplotlib.patches.Rectangle and colors:
        See: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html   # noqa: E501
        and https://matplotlib.org/stable/tutorials/colors/colors.html
        """
        self.game_rect: GameRect

    def make_rect(self,
                  p_top: float,
                  p_left: float,
                  p_width: float,
                  p_height: float,
                  p_line_width: float = 0.0,
                  p_fill: bool = False,
                  p_fill_color=None,
                  p_line_color=None):
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
          Color definitions must be from pygame.Color.
          See io_data.Colors

        :sets: (GameRect) proprietary rectangle data structure, with pygame
          Rect object referenced by "box" key
        N.B.:
        - Order of arguments is y, x, w, h, not x, y, w, h.

        """
        self.rect = {
            'bottom': p_top + p_height,
            'right': p_left + p_width,
            'h': p_height,
            'w': p_width,
            't': p_top,
            'y': p_top,
            'l': p_left,
            'x': p_left,
            'b': p_top + p_height,
            'r': p_left + p_width,
            'top_left': (p_left, p_top),
            'top_right': (p_left + p_width, p_top),
            'bottom_left': (p_left, p_top + p_height),
            'bottom_right': (p_left + p_width, p_top + p_height),
            'center': (p_left + p_width / 2.0, p_top + p_height / 2.0),
            'center_w': p_width / 2.0,
            'center_x': p_width / 2.0,
            'center_h': p_height / 2.0,
            'center_y': p_height / 2.0,
            'fill': p_fill,
            'fill_color': p_fill_color,
            'line_width': p_line_width,
            'line_color': p_line_color,
            'box': Rect((p_left, p_top), (p_width, p_height))
        }

    def rect_contains(self,
                      p_box_a: Rect,
                      p_box_b: Rect) -> bool:
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
                      p_box_a: Rect,
                      p_box_b: Rect) -> bool:
        """Determine if rectangle A and rectangle B overlap.
        use pygame colliderect
        :args:
        - p_box_a: (pygame.Rect) rectangle A
        - p_box_b: (pygame.Rect) rectangle B
        """
        if p_box_a.colliderect(p_box_b):
            return True
        else:
            return False

    def rect_borders(self,
                     p_rect_a: Rect,
                     p_rect_b: Rect) -> bool:
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
                  p_rect_a: Rect,
                  p_rect_b: Rect) -> bool:
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
