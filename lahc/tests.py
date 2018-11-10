# -*- coding: utf-8 -*-
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
from ._lahc import LateAcceptanceHillClimber
import math
import os
import random
import tempfile
import unittest


class LAHC(LateAcceptanceHillClimber):
    def move(self):
        A = random.normalvariate(0, 1)
        theta = random.random() * 2. * math.pi
        self.state[0] += A * math.cos(theta)
        self.state[1] += A * math.sin(theta)

    def energy(self):
        x = self.state[0]
        y = self.state[1]
        E = (x-2.)**2 + (y-5.)**2
        return E

    def update(self, *args, **kwargs):
        pass


class TestLateAcceptanceHillClimber(unittest.TestCase):
    def setUp(self):
        self.x0 = [11.0, 0.7]
        self.x1 = [2.0, 5.0]
        self.E1 = 0.

    def test_greedy_hc(self):
        solver = LAHC(self.x0)
        solver.history_length = 1
        x1, E1 = solver.run()
        self.my_assertListAlmostEqual(x1, self.x1, places=3)
        self.assertAlmostEqual(E1, self.E1, places=3)

    def my_assertListAlmostEqual(self, a, b, places=7):
        self.assertEqual(len(a), len(b))
        for ai, bi in zip(a, b):
            self.assertAlmostEqual(ai, bi, places=places)

    def test_save_load_state(self):
        solver = LAHC(self.x0)
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = os.path.join(tmpdirname, "test.state")
            solver.save_state(fname=fname)
            solver2 = LAHC(load_state=fname)
        self.my_assertListAlmostEqual(solver.state, solver2.state)


if __name__ == "__main__":
    unittest.main()
