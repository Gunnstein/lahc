# -*- coding: utf-8 -*-
from __future__ import print_function
import lahc
import math
import random


class RosenbrockProblem(lahc.LateAcceptanceHillClimber):
    """Defines the Rosenbrock problem.

        f(x, y) = (a-x)**2 + b(y-x**2)**2

    Exact solution is found at (a, a**2) for b > 0
    """
    def __init__(self, initial_state, a=1, b=100):
        self.rosenbrock_a = a
        self.rosenbrock_b = b
        super(RosenbrockProblem, self).__init__(initial_state=initial_state)

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

    # initializing the problem
    problem = RosenbrockProblem(initial_state)
    problem.rosenbrock_a = 25

    # adjust the history length and update interval
    problem.history_length = 5000
    problem.updates_every = 1000

    # and run the Late Acceptance Hill Climber for a solution
    problem.run()

    print()

    # compare found solution to exact solution
    print(problem.state, problem.exact_solution)
