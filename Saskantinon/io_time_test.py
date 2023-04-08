#!python
"""
:module:    io_time_test.py

:author:    GM (genuinemerit @ pm.me)
e an accurate astro-geo simulator.
"""

import math
import json
import pickle

from dataclasses import dataclass   # fields
from pprint import pformat as pf        # noqa: F401
from pprint import pprint as pp         # noqa: F401

from io_time import TimeIO              # type: ignore

TI = TimeIO()


class TimeIOTest(object):
    """Test Class for TimeIO class.
    """
    def __init__(self):
        """Initialize the class.
        """
        pass

    def test_percents(self):
        """Test per centage computations.
        """
        print(f"{TI.M.DC} to {TI.M.PCT}\n==================")
        for i in (0, 0.0, 10, 10., 0.5, 250, 0.002, 0.025, 0.00025, 0.000025):
            print(i, "-->", TI.dec_to_pct(i))
        print(f"\n{TI.M.PCT} to {TI.M.DC}\n==================")
        for i in (100, 0.50, 2, "2", "2%", "2.5%", "2 %"):
            print(i, "-->", TI.pct_to_dec(i))

    def test_geometry(self):
        """Test geometry computations.
        """
        print(f"{TI.M.DI} to {TI.M.RD}\n==================")
        for d in (0, 23e+10, 12e-3, 6, 3, 1, 5):
            print(d, "-->", TI.diam_to_radius(d))
        print(f"\n{TI.M.RD} to {TI.M.DI}\n==================")
        for r in (0, 23e+10, 12e-3, 6, 3, 1, 5):
            print(r, "-->", TI.radius_to_diam(r))

    def test_weight_and_mass(self):
        """Test weight and mass computations.
        """
        print(f"{TI.M.GM} to {TI.M.KG} default rounding\n==================")
        for g in (0, 5e+10, 3e-3, 27.34, 84734678.2, 5.6e-87):
            print(g, "-->", TI.grams_to_kilos(g))
        print(f"\n{TI.M.GM} to {TI.M.KG} no rounding\n==================")
        for g in (0, 5e+10, 3e-3, 27.34, 84734678.2, 5.6e-87):
            print(g, "-->", TI.grams_to_kilos(g, p_rounding=False))
        print(f"\n{TI.M.KG} to {TI.M.GM}\n==================")
        for k in (0, 5e+10, 3e-3, 27.34, 84734678.2, 5.6e+86):
            print(k, "-->", TI.kilos_to_grams(k))
        print(f"\n{TI.M.KG} to {TI.M.LB}\n==================")
        for k in (0, 5e+10, 3e-3, 27.34, 84734678.2, 5.6e+23):
            print(k, "-->", TI.kilos_to_pounds(k))
        print(f"\n{TI.M.LB} to {TI.M.KG}\n==================")
        for l in (0, 5e+10, 3e-3, 27.34, 84734678.2, 5.6e+23):
            print(l, "-->", TI.pounds_to_kilos(l))
        print(f"\n{TI.M.LB} to {TI.M.OZ}\n==================")
        for l in (12, 8, 0.2, 0.125, 1, 0.5):
            print(l, "-->", TI.pounds_to_oz(l))
        print(f"\n{TI.M.OZ} to {TI.M.LB}\n==================")
        for z in (12, 8, 16, 1, 32, 64, 2.67):
            print(z, "-->", TI.oz_to_pounds(z))
        print(f"\n{TI.M.OZ} to {TI.M.GM}\n==================")
        for z in (12, 8, 16, 1, 32, 64, 2.67, 10):
            print(z, "-->", TI.oz_to_grams(z))
        print(f"\n{TI.M.GM} to {TI.M.OZ}\n==================")
        for g in (100, 25, 10, 0.05, 1, 32, 64, 2.7e-32, 10):
            print(g, "-->", TI.grams_to_oz(g))
        print(f"\n{TI.M.KG} to {TI.M.SM} default rounding\n================")
        for k in (100000, 2.5e+10, 2.7e+32, 10.3e+31, 3.8e+30):
            print(k, "-->", TI.kilos_to_sm(k))
        print(f"\n{TI.M.KG} to {TI.M.SM} no rounding\n================")
        for k in (100000, 2.5e+10, 2.7e+32, 10.3e+31, 3.8e+30):
            print(k, "-->", TI.kilos_to_sm(k, p_rounding=False))
        print(f"\n{TI.M.SM} to {TI.M.KG}\n==================")
        for s in (1, 2.5e-10, 2.7e-32, 10.3e-31, 3.8e-30):
            print(s, "-->", TI.sm_to_kilos(s))

    def test_lengths_earth(self):
        """Test length computations using earthly units.
        """
        print(f"{TI.M.CM} to {TI.M.IN}\n==================")
        for c in (0, 1, 10, 2.54, 100, 12.432, 2.5):
            print(c, "-->", TI.cm_to_inches(c))
        print(f"\n{TI.M.IN} to {TI.M.CM}\n==================")
        for i in (0, 1, 10, 0.3937007874, 100, 12.432, 2.5):
            print(i, "-->", TI.inches_to_cm(i))
        print(f"\n{TI.M.FT} to {TI.M.M}\n==================")
        for f in (0, 1, 3.280839895, 100, 12.5, 3.7e+5):
            print(f, "-->", TI.ft_to_meters(f))
        print(f"\n{TI.M.M} to {TI.M.FT}\n==================")
        for m in (0, 1, 0.3048, 0.1524, 27.9, 2.8e+5):
            print(m, "-->", TI.meters_to_ft(m))
        print(f"\n{TI.M.FT} to {TI.M.IN}\n==================")
        for f in (0, 1, 1/12, 3, 0.5):
            print(f, "-->", TI.ft_to_inches(f))
        print(f"\n{TI.M.IN} to {TI.M.FT} w/rounding \n==================")
        for i in (0, 1, 12, 36, 0.00125, 1.7e-12):
            print(i, "-->", TI.inches_to_ft(i))
        print(f"\n{TI.M.IN} to {TI.M.FT} w/o rounding \n==================")
        for i in (0, 1, 12, 36, 0.00125, 1.7e-12):
            print(i, "-->", TI.inches_to_ft(i, p_rounding=False))

# Run program
if __name__ == '__main__':
    """Run program."""
    TIT = TimeIOTest()
    # TIT.test_percents()
    # TIT.test_geometry()
    # TIT.test_weight_and_mass()
    TIT.test_lengths_earth()


