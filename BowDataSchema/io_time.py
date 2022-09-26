#!python
"""
:module:    io_time.py

:author:    GM (genuinemerit @ pm.me)

This class prototypes definitions of astronomical events
in a game world's local star system. It define calendars
for the passage of time, including era, epoch, year,
season, month, day, noon, midnight, sunrise, sunset,
phases of two moons, timing of planetary conjunctions.
All are from perspective of a single time zone that
encompasses the lands of the game, spread over about 1,600
square kilometers.

All values are hard-coded in this class for now.
Once that is working, abstract static values into config
class or file. Smaller time increments may also be defined.
Consider for example something like the 3.333 second
division of an hour in the Hebrew calendar.

@DEV - Rebuild saskan conda venv using lessons leearned
from work on the home-finance app. Use latest version of
python and pandas. Consider switching to pygame.
"""

import pickle
# import random

# from copy import copy
from dataclasses import dataclass   # fields
from os import path
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_config import ConfigIO          # type: ignore
from io_file import FileIO              # type: ignore
from io_redis import RedisIO            # type: ignore

CI = ConfigIO()
FI = FileIO()
RI = RedisIO()


class TimeIO(object):
    """Class for Calendar-related data and methods.
    """
    def __init__(self,
                 p_file_nm: str):
        """Class for managing time, calendar and
        astronomical data. Store data in a pickled
        dictionary, CALENDAR_DB.

        How to:
        - Save the CALENDAR_DB pickle:
            self.set_time_data()

        :args: p_save_nm: str
            - Generic name of where time data object saved
            - Example: "time_data"
        """
        self.file_nm = path.join(RI.get_app_path(),
                                 RI.get_cfg_val(
                                     'save_path'),
                                 p_file_nm)
        with open(self.file_nm +
                  "_calendar.pickle", 'rb') as f:
            self.CALENDAR_DB = pickle.load(f)

    @dataclass
    class COLOR:
        """Define CLI colors."""
        BLUE = '\033[94m'
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        END = '\033[0m'
        GREEN = '\033[92m'
        PURPLE = '\033[95m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        UNDERLINE = '\033[4m'

    @dataclass
    class CAL:
        """Define static compoment of CALENDAR_DB.
        Initialize the time dictionary if one does not yet
        exist.  For example, to start a new one, or to
        wipe the current one and start a new one.

        These materials should remain immutable.
        Eventually move this to an external config file.

        All value units as follows unless otherwise noted:
        - distance => kilometers
        - mass => kilograms
        - day => 1 rotation of planet Gavor
        - year => 1 orbit of Gavor around its star, Faton
        - rotation => multiple or fraction of Gavoran days
        - orbit => revolution of Gavor around Faton:
           multiple, fractional Gavoran years

        Define objects by describing a container name,
        which references another object type, then each of
        the objects within that container. For example,
        planets are contained in a star; moons are
        contained in a planet.
        """
        STARS: dict = {
            "Galactic Center": {
                "Faton": {"diameter": 1.390473e+6,
                          "rotation": 36.0,
                          "type": "G-type main-seq star",
                          "mass": 2.10e30}
                }
            }
        PLANETS: dict = {
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
        MOONS: dict = {
            "Gavor": {
                "Endor": {"orbit": 32.1,
                          "mass": 1.00346e23},
                "Sella": {"orbit": 23.5,
                          "mass": 0.53779e23}}}
        SEASON: dict = {
            "winter": {
                "days": 91.75,
                "events": [{"day": 1,
                            "name": "solstice"},
                           {"day": 45.75,
                            "name": "midwinter"}]},
            "spring": {
                "days": 91.75,
                "events": [{"day": 1, "name": "equinox"}]},
            "summer": {
                "days": 91.75,
                "events": [{"day": 1, "name": "solstice"},
                           {"day": 45.75,
                            "name": "midsummer"}]},
            "autumn": {
                "days": 91.75,
                "events": [{"day": 1, "name": "equinox"}]}}
        CALENDAR: dict = {
            "AG": {"name": "Astro-Gavorian",
                   "type": "[solar, arithmetic]",
                   "day_start": "noon"},
            "LAG": {"name": "Long Astro-Gavorian",
                    "type": "[solar, arithmetic]",
                    "day_start": "noon"},
            "SAG": {"name": "Short Astro- Gavorian",
                    "type": "[solar, arithmetic]",
                    "day_start": "noon"},
            "Juuj": {"name": "Juujian",
                     "type": "[solar, arithmetic]",
                     "day_start": "noon"},
            "Beshq": {"name": "Beshquoise",
                      "type": "[solar, arithmetic]",
                      "day_start": "noon"},
            "Bye": {"name": "Byenungik",
                    "type": "[solar, arithmetic]",
                    "day_start": "noon"},
            "Nye": {"name": "Nyelik",
                    "type": "[solar, arithmetic]",
                    "day_start": "noon"},
            "Mobal": {"name": "Mobalbeqan",
                      "type": "[solar, arithmetic]",
                      "day_start": "noon"},
            "Settan": {"name": "Settan",
                       "type": "[solar, arithmetic]",
                       "day_start": "sunset"},
            "Ter": {"name": "Terrapin",
                    "type": "[solar, arithmetic]",
                    "day_start": "sunrise"},
            "Jack": {"name": "Jackalope",
                     "type": "[solar, arithmetic]",
                     "day_start": "sunrise"},
            "K'kol": {"name": "Kahilakol",
                      "type": "[solar, arithmetic]",
                      "day_start": "midnight"},
            "K'beq": {"name": "Kahilabeq",
                      "type": "[solar, arithmetic]",
                      "day_start": "midnight"},
            "Empa": {"name": "Empafarasi",
                     "type": "[solar, arithmetic]",
                     "day_start": "midnight"},
        }

    def set_time_data(self):
        """Store the calendar database.
        :write:
        - _calendar.pickle file
        """
        with open(self.file_nm +
                  "_calendar.pickle", 'wb') as f:
            pickle.dump(self.CALENDAR_DB, f)
        print(f"CALENDAR_DB object pickled to: {self.file_nm}" +
              "_calendar.pickle")

    def orbital_congruence(self,
                           p_obj_ty: object,
                           p_obj_nm_a: str,
                           p_obj_nm_b: str):
        """Compute the congruence of two orbits as the
        product of their orbital periods.
        :args:
        - p_obj_ty (object): object from CAL class
        - p_obj_nm_a (str): name of first orbital object
        - p_obj_nm_b (str): name of second orbital object
        :return: congruence (float) = product of two orbits
        """
        return (p_obj_ty[p_obj_nm_a]["orbit"] *
                p_obj_ty[p_obj_nm_b]["orbit"])

    def lunar_phases(self,
                     p_obj_ty: object,
                     p_obj_nm: str):
        """Compute the phases of a moon. The new, quarter,
        and full phases occur on specific days. The waning
        and waxing phases occur between these days.
        :args:
        - p_obj_ty (object): object from CAL class
        - p_obj (str): name of moon
        :return: phases (dict) = {phase_nm: day_num, ..}
        """
        orbit = p_obj_ty[p_obj_nm]["orbit"]
        phases = {"new": orbit,
                  "waxing crescent": orbit * 0.125,
                  "1st quarter": orbit * 0.25,
                  "waxing gibbous": orbit * 0.375,
                  "full": orbit * 0.5,
                  "waning gibbous": orbit * 0.625,
                  "3rd quarter": orbit * 0.75,
                  "waning crescent": orbit * 0.875}
        return phases
