#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Universe Calculator
:module:    universe
:classes:   Universe
:author:    GM <genuinemerit@protonmail.com>
:services_provided:
    Does computations and updates Universe data
"""

## General Purpose imports
import json
import math
import requests
import time                              # pylint: disable=W0611
import sys                               # pylint: disable=W0611
from collections import namedtuple
from os import path
## Home-grown
from func_basic import FuncBasic         # pylint: disable=E0401
from func_basic import BC                # pylint: disable=E0401

## Static methods and local instantiations
###########################################
FB = FuncBasic()

## Classes
#######################################
class Universe:
    """ Handle Universe computations """

    def __init__(self, p_data_path, p_log_path, p_host, p_univ_state, p_univ_nm):
        """ Instantiate Universe object. """
        self.data_path = p_data_path
        self.log_path = p_log_path
        self.univ_host = p_host
        self.univ_nm = p_univ_nm
        self.univ_state = p_univ_state
        # Get latest record from the queue for this key
        urec = FB.get_que_recs(self.data_path, self.univ_nm, p_latest=True)
        # Get the "data" section of the data record
        self.univ_data = FB.get_que_rec_data(urec)
        # FB.log_me('self.univ_data: "{}"'.format(str(self.univ_data)), self.log_path, BC.DEBUG)
        self.do_universe_logic()
        # self.start_universe_screen()

    def do_universe_logic(self):
        """ Execute business rules per requested message """
        if self.univ_state in ['start']:
            self.compute_iau()
            self.compute_pla()
            self.compute_xau()
            self.compute_dark_fluid()
            self.identify_overlaps()
            self.save_start_data()
        else:
            FB.log_me('Unknown message: "{}"'.format(self.univ_state), self.log_path, BC.ERROR)

    def start_universe_screen(self):
        """ Launch Tornado/HTML/JS to run the Start Universe animations """
        requests.get('https://' + self.univ_host + '/univ/play/{}'.format(self.univ_nm))

    def compute_iau(self):
        """
        Initial Universe Area (IAU) is computed as the circle within the Universe which touches
        the radius of the RG or SG cluster which is furthest from Universe origin point (center)
        at the start state. This can vary depending on the start state.
        The radius of the IAU is the inner radius of the PLA.

        Which cluster lies furthest from the universe origin (0,0,0)?
        iau_radius = distance from 0,0 to max_x, max_y + clust_rad
        The distance between two points (x1, y1), (x2, y2) on a plane is:
        he square root of (x2 - x1) squared plus (y2 - y1) squared, that is:  sqrt((x2 - x1)**2 + (y2 - y1)**2)
        The distance formula states that the distance between two points in xyz-space is the square root of the
        sum of the squares of the differences between corresponding coordinates. That is,
            given P1 = (x1,y1,z1) and P2 = (x2,y2,z2), the distance between P1 and P2 is given by
            d(P1,P2) = sqrt ((x2 - x1)2 + (y2 - y1)2 + (z2 - z1)2).
        We compute distance from origin (0,0) to cluster center (max_x, max_y, max_z), plus the cluster radius.
        The area of a sphere is 4 * Pi * radius squared (4 * pi * r**2)
        """
        self.univ_data["U"]["IAU"] = dict()
        self.univ_data["U"]["IAU"]["bgcolor"] = "rgb(255, 200, 200)"
        self.univ_data["U"]["IAU"]["fgcolor"] = "rgb(255, 100, 100)"
        self.univ_data["U"]["IAU"]["radius"] = 0.0
        for _, cdata in self.univ_data["C"].items():
            distance = math.sqrt((cdata['loc']['x'] ** 2) + (cdata['loc']['y'] ** 2) + (cdata['loc']['z'])) + cdata['radius']
            if distance > self.univ_data["U"]["IAU"]["radius"]:
                self.univ_data["U"]["IAU"]["radius"] = distance
        # Storing as "area" here since the "mass" equation was pure kludge and I really do want to know the area.
        self.univ_data["U"]["IAU"]["area"] = 4 * math.pi * (self.univ_data["U"]["IAU"]["radius"] ** 2)

    def compute_pla(self):
        """
        Planetary Life Area (PLA) is the area inside the XAU excluding the IAU.
        Stars, planets and life-forms evolve in this area.
        Its inner radius is equal to the radius of the IAU.
        Its outer radius is equal to the inner radius of the XAU.
        To get its area, compute it normally, then subtract out the IAU area.
        Just going to make the PLA outer radius = the IAU radius * 3 since this is where most of my game takes place.
        """
        self.univ_data["U"]["PLA"] = dict()
        self.univ_data["U"]["PLA"]["bgcolor"] = "rgb(200, 255, 200)"
        self.univ_data["U"]["PLA"]["fgcolor"] = "rgb(100, 255, 100)"
        self.univ_data["U"]["PLA"]["inner_radius"] = self.univ_data["U"]["IAU"]["radius"]
        self.univ_data["U"]["PLA"]["outer_radius"] = self.univ_data["U"]["IAU"]["radius"] * 3
        self.univ_data["U"]["PLA"]["area"] =\
            (4 * math.pi * (self.univ_data["U"]["PLA"]["outer_radius"] ** 2)) - self.univ_data["U"]["IAU"]["area"]

    def compute_xau(self):
        """
        Maximum Universe Area (XAU) is the area within the Universe which is outside the PLA.
        Stars, planet, life-forms terminate, dissipate and prepare for collapse in this area.
        The inner radius of the XAU is equivalent to the outer radius of the PLA.
        To get its area, compute it normally, then subtract out the IAU and PLA areas.
        ust going to make the PLA outer radius = the IAU radius * 4.
        """
        self.univ_data["U"]["XAU"] = dict()
        self.univ_data["U"]["XAU"]["bgcolor"] = "rgb(200, 200, 255)"
        self.univ_data["U"]["XAU"]["fgcolor"] = "rgb(100, 100, 255)"
        self.univ_data["U"]["XAU"]["inner_radius"] = self.univ_data["U"]["PLA"]["outer_radius"]
        self.univ_data["U"]["XAU"]["outer_radius"] = self.univ_data["U"]["IAU"]["radius"] * 4
        self.univ_data["U"]["XAU"]["area"] =\
            (4 * math.pi * (self.univ_data["U"]["XAU"]["outer_radius"] ** 2)) -\
            (self.univ_data["U"]["IAU"]["area"] + self.univ_data["U"]["PLA"]["area"])

    def compute_dark_fluid(self):
        """
        Dark Fluid's force is anti-mass and anti-gravity. It is our very simplistic version of
        Einstein's cosmological constant and combines the theories of dark matter and dark energy into one force.
        For the purpose of this simulation, it is initially the total "mass" of the Universe, as computed in the
        BigBang module, minus the total "mass" (area) of the regular and super galactic clusters.
        As the simulation progresss, we will "squeeze" and "extrude" the Dark Fluid into the IAU, PLA and XAU,
        in order to represent a sophomoric view of Universe expansion.
        """
        self.univ_data["U"]["DF"] = dict()
        self.univ_data["U"]["DF"]["mass"] = self.univ_data["U"]["mass"] -\
                                            self.univ_data["SG"]["mass"] + self.univ_data["RG"]["mass"]

    def identify_overlaps(self):
        """
        For clusters in the IAU (Initial Universe Area), identify how close each is to other by:
            origin point (center of spheres)
            nearest perimeter (surface of sphere)
        And identify which ones overlap with which other ones.
        """
        # Identify all cluster inter-relationships
        for cname, _ in self.univ_data["C"].items():
            clcnm = self.univ_data["C"][cname]
            # Location qualities of the cluster
            # This will become more important as we move out of the IAU.
            clcnm['zone'] = 'iau'

            # Movement qualities of the cluster
            # Coordinates of movement targets inside PLA, XAU zones and beyond the XAU
            targets = {2:'pla_1', 3:'pla_2', 4:'xau_1', 5:'xau_2'}
            clcnm['tgt'] = dict()
            for tgt_factor, tgt_nm in targets.items():
                clcnm['tgt'][tgt_nm] = {'x': clcnm['loc']['x'] * tgt_factor,
                                        'y': clcnm['loc']['y'] * tgt_factor,
                                        'z': clcnm['loc']['z'] * tgt_factor}
            # Amt actully moved per frame and in what direction is combo of move_force, anti_move_force, g_forces, anti_g_forces

            # 'Natural' force moving clusters toward their next target.  Smaller = faster.  Bigger = slower.
            # This number means we want to move from the current location to the next target in X number of "steps".
            # This leaves room to adjust the number of steps per animation frame or game turn.
            # My fake physics says that super clusters "expand into the Universe" more slowly than regular clusters and, by
            #  extension, that the rate of such "expansion" is inversely proportional to the "total mass" of the cluster.
            # My expectation would be to re-calculate the move_force once we've arrived at a spot near the target.
            adj_by_mass = clcnm['mass'] / 100
            clcnm["move_force"] = (1000.0 + adj_by_mass) if clcnm['type'] == "SG" else (700.00  + adj_by_mass)
            # Anti-move force due to dark fluid. Pct of move_force
            # The anti_move_force is a pct that slows down the move_force.
            # I want the anti_move_force to get stronger as the universe expands.
            # For now I'll set it according to what zone the cluster is in.
            df_anti_move = {'iau': 0.1, 'pla_1': 0.2, 'pla_2': 0.4, 'xau_1': 0.8, 'xau_2': 1.6}
            clcnm["anti_move_force"] = df_anti_move[clcnm['zone']]

            # Expected 'natural' size of radius at target
            # The expectation is that the cluster would grow towards this size incrementally, a little each step or turn
            # Other factors should adjust its shape; this is only for "natural" growth (interanl expansion)
            # The grow_force is set at what the expected size of radius would be upon arrival at/near next target zone coords.
            # Make it more sophisticated eventually...
            clcnm["grow_force"] = clcnm["radius"] + (clcnm["radius"] * 0.3)
            # Anti-growth size force. Pct of grow_force
            # Going to have it weaken somewhat as universe expands
            df_anti_grow = {'iau': 0.2, 'pla_1': 0.1, 'pla_2': 0.05, 'xau_1': 0.02, 'xau_2': 0.005}
            clcnm["anti_grow_force"] = df_anti_grow[clcnm['zone']]

            # Relationships with other clusters:
            clcnm["to"] = dict()
            for cnm_to, _ in self.univ_data["C"].items():
                clcto = self.univ_data["C"][cnm_to]
                if cnm_to != cname:
                    # distance is from clusters center-to-center
                    # g_force is current gravitational attraction between 2 clusters
                    #   expressed in terms of distance movement per frame
                    # fluid_g_force is anti-g_force per frame; as distance per frame or factor reducing g_force
                    # touch is True if they share even one pixel
                    # postive touch_dist = smallest distance between sphere surfaces
                    # negative touch_dist = maximum overlap amount between sphere surfaces
                    clcnm["to"][cnm_to] = {'dist': 0.0, 'g_force': 0.0, 'anti_g_force': 0.0, 'touch': False, 'touch_dist': 0.0}

                    # Distance formula (in Mega parsecs)
                    clcnm["to"][cnm_to]['dist'] = math.sqrt(((clcnm['loc']['x'] - clcto['loc']['x']) ** 2) +\
                                                            ((clcnm['loc']['y'] - clcto['loc']['y']) ** 2) +\
                                                            ((clcnm['loc']['z'] - clcto['loc']['z']) ** 2))
                    # Gravity force
                    # For the purpose of this game, we're going to assume that "mass" is in kg / 10 ** 24
                    # In other words, when we say the cluster mass is 23456, we mean it is 23456e24 kg
                    # For the distance amounts used so far (in IAU space), first note....
                    # Gigaparse = One billion parsecs
                    # Megaparsec = One million parsecs
                    # Kpc = Kiloparse. One thousand parsecs.
                    # pc = A parsec is about 3.26 light years (3.086 × 10**13 kilometers) (3.086 x 10**16 meters)
                    # Mpc = Milliparsec. One thousandth of a parsec.
                    # ... and that the Milky Way galaxy is about 8 Kpc across.
                    # A typical distance between nearby galaxies ranges from 8 Kpc (or less) to 800 Kpc (or more),
                    #    for an avg distance of maybe 110 Kpc in the case of the Milky Way
                    # A galactic cluster occupies 1-3 Mega pc (1-3 million parsecs)
                    # Distance between "nearby" galactic clusters is on the order of 80-200 Million parces (8-20 Mega pc)
                    # May need to tweak it a bit, but basically the distances between clusters should be considered Mega pc
                    # 1 Mega pc = 3.086 × 10**13 x 10**6 km = 3.086 x 10**19 km = 3.086 x 10**22 m (meters)
                    # Gravity: Every point mass attracts every single other point mass by a force acting along the line intersecting
                    #   both points. The force is proportional to the product of the two masses and inversely proportional to the
                    #   square of the distance between them.
                    # G is the gravitational constant (6.674×10**11 Newtons · (m/kg)**2)
                    # m1 is the first mass (in kg); m2 is the second mass (in kg)
                    # r is the distance between the center of the masses (in m)
                    # F is the gravitational force between them (in Newtons)
                    # F = G((m1 * m1)/r)
                    # There are a number of other factors to consider to fully understand 2-body and 3-body problems
                    #  and plenty of text books included game/animation guides to help with this. For now I am just goofing
                    #  around. It is also the case that galactic clusters are so far apart that g-forces between them are
                    #  typically minimal to negligible. For galaxies inside clusters, it is a different story.
                    # How this force works to affect attraction is another question.
                    dist_in_meters = clcnm["to"][cnm_to]['dist'] * 3.086 * 10**22
                    two_masses_mult = (clcnm['mass'] * 10**24) * (clcto['mass'] * 10**24)
                    # FB.log_me("dist_in_meters: {}".format(str(dist_in_meters)), self.log_path, options.loglevel)
                    # FB.log_me("two_masses_mult: {}".format(str(two_masses_mult)), self.log_path, options.loglevel)

                    clcnm["to"][cnm_to]['g_force'] = ((6.674 * 10**11) * (two_masses_mult / dist_in_meters))
                    # Just making up a counter-veiling force here
                    df_anti_grav = {'iau': 0.1, 'pla_1': 0.05, 'pla_2': 0.025, 'xau_1': 0.002, 'xau_2': 0.0002}
                    clcnm["to"][cnm_to]['anti_g_force'] = df_anti_grav[clcnm['zone']]

                    # How do we know if two spheres overlap and by how much?
                    # touch': False, 'touch_dist': 0.0

                    # Two circles intersect if, and only if, the distance between their centers is
                    # between the sum and the difference of their radii. Given two circles
                    # (x0, y0, R0) and (x1, y1, R1), the formula is as follows:

                    # ABS(R0 - R1) <= SQRT((x0 - x1)^2 + (y0 - y1)^2) <= (R0 + R1)
                    # Squaring both sides lets you avoid the slow SQRT,
                    # and stay with ints if your inputs are integers:

                    # (R0 - R1)^2 <= (x0 - x1)^2 + (y0 - y1)^2 <= (R0 + R1)^2

                    # I am guessing this will work for spheres by adding the square of
                    # the difference in their Z coordinates, eg:
                    # If (R0 - R1)^2 <= (x0 - x1)^2 + (y0 - y1)^2  + (z0 - z1)^2 <= (R0 + R1)^2
                    # then they interesect
                    diff_radii_sq = (clcnm['radius'] - clcto['radius'])**2
                    sum_radii_sq =  (clcnm['radius'] + clcto['radius']**2)
                    sum_sqs_coords = (clcnm['loc']['x'] - clcto['loc']['x'])**2 +\
                                     (clcnm['loc']['y'] - clcto['loc']['y'])**2 +\
                                     (clcnm['loc']['z'] - clcto['loc']['z'])**2
                    clcnm['to'][cnm_to]['touch'] = True if diff_radii_sq <= sum_sqs_coords and sum_radii_sq >= sum_sqs_coords \
                                                        else False

            self.univ_data['C'][cname] = clcnm


    def save_start_data(self):
        """
        Write GXDB record to memory file
        """
        FB.write_que(self.data_path, self.univ_nm, self.univ_data)
