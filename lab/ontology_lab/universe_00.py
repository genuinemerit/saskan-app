#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module defines Class AppUniverse and related Classes for
handling in-memory data structures, constraints, definitions and
rules relating to the structure of the game Universe.
"""
# python packages
import locale
import math
import random

# ==============================================
class Universe(object):
    """
    Contains objects, structures and methods for storing data about the
    game Universe in memory.
    Methods in this class control how the 'physical' game Universe
    is constructed and behaves.
    """
    def __init__(self, uname='Void'):
        """
        Set up a new Universe, you gods-like player you.

        Args:
            uname:  Name for this Universe
        """
        # Universe-level items
        # ---------------------------
        ## Regular Galactic Clusters
        self.reggx = {"minpct": 1.0, "maxpct": 5.0,
                      "sectpct": 0.0, "cntpct": 0.0,
                      "mincnt": 1, "maxcnt": 100, "actcnt": 0,
                      "rgx": {}}
        ## Galactic Super Clusters
        self.supergx = {"minpct": 1.0, "maxpct": 5.0,
                        "sectpct": 0.0, "cntpct": 0.0,
                        "mincnt": 1, "maxcnt": 50, "actcnt": 0,
                        "sgx": {}}
        ## Total Universe
        self.univ = {"name": uname, "emptyPct": 0.0, "stats": {}}

        # Galaxy Super-cluster items
        # Galaxy Cluster items
        # Galaxy Cloud items
        # Galaxy items

    # Methods relating directly to the Universe as a Whole
    # =====================================================
    def set_supergx_sector_pct(self, apptxts, gxsteps):
        """
        Set pct of Universe occupied by galactic super clusters.
        This tells us, of the total space, how much of it is occupied by
        Galactic Super Clusters.  Another way to consider it is that this
        tells us what percent of sectors of the Universe contain Galactic
        Super Clusters.

        Args:
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        Returns:
            boolean
        """
        # Compute a random percent between min and max
        float_num = random.random()
        int_num = random.randrange(self.supergx["minpct"],
                                   self.supergx["maxpct"])
        self.supergx["sectpct"] = float(int_num + float_num)
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["superClusterSectorPct"],
                         locale.format("%.4f", self.supergx["sectpct"],
                                       grouping=True))
        return True

    def set_reggx_sector_pct(self, apptxts, gxsteps):
        """
        Set pct of Universe occupied by regular super clusters.
        This tells us, of the total space, how much of it is occupied by
        Regular Galactic Clusters. Another way to consider it is that this
        tells us what percent of sectors of the Universe contain regular
        Galactic Clusters.

        Args:
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        Returns:
            boolean
        """
        # Compute a random percent between min and max
        float_num = random.random()
        int_num = random.randrange(self.reggx["minpct"],
                                   self.reggx["maxpct"])
        self.reggx["sectpct"] = float(int_num + float_num)
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["regularClusterSectorPct"],
                         locale.format("%.4f", self.reggx["sectpct"],
                                       grouping=True))
        return True

    def set_empty_univ_pct(self, apptxts, gxsteps):
        """
        Set pct of Universe that contains no galactic clusters.
        This tells us, of the total space, how much of it is empty, meaning
        that it contains no Galactic Clusters of any kind.  Another way to
        think about it is that this tells us what percentage of sectors of
        the Universe are empty of galaxies.

        Args:
            msgs:       Message-handling object
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        """
        # If Cluster percentages not set, then randomize them
        if self.supergx["sectpct"] == 0.0:
            self.set_supergx_sector_pct(apptxts, gxsteps)
        if self.reggx["sectpct"] == 0.0:
            self.set_reggx_sector_pct(apptxts, gxsteps)
        # Compute based on Cluster percentages
        self.univ["emptyPct"] = float(100.0 - \
                                (self.supergx["sectpct"] + \
                                 self.reggx["sectpct"]))
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["emptySectorPct"],
                         locale.format("%.4f", self.univ["emptyPct"],
                                       grouping=True))

    def set_supergx_pct(self, apptxts, gxsteps):
        """
        Set the percentage of all Galactic Clusters that are Super Clusters.
        The previous calculation told us how much space is occupied by
        Super Clusters.  We can consider that that calc will define what
        sectors of the Universe contains Super Clusters.  This calculation
        will determine how sparsely or densely those sectors will be
        populated by Super Clusters.

        Determine the ratio of Super Cluster Pct of Univ to Regular galaxies
        pct of Univ. This ratio provides boundaries around min and max pct
        of total galaxies that are super clusters.

        The computation of this value will lead to the calculation of the
        total number of super clusters in the Universe.

        Args:
            msgs:       Message-handling object
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        """
        # If EmptyUniversePct percentage not set, then randomize it
        if self.univ["emptyPct"] == 0.0:
            self.set_empty_univ_pct(apptxts, gxsteps)
        # Get ratio of super cluster sections to regular cluster sectors
        gxratio = self.supergx["sectpct"] / self.reggx["sectpct"]
        # Set desired boundaries for min and max
        sgxpct = {"min": gxratio * 35, "max": gxratio * 43}
        sgxpct["min"] = 5.0 if sgxpct["min"] < 5.0 else sgxpct["min"]
        sgxpct["max"] = 95.0 if sgxpct["max"] > 95.0 else sgxpct["max"]
        float_num = random.random()
        int_num = random.randrange(math.floor(sgxpct["min"]),
                                   math.floor(sgxpct["max"]))
        pct = float(int_num + float_num)
        # Adjust pct to min and max
        if pct < sgxpct["min"]:
            pct = sgxpct["min"]
        if pct > sgxpct["max"]:
            pct = sgxpct["max"]
        self.supergx["cntpct"] = float(pct)
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["superClusterCountPct"],
                         locale.format("%.4f", self.supergx["cntpct"],
                                       grouping=True))

    def set_reggx_pct(self, apptxts, gxsteps):
        """
        Set the percentage of all Galactic Clusters that are Regular Clusters.
        The previous calculation told us how much space is occupied by
        Regular Clusters.  We can consider that that calc will define what
        sectors of the Universe contain Regular Clusters.  This calculation
        will determine how sparsely or densely those sectors will be
        populated by Regular Clusters. Derived from percentage of super
        clusters.

        The computation of this value will lead to the calculation of the
        total number of regular galactic clusters in the Universe.

        Args:
            msgs:       Message-handling object
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        """
        # If pct of Galaxies that are Super Clusters is not set, randomize it
        if self.supergx["cntpct"] == 0.0:
            self.set_supergx_pct(apptxts, gxsteps)
        self.reggx["cntpct"] = float(100.0 - self.supergx["cntpct"])
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["regularClusterCountPct"],
                         locale.format("%.4f", self.reggx["cntpct"],
                                       grouping=True))

    def set_supergx_cnt(self, apptxts, gxsteps):
        """
        Compute the number of galactic super clusters in the Universe

        Args:
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        """
        # Compute a random integer between min and max
        int_cnt = random.randrange(self.supergx["mincnt"],
                                   self.supergx["maxcnt"] + 1)
        self.supergx["actcnt"] = math.floor(int_cnt)
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["superClusterCnt"],
                         locale.format("%.4f", self.supergx["actcnt"],
                                       grouping=True))

    def set_reggx_cnt(self, apptxts, gxsteps):
        """
        Compute the number of regular galactic clusters in the Universe

        Args:
            apptxts:    App Texts dict
            gxsteps:    Galaxy computation steps
        """
        # If count of super clusters not set, then randomize it
        if self.supergx["actcnt"] == 0.0:
            self.set_supergx_cnt(apptxts, gxsteps)
        # Compute ratio of Regular to Super Clusters
        gxratio = float(self.reggx["cntpct"] / self.supergx["cntpct"])
        self.reggx["actcnt"] = math.ceil(gxratio * self.supergx["actcnt"])
        # Save the value in the step values dict
        step = gxsteps.get_step()
        gxsteps.set_value(step["num"], apptxts["regularClusterCnt"],
                         locale.format("%.4f", self.reggx["actcnt"],
                                       grouping=True))

# ==============================================
# class SuperCluster:
#    """
#    Defines data, rules and methods associated with Galactic Super Clusters.
#    """
#    def __init__(self):
#        """
#        Initialize a new SuperCluster object.
#        """
#        self.Id = ''
#        self.Name = ''
#        self.Description = ''
#        self.ParentId = ''

