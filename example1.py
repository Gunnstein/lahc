# -*- coding: utf-8 -*-
from __future__ import print_function
import math
import random
from lahc import LateAcceptanceHillClimber


import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.rc('figure', dpi=144)
plt.rc('text', usetex=False)
plt.style.use('classic')


class Graph(object):
    def __init__(self, axes=None):
        if axes is None:
            self.figure, self.axes = plt.subplots()
        else:
            self.figure = axes.figure
            self.axes = axes
        self.xdata, self.ydata = [], []
        self.line, = self.axes.plot([], [], 'k-', lw=1.0)

        self.axes.set(xlabel='Iterations', ylabel='Energy')
        self.axes.grid(True)
        self.canvas = self.figure.canvas
        self.figure.show()
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.axes.bbox)

    def update_graph(self, x, y):
        self.xdata.append(x)
        self.ydata.append(y)
        if x % 1000 == 0:
            self.relim(x, y)
        self.line.set_data(self.xdata, self.ydata)
        self.canvas.restore_region(self.background)
        self.axes.draw_artist(self.line)
        self.canvas.blit(self.axes.bbox)

    def relim(self, x, y):
        if x > 0:
            nu = 10**max(int(math.log10(x)), 3)
        else:
            nu = 10**3
        n = ((x // nu)+1) * nu
        self.axes.set(xlim=(0, n), ylim=(0, max(self.ydata)))


def distance(a, b):
    """Calculates distance between two latitude-longitude coordinates."""
    R = 3963  # radius of Earth (miles)
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    return R * math.acos(
        math.sin(lat1) * math.sin(lat2) +
        math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2))


class TravellingSalesmanProblem(LateAcceptanceHillClimber, Graph):

    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, distance_matrix, axes=None):
        self.distance_matrix = distance_matrix
        LateAcceptanceHillClimber.__init__(self, initial_state=state)
        Graph.__init__(self, axes=axes)

    def move(self):
        """Swaps two cities in the route."""
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """Calculates the length of the route."""
        e = 0
        for i in range(len(self.state)):
            e += self.distance_matrix[self.state[i-1]][self.state[i]]
        return e

    def update(self, *args, **kwargs):
        self.default_update(*args, **kwargs)
        self.update_graph(args[0], args[2])


if __name__ == '__main__':

    # latitude and longitude for the twenty largest U.S. cities
    cities = {
        'New York City': (40.72, 74.00),
        'Los Angeles': (34.05, 118.25),
        'Chicago': (41.88, 87.63),
        'Houston': (29.77, 95.38),
        'Phoenix': (33.45, 112.07),
        'Philadelphia': (39.95, 75.17),
        'San Antonio': (29.53, 98.47),
        'Dallas': (32.78, 96.80),
        'San Diego': (32.78, 117.15),
        'San Jose': (37.30, 121.87),
        'Detroit': (42.33, 83.05),
        'San Francisco': (37.78, 122.42),
        'Jacksonville': (30.32, 81.70),
        'Indianapolis': (39.78, 86.15),
        'Austin': (30.27, 97.77),
        'Columbus': (39.98, 82.98),
        'Fort Worth': (32.75, 97.33),
        'Charlotte': (35.23, 80.85),
        'Memphis': (35.12, 89.97),
        'Baltimore': (39.28, 76.62)
    }

    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    # create a distance matrix
    distance_matrix = {}
    for ka, va in cities.items():
        distance_matrix[ka] = {}
        for kb, vb in cities.items():
            if kb == ka:
                distance_matrix[ka][kb] = 0.0
            else:
                distance_matrix[ka][kb] = distance(va, vb)

    tsp = TravellingSalesmanProblem(init_state, distance_matrix)
    tsp.history_length = 30000
    tsp.updates_every = 1000

    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"
    state, e = tsp.run()

    while state[0] != 'New York City':
        state = state[1:] + state[:1]  # rotate NYC to start

    print()
    print("{0:.1f} mile route after {1:n} steps.".format(e, tsp.step-1))
    for city in state:
        print("\t", city)
    plt.show(block=True)
