import unittest
import pygame as pg
import random
from io_data import Astro
from io_data import CompareRect

pg.init()     # Initialize PyGame for use in this module


class TestAstro(unittest.TestCase):

    def test_galaxy_name_parts(self):
        # Test galaxy name part generation
        adj = Astro.GADJ
        item = Astro.GITM
        name = Astro.GNAM

        adj_name = random.choice(adj)
        item_name = random.choice(item)
        name_name = random.choice(name)

        # full_name = f"{adj_name} {item_name} {name_name}"
        self.assertIn(adj_name, Astro.GADJ)
        self.assertIn(item_name, Astro.GITM)
        self.assertIn(name_name, Astro.GNAM)

    def test_constants(self):
        # Test some key constants
        self.assertEqual(Astro.DEP, 0.683)
        self.assertEqual(Astro.DMP, 0.274)
        self.assertEqual(Astro.BMP, 0.043)
        self.assertEqual(Astro.TUV, 415000)

    def test_conversions(self):
        # Test some key conversions
        self.assertEqual(Astro.AU_TO_KM, 1.495979e+8)
        self.assertEqual(Astro.LS_TO_LM, 0.000000000000105)


class TestCompareRect(unittest.TestCase):

    def setUp(self):
        self.comp = CompareRect()

    def test_rect_contains(self):
        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(2, 2, 5, 5)
        self.assertTrue(self.comp.rect_contains(r1, r2))

        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(20, 20, 5, 5)
        self.assertFalse(self.comp.rect_contains(r1, r2))

        r1 = pg.Rect(10, 10, 0, 0)
        r2 = pg.Rect(10, 10, 0, 0)
        self.assertTrue(self.comp.rect_contains(r1, r2))

    def test_rect_overlaps(self):
        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(5, 5, 5, 5)
        self.assertTrue(self.comp.rect_overlaps(r1, r2))

        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(20, 20, 5, 5)
        self.assertFalse(self.comp.rect_overlaps(r1, r2))

        r1 = pg.Rect(10, 10, 0, 0)
        r2 = pg.Rect(10, 10, 0, 0)
        self.assertTrue(self.comp.rect_overlaps(r1, r2))

    def test_rect_borders(self):
        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(10, 0, 10, 10)
        self.assertTrue(self.comp.rect_borders(r1, r2))

        r1 = pg.Rect(0, 0, 10, 10)
        r2 = pg.Rect(20, 20, 10, 10)
        self.assertFalse(self.comp.rect_borders(r1, r2))

        r1 = pg.Rect(10, 10, 0, 0)
        r2 = pg.Rect(10, 10, 0, 0)
        self.assertTrue(self.comp.rect_borders(r1, r2))

    def test_rect_same(self):
        r1 = pg.Rect(10, 10, 10, 10)
        r2 = pg.Rect(10, 10, 10, 10)
        self.assertTrue(self.comp.rect_same(r1, r2))

        r1 = pg.Rect(10, 10, 10, 10)
        r2 = pg.Rect(10, 11, 10, 10)
        self.assertFalse(self.comp.rect_same(r1, r2))

        r1 = pg.Rect(10, 10, 0, 0)
        r2 = pg.Rect(10, 10, 0, 0)
        self.assertTrue(self.comp.rect_same(r1, r2))


if __name__ == '__main__':
    unittest.main()
