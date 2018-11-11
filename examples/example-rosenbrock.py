# -*- coding: utf-8 -*-
from __future__ import print_function
import lahc
import math
import random


class RosenbrockProblem(lahc.LateAcceptanceHillClimber):
    """Defines the Rosenbrock problem.

        f(x, y) = (a-x)**2 + b(y-x**2)**2

    Global minima is located at (x, y) = (a, a**2) for b > 0
    """
    def __init__(self, initial_state, a=25, b=100):
        super(RosenbrockProblem, self).__init__(initial_state=initial_state)
        self.rosenbrock_a = a
        self.rosenbrock_b = b

    def move(self):
        A = random.normalvariate(0, 1)
        theta = random.random() * 2. * math.pi
        self.state[0] += A * math.cos(theta)
        self.state[1] += A * math.sin(theta)

    def energy(self):
        x, y = self.state[0], self.state[1]
        a, b = self.rosenbrock_a, self.rosenbrock_b
        return (a - x)**2 + b*(y - x**2)**2

    @property
    def exact_solution(self):
        return [self.rosenbrock_a, self.rosenbrock_a**2]


if __name__ == '__main__':
    # guessing a solution
    initial_state = [-5.0, 5.0]

    # adjust the history length and update interval
    lahc.LateAcceptanceHillClimber.history_length = 5000
    lahc.LateAcceptanceHillClimber.updates_every = 1000

    # initializing the problem
    prob = RosenbrockProblem(initial_state)

    # and run the Late Acceptance Hill Climber for a solution
    prob.run()

    # compare found solution to exact solution
    print()
    print(prob.state, prob.exact_solution)
    print(
        "Solution with `deepcopy` strategy in: {0:.1f}s".format(
            prob.time_end - prob.time_start))
    print()


    # The default behavoir of the algorithm is to use STL copy.deepcopy
    # method, which is known to be slow at copying lists compared to
    # slicing the list. Let us try the same problem with the slicing
    # strategy.
    prob_slice = RosenbrockProblem(initial_state)
    prob_slice.copy_strategy = 'slice'

    prob_slice.run()
    print()
    print(prob.state, prob.exact_solution)
    print(
        "Solution with `slice` strategy in: {0:.1f}s".format(
            prob_slice.time_end - prob_slice.time_start))
