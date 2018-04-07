# -*- coding: utf-8 -*-
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import numpy as np
from ._lahc import LateAcceptanceHillClimber
import unittest


class LAHC(LateAcceptanceHillClimber):
    def move(self):
        A = .001
        theta = np.random.random() * 2.*np.pi
        self.state += np.array([A*np.cos(theta), A*np.sin(theta)])

    def energy(self):
        x = self.state[0]
        y = self.state[1]
        E = x**2 + x*y + y**2
        return E

    def update(self, *args, **kwargs):
        pass


class TestLateAcceptanceHillClimber(unittest.TestCase):
    def setUp(self):
        self.x0 = np.array([1.0e1, 0.7])
        self.x1 = np.array([0., 0.])
        self.energy = 0.

    def test_greedy_hc(self):
        solver = LAHC(self.x0)
        solver.history_length = 1
        x1, E = solver.run()
        np.testing.assert_almost_equal(x1, self.x1, decimal=3)
        self.assertAlmostEqual(E, self.energy, places=3)

    def test_save_load_state(self):
        solver = LAHC(self.x0)
        fname = "/tmp/test.state"
        solver.save_state(fname=fname)

        solver2 = LAHC(load_state=fname)

        np.testing.assert_array_equal(solver.state, solver2.state)


if __name__ == "__main__":
    unittest.main()
