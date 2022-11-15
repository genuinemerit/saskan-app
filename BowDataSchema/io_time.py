#!python
"""
:module:    io_time.py

:author:    GM (genuinemerit @ pm.me)

Prototype definitions of astronomical events
in a game world's local star system. Define calendars
for the passage of time, including era, epoch, year,
season, month, day, noon, midnight, sunrise, sunset,
phases of two moons, timing of planetary conjunctions.
All are from perspective of a single time zone that
encompasses the lands of the game, spread over about 1,600
square kilometers, located in the northern hemisphere.

All values are hard-coded for now. Later, abstract the
static values into config class or file.

To simplify things for now, all day-counts are based on
a start-time at midnight.

Rebuild the saskan conda venv using lessons learned
from work on the home-finance app. Use latest version of
python and pandas. Switch to pygame for a GUI.
"""

import pickle
# import random

# from copy import copy
from dataclasses import dataclass   # fields
# from os import path
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401
# from symbol import pass_stmt            # noqa: F401

from io_config import ConfigIO          # type: ignore
from io_file import FileIO              # type: ignore
# from io_redis import RedisIO            # type: ignore

CI = ConfigIO()
FI = FileIO()
# RI = RedisIO()


class TimeIO(object):
    """Class for Calendar-related data and methods.
    """
    def __init__(self,
                 p_file_nm: str):
        """Manage time, calendar and astronomical data.
        Store data in a pickled dict: CALENDAR_DB.

        To save the CALENDAR_DB pickle, call:
            self.set_time_data(p_file_nm)
        To retieve it, call:
            self.get_time_data(p_file_nm)

        :args: p_file_nm: str
            - Generic name of time data file object
            - Example: "time_data"
        """
        self.CAL_DB = dict()

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
        """Define static compoments of CALENDAR_DB.
        Initialize the time dictionary if one does not yet
        exist.  For example, to start a new one, or to
        wipe the current one and start a new one.

        These materials should remain immutable.
        Eventually move this to an external config file.

        Units are as follows unless otherwise noted:
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
                   "type": "[solar, arithmetic]",
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
                    "type": "[solar, arithmetic]",
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
                     "type": "[solar, arithmetic]",
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
                      "type": "[solar, arithmetic]",
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
                    "type": "[solar, arithmetic]",
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
                    "type": "[solar, arithmetic]",
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
                      "type": "[solar, arithmetic]",
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
                       "type": "[lunar, astronomical]",
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
                    "type": "[solar, arithmetic]",
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
                     "type": "[arithmetic]",
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
                      "type": "[solar, arithmetic]",
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
                      "type": "[solar, arithmetic]",
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
                     "type": "[stellar, arithmetic]",
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

    def set_file_name(self,
                      p_file_nm: str):
        """Return full name of calendar DB file."""
        # self.file_nm = path.join(RI.get_app_path(),
        #                        RI.get_cfg_val(
        #                            'save_path'),
        #                        p_file_nm)
        file_nm = "/tmp/" + p_file_nm + "_calendar.pickle"
        return file_nm

    def get_time_data(self,
                      p_file_nm: str):
        """Retrieve the calendar database

        :args: p_file_nm (str) - generic file name
        """
        try:
            with open(self.set_file_name(p_file_nm), 'rb') as f:
                    self.CAL_DB = pickle.load(f)
            pp(self.CAL_DB)
        except FileNotFoundError:
            print("No calendar database found.")

    def set_time_data(self,
                      p_file_nm: str):
        """Store the calendar database.
        :args: p_file_nm (str) - generic file name
        :write:
        - _calendar.pickle file
        """
        try:
            with open(self.set_file_name(p_file_nm), 'wb') as f:
                pickle.dump(self.CAL_DB, f)
            print("Calendar database saved.")
        except Exception as e:
            print("Error writing calendar database. " + str(e))

    def orbital_congruence(self,
                           p_orb_obj: object,
                           p_core_nm: str,
                           p_obj_nm_a: str,
                           p_obj_nm_b: str):
        """Compute the congruence of two orbits as the
        product of their orbital periods. The objects
        must be of the same type, either PLANETS or
        MOONS. The first argument is the actual object
        from CAL, not just a type name.
        :args:
        - p_orb_obj (object): object from CAL class
        - p_core_nm (str): name of object around which they orbit
        - p_obj_nm_a (str): name of first orbital object
        - p_obj_nm_b (str): name of second orbital object
        :return: congruence (float) = product of two orbits
        """
        return (p_orb_obj[p_core_nm][p_obj_nm_a]["orbit"] *
                p_orb_obj[p_core_nm][p_obj_nm_b]["orbit"])

    def lunar_phases(self,
                     p_lunar_obj: object,
                     p_planet_nm: str,
                     p_moon_nm: str):
        """Compute the phases of a moon. The new, quarter,
        and full phases occur on specific days. Waning
        and waxing phases occur between these days.
        The times are computed as fractions of an orbit,
        which is calculated in Gavoan days. The "common"
        reference to the phases may extend a bit on either
        side of the computed day/time.

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
        return(zero_point_orbits)

    def year_zero(self,
                  p_cal_nm: str):
        """Provide starting point for time calculations.
        Based on the calendar type, the starting point is
        adjusted for season (year start) and time (day start),
        relative to the SAG starting point.

        :args: p_cal_nm (str): name of calendar

        :return: dict = {start_time (float) = year zero, in calendar
        reckoning, adjusted for year and day start
        "SAG": {"name": "Short Astro-Gavorian",
                    "type": "[solar, arithmetic]",
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
        """
        # Year zero / Day zero is the same on all calendars,
        # so we just grab it from the SAG calendar. 
        # Always midnight at the Winter Solstice.

        #  SAG Year Zero, Day 1 is represented as:
        #  Day      1
        #  Month    NA
        #  Year     4934
        #  Time     00:00
        #  Desc     Day 1, Year 4934, Midnight, Winter solstice.
        print("\n..." + p_cal_nm)
        sag_start_season =\
            self.CAL.CALENDAR["SAG"]["year"]["start"]["season"]
        sag_start_event =\
            self.CAL.CALENDAR["SAG"]["year"]["start"]["event"]
        sag_start_day = 1
        sag_start_time =\
            self.CAL.CALENDAR["SAG"]["day"]["start"]
        # print("\nSAG Year Zero, Day Zero: " +
        #       sag_start_season + " " +
        #       sag_start_event + ", " +
        #       str(sag_start_day) + " " +
        #       sag_start_time)

        # The calendar DB has year zero for each calendar.
        cal_start_year =\
            self.CAL.CALENDAR[p_cal_nm]["year"]["zero"]
        cal_start_month = "??"
        if self.CAL.CALENDAR[p_cal_nm]["months"] is None:
            cal_start_month = "N/A"
        cal_start_day = "??"
        # Calendars start the year at different times.
        # How date and time are described varies by calendar.
        # If there are differences between it and the SAG
        # calendar, then day and month needs to be computed as 
        # an offest from the SAG calendar.

        # Most, but not all, solar calendars start on a solstice
        # or equinox, that is, the first day of a season. In these
        # cases, we can easily compute the number of days from start
        # of the calendar year to the winter solstice.

        # We assume that any start season which is not winter
        # occurs __prior__ to winter.  We want to compute the
        # days offset between when the calendar starts and the
        # winter solstice, which is the start of season #4. 
        # The CAL SEASONS object's "reverse" attribute tells us
        # how many seasons before Winter that season is. 
        try:
            cal_start_season =\
                self.CAL.CALENDAR[p_cal_nm]["year"]["start"]["season"]
            print("Calendar start season: " + cal_start_season)
            days_before_winter =\
                self.CAL.SEASON[cal_start_season]["rel"]["reverse"] *\
                self.CAL.SEASON["days"]
            cal_start_day = int(round(
                sag_start_day + days_before_winter))
        except KeyError:
            pass

        # Lunar calendars typically start on a full moon. OR two.
        # Their year/start/event name will be "full" and it will
        # list one or both the moons names. Luckily :-) the day zero
        # event occurred on a winter solstice that also happened to be
        # a full moon conjunction of the two moons.  Only the Settan
        # calendar (so far) is a lunar one. We can use a "full moons"
        # rule to set its day count to 1 for the day zero event.

        # Some solar calendars (K'hol, K'beq) start their count on
        # an arbitrary day, enumerated as day 1, but the count is not
        # necessarily in synch with the SAG calendar every year. They have a negative year zero count.
        # For the sake of conveniece, unless they
        # provide a different seasonal start point, assume they
        # start on the winter solstice. In other words assume their
        # day zero day count is 1.

        # The Empa calendar starts on the planetary conjunction
        # Gavor and Astra, which occurs only every 84,989 days. Its
        # years are a fraction of this amount, with each year being
        # counted as tick towards the cojunction, then starting over.
        # Since day zero occurred during a Great Conjunction, we can
        # define Empa day zero as day 1 of its calendar. 

        # Different calendars start a __day__ at different times.
        # The SAG day starts at midnight. May need to adjust the
        # day count up or down by 1 to account for these differences.

        # Some calendars use months, some don't.
        # For those that do, if we have a day-count then now we
        #  can compute the month and day of the month.

        return(self.CAL.CALENDAR[p_cal_nm]["name"],
               cal_start_year,
               cal_start_month,
               cal_start_day)

    def get_day_part(self,
                     p_day_t: float):
        """Determine if time is before or after noon, etc.
        Same for all calendars.

        :args: p_day_t (float): time of day, as decimal portion of day
        """
        day_part = None
        for part in ["midnight", "sunrise", "noon", "sunset"]:
            if p_day_t >= self.CAL.PARTS["day"]["time"][part]:
                day_part = part
        return day_part

    def get_day_hour(self,
                     p_cal_nm: str,
                     p_day_t: float):
        """Determine the hour of the day, for specified calendar.

        :args:
        - p_cal_nm (str): index to static calender data
        - p_day_t (float): time of day, as decimal portion of day
        """
        # For day starting at midnight:
        hour = int(p_day_t / self.CAL.PARTS["day"]["duration"]["hour"])
        day_start = self.CAL.CALENDAR[p_cal_nm]["day"]["start"]
        if day_start == "sunrise":
            hour -= 6
        elif day_start == "noon":
            hour -= 12
        elif day_start == "sunset":
            hour -= 18
        return hour

    def get_day_watch(self,
                      p_day_h: int):
        """Determine the watch for specified calendar-hour.

        :args:
        - p_cal_nm (str): index to static calender data
        - p_day_h (int): hour of the day, calendar-specific
        """
        watch = int(p_day_h / self.CAL.PARTS["hour"]["duration"]["watch"]
                    + 1)
        return watch

    def get_date_time(self,
                      p_day_n: float,
                      p_roll_n: float = 0.0):
        """Compute the date from the day number.
        If only day num provided, return that date.
        If roll number, then return day num plus roll num date.
        Use negative roll number to roll backwards.
        Fractions of days expressed as decimals in the arguments,
        returned as watches, hours, wayts and ticks.
        Count SAG day zero at midnight as day number 0.

        Results are saved in a dictionary, keyed by SAG day number.

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
                           self.CAL.CALENDAR["SAG"]["year"]["zero"])
            self.CAL_DB[p_day_n] = dict()
            for cal_nm in self.CAL.CALENDAR.keys():
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
