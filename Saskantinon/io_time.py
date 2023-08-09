#!python
"""
:module:    io_time.py

:author:    GM (genuinemerit @ pm.me)

Prototype definitions of astro-temporal events
in game world's local star system. Define calendars
for the passage of time, including era, epoch, year,
season, month, day, noon, midnight, sunrise, sunset,
phases of moons, timing of planetary conjunctions.

A single time zone encompasses the lands, spread over 2182031 km^2.
(1660 km east-west, 1310 km north-south), located in the
northern hemisphere. Two major time zones would be better.
Given the low technology level, more local and regional variations
would be entirely appropriate.


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
- All of this implies bringing a geo data set into the mix.
    - Use io_graphs, as useful, to visualize the geo data.
    - Use the places spreadsheet as a starting point, but store as JSON.
- Do something similar for stars in local galaxy and galaxies in local cluster.
- See ontology lab (universe.py, region.py) for ideas.
- See map_build.py and other prototype modules for ideas.
- See schema/places_data.ods for ideas about data.
- Try to use accurate-ish formulae for the calculations,
  BUT don't get obsessed with it. Goal is to have something fun
  to play with, not to be an accurate astro-geo simulator.

OK..

- Created a schema, saskan_space.json and started filling in data. ChatGPT was very helpful in trying to come with something resembling a plausible planet + satellites system. I'm not sure how much of it I'll use, but it's a start. Would be interesting to see if I can use GPT inside VS Word / GitHub Pilot to write code simulating movement of heavenly bodies, phases of the moons, etc.

- Created a saskan_time.json schema too but have not started filling it in yet. Want to use algorithms as much as I can when dealing with calendars, dates, times in the game context.
"""

import math
import matplotlib.pyplot as plt
import numpy as np
# import json
import pickle

from dataclasses import dataclass   # fields
from matplotlib.animation import FuncAnimation
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_file import FileIO              # type: ignore
from saskan_math import SaskanMath      # type: ignore

FI = FileIO()
SM = SaskanMath()

class SpaceIO(object):
    """Class for astronomical data and methods.
    """
    def __init__(self):
        """Manage astronomical data.
        Pull in schema from saskan_space.json.
        Derive addtional data
        """
        # moon = FI.S["space"]["Endor"]
        # self.get_orbit_and_angular_diameter(moon)
        # self.simulate_lunar_orbit()
        pass

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

    def common_lunar_orbits(self,
                            max_days: float = 100000.00,
                            full_rpt: int = 4):
        """Compute synchronization of lunar orbits.

        :args:
        - max_days: (float) default = 5000.00
            - Maximum number of days for which to compute lunar orbits.

        - So far, the report shows days on which the moons are full, that is,
          have completed an orbit. If more than one moon is full on the same day,
          they are grouped together.

          Next I need to be able to analyze that data. On what dates do full moons
          of any kind occur? On what dates do multiples full moons occur? When do
          specific combinations of full moons occur?  What are the patterns for
          congurence of full moons?

          Post results of this algorithm to a file or queue,
          maybe a Pandas dataframe or any in-memory object in such a way as to be able
          to perform analysis on the entire dataset.

          My fantasy world is currently set at year AGD 4934. The AGD calendar uses
          a 365 or 366 days year, with a leap day added every four years, for an average
          year of 365.24 days.  That means we are presently up to day number 1,802,095 or so.
          We can expect the fantasy world to continue for another 5,000 years, so that would
          be 1,826,095 more days. Let's even things out and say I want full moons data for
          a period of 10,000 years, or 3,650,000 days.

          Before I go there, maybe see if I can come up with a simpler algorithm just to
          identify days when there are multiple full moons.  Part of the challenge is that
          the days are incremented by 0.01, then the "day" of a full moon is taken as the
          integer rounding of the day -- close enough for what I need. But there can be a
          hundred iterations of each "day", so need to be careful to filter out / prevent duplicates.

          The queue should fill for each "integer day", with complete set of results for that "day",
          then get emptied out to a file or other store when the integer day changes.
          Throttle its contents based on desired analysis -- i.e., all full moons, only when
          multples, specific combos, etc.

          Continue to test with relatively small number of days, then scale up to 10,000 years.

          Tested for 1 million years. Took about 3 minutes to run. Not sure how I can optimize it.
          Tested for 3.5 millionyears. Took about 15 minutes.
          There's a wee bug in the code where the year reported is always reset to the last year
          that had full moons reported, e.g., year 9583. Obviously its becasue I am not printing
          the year based on i_day, but the last counted year. D'oh!

          Would also be handy to show the day (AGD calender) on which the full moons occur,
          not just the total count of days since day 0.  This may be a good time to start
          computing the FD and Terr. dates too.

          Getting better! Another nice thing to have would be option to indicate near full
          moon conjunctions. Let's say, for sake of argument, a near conjunction is when the
          complete orbits are within 1 degree of each other. So if Moon A is at 360 / 0 degrees
          in its orbit and Moon B is between 359 and 1 degrees, that would be a near conjunction.

          Of course, this is all fantasy. I assuume all the moons have same or nearly same
          ecliptic plane. Which is not how it works, say, on Jupiter. And even bigger fantasy,
          I am assuming they were all in conjunction on Day Zero - the day of the Great Cataclysm.
          Interestingly, after 3.5 million days, the most conjunctions I've seen is 5. Wondering
          how long it would take to see all 8 in conjunction. Would it be the product of the
          period of all their orbits?

        """
        def set_moons_struct():
            """Init a local structure for augmenting moon schema data with orbits data.
            """
            moons = dict()
            for m_nm, m_data in FI.S["space"].items():
                if m_data["type"] == "MOON":
                    orbit = m_data["orbit"][0]["days"]
                    daily_arc = round(360/ orbit, 2)
                    moons[m_nm] = {"Day": 0.00,
                                "Arc": daily_arc,
                                "Orbit": orbit,
                                "arc_completed": 0.00,
                                "orbits_completed": 0}
            return moons

        moons = set_moons_struct()
        d_day = 00.00
        day_increment = 0.01
        q_data = dict()
        while d_day < max_days:
            d_day = round((d_day + day_increment), 2)
            i_day = round(d_day)
            for m_nm, m_data in moons.items():
                arc_completed = m_data["arc_completed"] + (m_data["Arc"] * day_increment)
                if arc_completed >= 360.00:
                    m_data["orbits_completed"] += 1
                    m_data["arc_completed"] = 360.00 - arc_completed
                    if i_day not in q_data:
                        q_data[i_day] = list()
                    q_data[i_day].append((m_nm, m_data['orbits_completed']))
                else:
                    m_data["arc_completed"] = arc_completed
        for i_day, m_data in q_data.items():
            if len(m_data) >= full_rpt:
                year = math.floor(i_day / 365.24)
                d_day = i_day - (year * 365.24)
                day = math.floor(d_day)
                agd_wayt = round((d_day - day) * 100)
                pp((f"AGD {year}.{day}.{agd_wayt} ({len(m_data)} full moons:)", m_data))

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


class TimeIO(object):
    """Class for Calendar-related data and methods.
    Includes astronomical and geographical data as well as temporal/calendrical
    data and algorithms.  Seasonal data is also a distinct data class.
    Will eventually want a tidal data class too probably.

    @DEV:
    Eventually may want distinct io_geo and io_astro classes.
    And a mapping class for rendering graphic displays, maps.
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

        Angular diameter is the apparent size of an object as seen from a point of view, i.e., how big a moon appears in the sky. Given the distance (d) and diameter (D) of an object, its angular diameter (δ) can be calculated as follows:
        δ = 2 × arctan(D/2d)


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

    def get_parent_maps(self,
                        p_m: dict,
                        p_t: dict,
                        p_i: int):
        """Recursive function to get all parent maps.
        Keep recursing until a grid_id is found.

        :args:
        - p_m (dict) - a unit-level dict from SM.MAP.maps
        - p_t (dict) - the combined dict of all parent maps
        - p_i (int) - the number of recursions
        """
        m = p_m
        t = p_t
        i = p_i
        if "grid_id" in m.keys():
            g = SM.MAP.grids[m["grid_id"]]
            t = {**t, **{"grid": {**g, **{"_id": m["grid_id"]}}}}
        elif "parent_nm" in m.keys():
            i += 1
            k = m["parent_nm"]
            m = SM.MAP.maps[k]
            t = {**t, **{f"map_{i}": {**m, **{"_name": k}}}}
            t = self.get_parent_maps(m, t, i)
        return t

    def get_map_stats(self,
                      p_map_nm: str) -> tuple:
        """Return map info and dimensions in various units.

        :args:
        - p_map_nm (str) - map template index = valid index to SM.MAP['maps']

        :returns:
        - map_dim (tuple (dict, str)) - map dimensions (dict, json)

        """
        m = SM.MAP.maps[p_map_nm]
        t = self.get_parent_maps(
            m, {f"map_0": {**m, **{"_name": p_map_nm}}}, 0)

        # Get grid dimensions in various units
        grid_km = t["grid"]["grid_km"]
        t["grid"]["grid_mi"] = SM.km_to_mi(grid_km, p_round=True)
        t["grid"]["grid_gawo"] = SM.km_to_ga(grid_km, p_round=True)
        t["grid"]["grid_kata"] = SM.km_to_ka(grid_km, p_round=True)
        for k, m in t.items():
            if k.startswith("map_"):
                t[k]["km"]= {}
                t[k]["km"]["w"] = m['grid_cnt']['w'] * grid_km
                t[k]["km"]["h"] = m['grid_cnt']['h'] * grid_km
                t[k]["mi"]= {}
                t[k]["mi"]["w"] = SM.km_to_mi(t[k]["km"]["w"], p_round=True)
                t[k]["mi"]["h"] = SM.km_to_mi(t[k]["km"]["h"], p_round=True)
                t[k]["gawo"]= {}
                t[k]["gawo"]["w"] = SM.km_to_ga(t[k]["km"]["w"], p_round=True)
                t[k]["gawo"]["h"] = SM.km_to_ga(t[k]["km"]["h"], p_round=True)
                t[k]["kata"]= {}
                t[k]["kata"]["w"] = SM.km_to_ka(t[k]["km"]["w"], p_round=True)
                t[k]["kata"]["h"] = SM.km_to_ka(t[k]["km"]["h"], p_round=True)

        pp(("t", t))
        # return t
        # return (t, json.dumps(t))

        # km_ew = p_grid_w * grid['grid_km']
        # km_ns = p_grid_h * grid['grid_km']
        # dglat_n = grid['edge_dg']["N"] - (p_grid_t * grid['grid_dg']["NS"])
        # dglat_s = dglat_n - (p_grid_h *  grid['grid_dg']["NS"])
        # dglong_w = grid['edge_dg']["W"] + (p_grid_l + grid['grid_dg']["EW"])
        # dglong_e = dglong_w + (p_grid_w * grid['grid_dg']["EW"])


        # Currently, North and West cannot be moved further north or west.
        # South and East can be moved further south or east.
        # North can move further south, past the Equator, past the South Pole for that matter.
        # South can move further south, past the South Pole.
        # West can move further east, past the Prime Meridian, etc.
        # East can move further east, past the Prime Meridian, the International Date Line, etc.
        # @DEV: Add support for adjusting values that pass beyond 180 degrees longitude or latitude,
        # keeping in mind that the planet is (effectively) a sphere.


    def define_universe(self,
                        p_smaller: bool = False,
                        p_larger: bool = False) -> dict:
        """Define universe. Drawing on some of the concepts in the old
        'universe.py' module (see ontology_lab).

        Concepts defining the game space include the following.


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

          The planetary system should include at least one gas giant
          that will divert asteroids and other junk from the inner
          planets.  If the system is intended to support life, it should
          be relatively close to the star, but not too close, or be a
          moon with an atmosphere of a gas giant.

        Based on inputs and rules, return dimensions, mass, rate of
        expansion, etc. for the play Universe.
        """
        def set_TU() -> dict:
            """
            - Total Universe (TU): a sphere measured in gigaparsecs, the
            largest possible unit defined for game play.

            Diameter of the known universe is about 28.5 gigaparsecs;
            radius is 14.25 gigaparsecs. This will be fairly constant,
            with only minor changes for each generation. It fluctuates
            as the universe expands. In the old version I used the "big
            bang" animation to center the universe, and as a splash screen,
            similar to some video games.

                - So, either pick a random diameter within constraints, or
                allow for an input indicating a slightly larger or slightly
                smaller universe.

            Age of the TU is 13.787±0.020 billion years, give or take, with
            only Agency calendars going back more than 4,000 Gavoran years
            or so.

            For unit measurement conversions, see the 'C' dataclass.
            For unit names, see the 'M' dataclass.

            The origin point at the center of the sphere is where this known
            universe began, its big bang point. Or in game terms, where the
            last game universe ended and a new one began.

            It is exapanding in all directions at a rate of 73.3 kilometers
            per second per megaparsec.

            Dark Energy comprisees 68.3% of the universe, Dark Matter 27.4%,
            remaining 4.3% is baryonic matter (stars, planets, life, etc.),
            also referred to as "ordinary matter".

            Ordinary matter/mass = 1.5×10^53 kg
            For game purposes, I will take 4.3% as the approximate area of
            the TU sphere that contains galaxies, stars, planets, etc.

            For the purposes of the game, we will consider mass and matter to
            be the same thing. Antimatter equals matter at the big bang, but
            then almost entirely vanishes. No one know why. Theoretically,
            the universe should not exist since matter and antimatter should
            have annihilated each other. But it does. So, we will assume that
            the universe is made of matter, not antimatter, and that the
            antimatter "went somewhere".

            If I want to mess around with goofy concepts, then come up with
            scenarios where antimatter is the dominant force or pooled, or where
            dark energy or dark matter get concentrated rather than being constant.

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

            @DEV: Vary the limits for size of universe a bit more.
            """
            # radius in gigaparsecs
            # baryonic mass in kg
            # baryonic pct
            # setting radius in megap, kilop, parsecs, light years, AU, km, m...
            TU = {(self.M.RD, self.M.GPC): 14.25,
                  (self.M.BA, self.M.MS, self.M.KG): 1.5 * 10e53,
                  (self.M.BA, self.M.PCT): 4.3}
            if p_smaller:
                TU[(self.M.RD, self.M.GPC)] *= 0.9999
                TU[(self.M.BA, self.M.MS, self.M.KG)] *= 0.9999
            elif p_larger:
                TU[(self.M.RD, self.M.GPC)] *= 1.0001
                TU[(self.M.BA, self.M.MS, self.M.KG)] *= 1.0001
            # radius in megaparsecs, kiloparsecs, parsecs, light years, AU, km, m ?
            TU[(self.M.RD, self.M.MPC)] = TU[(self.M.RD, self.M.GPC)] * self.C.GPC_TO_MPC
            TU[(self.M.RD, self.M.KPC)] = TU[(self.M.RD, self.M.MPC)] * self.C.MPC_TO_KPC
            TU[(self.M.RD, self.M.PC)] = TU[(self.M.RD, self.M.KPC)] * self.C.KPC_TO_PC
            TU[(self.M.RD, self.M.LY)] = TU[(self.M.RD, self.M.PC)] * self.C.PC_TO_LY
            TU[(self.M.RD, self.M.GLY)] = TU[(self.M.RD, self.M.LY)] * self.C.LY_TO_GLY
            TU[(self.M.RD, self.M.AU)] = TU[(self.M.RD, self.M.LY)] * self.C.LY_TO_AU
            TU[(self.M.RD, self.M.KM)] = TU[(self.M.RD, self.M.AU)] * self.C.AU_TO_KM
            TU[(self.M.RD, self.M.M)] = TU[(self.M.RD, self.M.KM)] * self.C.KM_TO_M
            # volume in gigaparsecs, gigalight years, light years, meters cubed
            TU[(self.M.VL, self.M.GPC3)] =\
                4 * math.pi * (TU[(self.M.RD, self.M.GPC)] ** 2)
            TU[(self.M.VL, self.M.LY3)] =\
                4 * math.pi * (TU[(self.M.RD, self.M.LY)] ** 2)
            TU[(self.M.VL, self.M.GLY3)] =\
                4 * math.pi * (TU[(self.M.RD, self.M.GLY)] ** 2)
            TU[(self.M.VL, self.M.M3)] =\
                4 * math.pi * (TU[(self.M.RD, self.M.M)] ** 2)

            # Volume of known universe: 3.566 x 10^80 cubic meters
            # Another estimate is 415,065 Glyr3  (cubic gigalight years)

            # Also, keep in mind that the universe may be infinite, that
            # we can sort of measure the observable universe, but even then
            # being accurate is hard since no one really knows its shape,
            # and it is expanding, and that expansion will limited by the
            # mass of all the matter in the universe, and that mass is also
            # a bit of a mystery. So, we will just use a number that is fun!

            # Do some transforms of units to see if this model works.
            # I came up with 2.4296690577848235e+54 for vol in meters,
            # so something is wrong. My computed value is much tinier:
            # 2.429675e+54 / 3.566e+80 = 6.8e-27
            # Check each transform to see where the error is.
            # Check to see where the volume of known universe came from.
            # Try reversing the area calculation to get the radius in m?

            # Back up the testing a bit. Check all of the transform equations
            # before doing the volume calculations and other large algorithms.
            return TU

        TU = set_TU()
        pp((self.M.TU.title(), TU))

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
