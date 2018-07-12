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

__all__ = ["LateAcceptanceHillClimber"]


def time_string(seconds):
    """Returns time in seconds as a string formatted HHHH:MM:SS."""
    s = int(round(seconds))  # round to nearest second
    h, s = divmod(s, 3600)   # get hours and remainder
    m, s = divmod(s, 60)     # split remainder into minutes and seconds
    return '%4i:%02i:%02i' % (h, m, s)


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
    This implementation is heavily influenced by the simanneal project found at

        https://github.com/perrygeo/simanneal

    which implements the Simulated Annealing heuristic.
    """

    __metaclass__ = abc.ABCMeta

    # defaults
    steps_min = 100000
    idle_steps_fraction = 0.02
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
        self.start = None

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

        Provide own implementation if necessary.
        """
        return ((self.step > self.steps_min)
                and (self.step_idle > self.step*self.idle_steps_fraction))

    def run(self):
        """Minimize the energy of the system by Late Acceptance Hill Climbing.

        Returns
        -------
            (state, energy) : the best state and energy found
        """
        self.step = 0
        self.step_idle = 0
        self.start = time.time()

        E = self.energy()

        prev_state = self.copy_state(self.state)
        prev_energy = E

        self.best_state = self.copy_state(self.state)
        self.best_energy = E
        self.best_step = 0
        self.energy_history = [E] * self.history_length

        trials = 0
        self.update(self.step, self.step_idle, E)

        while not self.terminate_search() and not self.user_exit:
            self.move()
            E = self.energy()
            trials += 1

            if E >= prev_energy:
                self.step_idle += 1
            else:
                self.step_idle = 0

            v = self.step % self.history_length
            if E < self.energy_history[v] or E <= prev_energy:
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
            if E < self.energy_history[v]:
                self.energy_history[v] = E
            self.step += 1
            if trials == self.updates_every:
                self.update(self.step, self.step_idle, E)
                trials = 0
        self.state = self.copy_state(self.best_state)
        if self.save_state_on_exit:
            self.save_state()

        # Return best state and energy
        return self.best_state, self.best_energy

    def update(self, *args, **kwargs):
        """Wrapper for internal update. """
        self.default_update(*args, **kwargs)

    def default_update(self, step, step_idle, E):
        """Default update, outputs to stderr.

        Prints the current number of idle steps, energy, acceptance rate,
        improvement rate, elapsed time, and remaining time.

        The acceptance rate indicates the percentage of moves since the last
        update that were accepted.  It includes moves that decreased the
        energy, moves that left the energy unchanged, and moves that increased
        the energy by late acceptance.

        The improvement rate indicates the percentage of moves since the
        last update that strictly decreased the energy.  Initially it will
        include both moves that improved the overall state and moves that
        simply undid previously accepted moves that increased the energy.
        It will tend toward zero as the moves that can decrease the energy
        are exhausted and moves that would increase the energy are no longer
        present in the history buffer for late acceptance."""
        elapsed = time.time() - self.start
        s0 = "{0:>12s}{1:>12s}{2:>12s}{3:>12s}{4:>12s}{5:>12s}"
        s1 = "\r{0:>12n}{1:>12.2e}{2:>12s}"
        s2 = "\r{0:>12n}{1:>12.3e}{2:>11.2f}%{3:>11.2f}%{4:>12s}{5:>12s}\r"

        if step == 0:
            print(s0.format(
                "Idle steps", "Energy", "Accept", "Improve", "Elapsed",
                "Remaining"), file=sys.stderr)
            print(s1.format(step_idle, E, time_string(elapsed)),
                  file=sys.stderr, end="\r")
            sys.stderr.flush()
        else:
            remain = (self.steps_min - step) * (elapsed / step)
            print(s2.format(
                step_idle, E, 100.0 * 1, 100.0 * 1,
                time_string(elapsed), time_string(remain)), file=sys.stderr,
                end="\r")
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
