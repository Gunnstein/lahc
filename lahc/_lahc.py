# -*- coding: utf-8 -*-
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import abc
import copy
import datetime
import pickle
import signal
import sys
import time

__all__ = ["LateAcceptanceHillClimber", "SolutionHistoryMixIn"]


class LateAcceptanceHillClimber(object):
    """Abstract class for Late Acceptance Hill climbing heuristic.

    The Late Acceptance Hill Climbing (LAHC) heuristic is an extension of the
    simple Hill Climber where worse solutions can be accepted during the
    solution process based on the solution history. In contrast to several
    other metaheuristics it only relies on a single parameter (the history
    length) but has still shown to be competitive with more complex heuristics
    for many applications.

    For more information see

        E. K. Burke, Y. Bykov, The late acceptance Hill-Climbing heuristic.
        European Journal of Operational Research. 258, 70–78 (2017).

    Any subclass of this abstract class should define the following methods:

        `move`   : Change the state (move to a neighbor state)
        `energy` : Return the energy of the state


    The implementation relies heavily on copying state, the default copy
    strategy (copy_strategy='deepcopy') uses the STL copy.deepcopy function
    that is slow for many data structures. Large performance gains can be
    obtained using slicing for list type structures or by providing your own
    copying method for the state.


    Acknowledgements
    ----------------
    This implementation is heavily influenced by the `simanneal` project
    which implements the Simulated Annealing heuristic, another
    widely used and successful metaheuristic. Check out the `simanneal`
    project at

        https://github.com/perrygeo/simanneal
    """
    __metaclass__ = abc.ABCMeta

    # defaults
    steps_minimum = 100000
    steps_idle_fraction = 0.02
    history_length = 5000
    updates_every = 100
    copy_strategy = 'deepcopy'
    save_state_on_exit = False

    def __init__(self, initial_state=None, load_state=None):
        """Initializer for the class.

        Either initial_state or load_state must be given.

        Arguments
        ---------
        initial_state : Optional

        load_state : Optional[str]
            Uses the load_state method to load state from a pickle file.
        """
        if initial_state is not None:
            self.state = self.copy_state(initial_state)
        elif load_state:
            self.load_state(load_state)
        else:
            raise ValueError('No valid values supplied for neither \
            initial_state nor load_state')

        # placeholders
        self.step = None
        self.step_idle = None
        self.best_state = None
        self.best_energy = None
        self.best_step = None
        self.time_start = None
        self.time_end = None

        self.user_exit = False
        signal.signal(signal.SIGINT, self.set_user_exit)

    @abc.abstractmethod
    def move(self):
        """Change state"""
        pass

    @abc.abstractmethod
    def energy(self):
        """Return state energy"""
        pass

    def terminate_search(self):
        """Terminate the loop in run method.

        Override for customization of termination criteria for
        search.
        """
        return ((self.step > self.steps_minimum)
                and (self.step_idle > self.step*self.steps_idle_fraction))

    def run(self):
        """Minimize the energy of the system by Late Acceptance Hill Climbing.

        Returns
        -------
            (state, energy) : the best state and energy found
        """
        self.time_start = time.time()
        self.step = 0
        self.step_idle = 0

        E = self.energy()

        prev_state = self.copy_state(self.state)
        prev_energy = E

        self.best_state = self.copy_state(self.state)
        self.best_energy = E
        self.best_step = 0
        self.energy_history = [E] * self.history_length
        Ehmean = E
        Ehvar = 0.
        Nvar = float(max(self.history_length - 1, 1))

        steps_since_update = 0
        if self.updates_every > 0:
            self.update(self.step, self.step_idle, E, Ehmean, Ehvar)

        while not self.terminate_search() and not self.user_exit:
            self.move()
            E = self.energy()
            steps_since_update += 1

            if E >= prev_energy:
                self.step_idle += 1
            else:
                self.step_idle = 0

            v = self.step % self.history_length
            Ev = self.energy_history[v]
            if E < Ev or E <= prev_energy:
                # accept candidate state
                prev_state = self.copy_state(self.state)
                prev_energy = E

                if E < self.best_energy:
                    self.best_state = self.copy_state(self.state)
                    self.best_energy = E
                    self.best_step = self.step
            else:
                # restore previous state
                self.state = self.copy_state(prev_state)
                E = prev_energy

            if E < Ev:
                # Update energy history
                self.energy_history[v] = E

                # and its mean and variance
                dE = E - Ev
                Ehmean_old = Ehmean

                Ehmean += dE / self.history_length
                Ehvar += dE * (E-Ehmean+Ev-Ehmean_old) / Nvar

            self.step += 1
            if steps_since_update == self.updates_every:
                self.update(self.step, self.step_idle, E, Ehmean, Ehvar)
                steps_since_update = 0

        self.state = self.copy_state(self.best_state)
        if self.save_state_on_exit:
            self.save_state()

        self.time_end = time.time()
        return self.best_state, self.best_energy

    def update(self, *args, **kwargs):
        """Wrapper for internal update. """
        self.default_update(*args, **kwargs)

    def default_update(self, step, step_idle, E, Ehmean, Ehvar):
        """Default update, outputs to stderr.

        Prints the number of idle steps, current energy, energy history mean,
        energy history coefficient of variation (CoV) and elapsed time.

        The CoV indicates the variance in the history buffer. The CoV will
        tend towards zero when the search is close to a minimum and can be
        used as a indicator of time until the search is terminated.
        """
        if step == 0:
            s0 = "{0:>12s}{1:>12s}{2:>12s}{3:>12s}{4:>12s}"
            print(s0.format("Idle steps", "Energy", "Hist. Mean", "Hist. CoV",
                            "Elapsed"), file=sys.stderr)
        telapsed = time.strftime(
            "%H:%M:%S", time.gmtime(time.time() - self.time_start))
        s1 = "\r{0:>12n}{1:>12.2e}{2:>12.2e}{3:>11.2f}%{4:>12s}"
        print(s1.format(step_idle, E, Ehmean,
                        Ehvar**.5 / Ehmean * 100,
                        telapsed), file=sys.stderr, end="\r")
        sys.stderr.flush()

    def set_user_exit(self, signum, frame):
        """Raises the user_exit flag, further iterations are stopped.
        """
        self.user_exit = True

    def copy_state(self, state):
        """Returns an exact copy of the provided state

        Implemented according to self.copy_strategy, one of
        * deepcopy : use copy.deepcopy (slow but reliable)
        * slice: use list slices (faster but only works if state is list-like)
        * method: use the state's copy() method
        """
        if self.copy_strategy == 'deepcopy':
            return copy.deepcopy(state)
        elif self.copy_strategy == 'slice':
            return state[:]
        elif self.copy_strategy == 'method':
            return state.copy()
        else:
            s = 'No implementation found for the self.copy_strategy "{0:s}"'
            raise RuntimeError(s.format(self.copy_strategy))

    def save_state(self, fname=None):
        """Save state to pickle file

        Arguments
        ---------
        fname : Optional[str]
            If a filename is not provided, the current date time is assigned.
        """
        if not fname:
            date = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
            fname = date + "_LAHC" + ".state"
        with open(fname, "wb") as fh:
            pickle.dump(self.state, fh)

    def load_state(self, fname):
        """Loads state from pickle

        Arguments
        ---------
        fname : str
            The filename of the pickle file.
        """
        with open(fname, 'rb') as fh:
            self.state = pickle.load(fh)


class SolutionHistoryMixIn(object):
    """Store the solution history on update.

    Use this mixin to complement the `update` method and store the
    solution history in a list named `solution_history`.

    """
    def update(self, *args, **kwargs):
        if self.step == 0:
            self.solution_history = []
        self.solution_history.append(args)
        super(SolutionHistoryMixIn, self).update(*args, *kwargs)
