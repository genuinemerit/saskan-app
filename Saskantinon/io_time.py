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

import glob
import math
import matplotlib.pyplot as plt
import numpy as np
# import json
import pickle
import time

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
        self.FULL_MOONS = dict()
        self.CAL = dict()

    def set_cal_file_name(self,
                          p_nm: str):
        """Return full name of a Calendar data file.
        Each calender data file holds 1 Terpin turn =
        4 AGD or FD turns.
        :args:
        - p_nm (str) - identify Terpin and AGD turns in
            file name using format "tttttt_aaaa-aaaa"
        """
        file_nm = "/dev/shm/" + p_nm + "_Calendar.pickle"
        # print("Pickle file name: " + file_nm)
        return file_nm

    def get_cal_file(self,
                     p_nm: str):
        """Retrieve the Calendar data file.

        :args: p_db_nm (str) - turn-specific part of file name
        """
        try:
            with open(self.set_cal_file_name(p_nm), 'rb') as f:
                self.CAL = pickle.load(f)
            print("Calendar data file retrieved.")
        except FileNotFoundError:
            print("No Calendar data file found.")

    def write_cal_file(self,
                     p_nm: str):
        """Store the Calendar data in pickled file.
        :args: p_nm (str) - turn-specific part of file name
        :write:
        - _{name}_Moons.pickle file
        """
        try:
            with open(self.set_cal_file_name(p_nm), 'wb') as f:
                pickle.dump(self.CAL, f)
            print("Calendar data file saved.")
        except Exception as e:
            print(f"Calendar data file not saved:\n{str(e)}")

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

    def generate_calendars(self,
                           p_start_terp_cnt: int=1,
                           p_terp_calendars: int=1):
        """
        Let's start by generating a separate file for each Terpin turn.
        :args:
        - p_start_terp_cnt: (int) default = 1 - Terpin turn to start with.
            Ter Count 1 = Ter Turn 359696
        - p_terp_calendars_to_generate: (int) default = 1 - Number of calendar
            files to generate. Each file contains one Terpin turn = 4 AGD and FD
            turns.

        @DEV:
        The way this is currently set up, calendar generation has to
        always start with the "cata" Terpin turn, and then proceed from there.
        I can probably adjust that, but need to think about it. Probably just
        add 1451 to the epoch start day? May also want to add a parameter to
        indicate the count of Terpin turns to start with, and how many to
        generate.

        # The epochal ("cata") year in AGD is 1.
        # The epochal ("cata") year in Terpin is 359696.
        # The epochal ("cata") year in FD is -508

        # There are 1451 days in a Terpin turn.
        #  All Terpin turns are the same length.
        # AGD and FD turns are 365.24 days long on avereage, varying in 4-turn
        # cycles from 365 to 366 days.

        # adjust for calendars that have a negative value for epoch_start_year
        # NB - We assume no calendars use a year = 0.
        """
        def init_cal_data(p_start_terp_cnt,
                           p_terp_calendars):
            cal_schema = {c_nm: c_data for c_nm, c_data in FI.S["time"].items()}
            p_start_terp_cnt = 0 if p_start_terp_cnt <= 1 else p_start_terp_cnt - 1
            p_terp_calendars = 0 if p_terp_calendars <= 1 else p_terp_calendars - 1
            cal = dict()
            # Important to do TER first...
            for c in ("TER", "AGD", "FD"):
                c_data = cal_schema["Calendar"][c]
                cal[c] = dict()
                cal[c]["epoch_start"] = c_data["turn"]["epoch_start"]
                cal[c]["diy_nm"] = c_data["turn"]["days"]
                cal[c]["diy"] = cal_schema[c_data["turn"]["days"]]["length"]
                if cal[c]["diy_nm"] == "Leap_Turn":
                    cal[c]["turn"] = cal[c]["epoch_start"] + p_start_terp_cnt
                    cal[c]["end_turn"] = cal[c]["turn"] + p_terp_calendars
                elif cal[c]["diy_nm"] == "Fatune_Turn":
                    multi_y = round((cal["TER"]["diy"] / cal[c]["diy"]))
                    cal[c]["turn"] = cal[c]["epoch_start"] + (multi_y * p_start_terp_cnt)
                    if cal[c]["epoch_start"] < 1 and cal[c]["turn"] >= 0:
                        cal[c]["turn"] += 1
                    cal[c]["end_turn"] = cal[c]["turn"] + (multi_y * (p_terp_calendars + 1)) - 1

            epoch_day = 1 + (cal["TER"]["diy"] * p_start_terp_cnt)
            return(cal, epoch_day, multi_y)

        def set_turn_day(epoch_day, leap_cal_day, fatune_day):
            self.CAL[epoch_day] = dict()
            for c in ("TER", "AGD", "FD"):
                if c == "TER":
                    self.CAL[epoch_day]["TER"] = {
                        "turn": f"{cal['TER']['turn']}",
                        "day_in_turn": leap_cal_day}
                else:
                    self.CAL[epoch_day][c] = {
                        "turn": f"{cal[c]['turn']}",
                        "day_in_turn": fatune_day}

        def set_moon_data(epoch_day):
            if epoch_day in self.FULL_MOONS:
                self.CAL[epoch_day]["Moons"] = dict()
                for m_data in self.FULL_MOONS[epoch_day]["data"]:
                    for m_nm, m_info in m_data.items():
                        self.CAL[epoch_day]["Moons"][m_nm] = {
                            "epoch_day": m_info[1],
                            "ang_diam_dg": FI.S["space"][m_nm]["angular_diameter"][0]["dg"],
                            "dist_km": FI.S["space"][m_nm]["distance"][0]["km"]}

        def pickle_cal_file(cal):
            """ pickle the file and move on to next Leap_Year turn calendar"""
            file_range = f"{cal['AGD']['turn']:04d}-{cal['AGD']['turn'] + 3:04d}." +\
                         f"{cal['TER']['turn']:06d}"
            self.write_cal_file(file_range)
            self.CAL = dict()

        # generate_calendars() main
        # =========================
        cal, epoch_day, multi_y = init_cal_data(p_start_terp_cnt, p_terp_calendars)
        if epoch_day > 3509999:
            print("Too far into the future. Max epoch day is 3509999.")
            return False
        self.get_moons_file('Full')

        while cal["TER"]["turn"] <= cal["TER"]["end_turn"]:
            leap_cal_day = 1
            for fatune_cycle in range(1, multi_y + 1):
                end_day = 367 if fatune_cycle == 4 else 366
                for fatune_day in range(1, end_day):
                    set_turn_day(epoch_day, leap_cal_day, fatune_day)
                    set_moon_data(epoch_day)
                    epoch_day +=1
                    leap_cal_day += 1
                for c in ("AGD", "FD"):
                    cal[c]['turn'] += 1
                    cal[c]['turn'] = 1 if cal[c]['turn'] == 0 else cal[c]['turn']
            pickle_cal_file(cal)
            cal["TER"]["turn"] += 1

    def analyze_calendars(self,
                          p_start_turn: int = 1,
                          p_end_turn: int = 0):
        """Analyze calendars. Run various types of reports.
        :args:
        - p_start_turn: (int) default = 1  AGD Turn to start with
        - p_end_turn: (int) default = 0    AGD Turn to end with.
        """
        p_start_turn = 1 if p_start_turn < 1 or p_start_turn > 9999\
            else p_start_turn
        p_end_turn = p_start_turn if p_end_turn < p_start_turn\
            else p_end_turn
        p_end_turn = 9999 if p_end_turn < 1 or p_end_turn > 9999\
            else p_end_turn
        t_start = f"{p_start_turn:04d}"
        t_end = f"{p_end_turn:04d}"
        print(f"Start Fatune Turn: {t_start}\tEnd Fatune Turn: {t_end}")
        cal_files = glob.glob(f"/dev/shm/*Calendar.pickle")
        cals_to_analyze = list()
        for cal_f_full in cal_files:
            cal_nm = cal_f_full.split("/")[-1].split(".")[0].split("-")
            if cal_nm[0] >= t_start or cal_nm[1] >= t_start:
                cals_to_analyze.append(cal_f_full)
            if cal_nm[1] >= t_end:
                break
        # print("Calendars to analyze:")
        # pp((cals_to_analyze))
        t_this = t_start
        # print(f"t_this: {t_this}\tt_end: {t_end}")
        while t_this <= t_end:
            for cal_f in cals_to_analyze:
                cal_nm = cal_f.split("/")[-1].split(".pickle")[0].split("_")[0]
                cal_yrs = cal_nm.split(".")[0].split("-")
                # pp(("cal_nm", cal_nm))
                # pp(("cal_yrs", cal_yrs))
                print(f"\nAnalyzing calendar: {cal_nm} for Fatune Turn: {t_this}")
                if cal_yrs[0] >= t_this or cal_yrs[1] >= t_this:
                    self.get_cal_file(cal_nm)
                    cal_data = {e_day: data for e_day, data in self.CAL.items()
                                if f"{int(data['AGD']['turn']):04d}" == t_this}
                    pp((cal_data))
                t_this = f"{int(t_this) + 1:04d}"
                # print(f"Next... t_this: {t_this}\tt_end: {t_end}")

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
