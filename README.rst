LAHC
====

Implementation of Late Acceptance Hill Climbing (LAHC) algorithm in
python.


Installation
------------

Download the repository to your computer and install, e.g. by **pip**
::
    pip install .


Usage
-----

The package provides a base class for subclassing to a specific
problem. The `move` and `energy` methods must be implemented by the
user before the algorithm is applied. The search is started by calling
the `run` method. The user controls the algorithm by adjusting a
single algorithmic parameter, the history length, and the termination
criteria for the algorithm. See subsection on each of the topics below.

The example is a good place to start using of the package.


The history length
------------------

The behaviour of the LAHC algorithm is governed by a single parameter,
the history length. If the history length is set to one, the LAHC
algorithm is equivalent to a simple greedy Hill Climbing
algorithm. Increasing the history length generally improves the
solution quality and also increases the time to convergence.

Selection of the history length should therefore be based on
requirements for the quality of the solution and time available for
the analysis.

A useful characteristic of the LAHC heuristic is that the runtime to
convergence is roughly proportional to the history length. The runtime
at any history length can therefore easily be estimated after applying
the algorithm at a few different history lengths.

As a general recommendation, start at a low history length and
gradually increase it to determine the runtime and variation in the
estimated results. Select a shorter history length that allows
multiple runs in the time allocated for simulations rather than a
longer history length at with a single run.


Termination criteria
--------------------

The algorithm terminates when the `terminate_search` method evaluates

to `True` or when a interupt signal (Ctrl-C) is sent to the process.
The default behaviour of the `terminate_search` is to terminate the
algorithm when a minimum number of attempts has been made and the
algorithm has not been able to improve the solution for a certain
number of steps. The minimum number of steps and necessary number of
idle iterations can be adjusted with the `steps_minimum` and
`steps_idle_fraction` parameters, respectively.

The default value of the `steps_idle_fraction` (0.02) is generally a
good choice for a variety of problems, but the default `steps_minimum`
value (100000) may have to be adjusted depending on the problem. As a
general recommendation, the user should reduce the `step_minimum`
parameter if the algorithm consistently terminates at `steps_minimum`
after running for a long period without improving the solution.

Note that the user can also apply alternative termination criteria by
implementing his own `terminate_search` method.


Acknowledgements
----------------

The package is heavily influenced by the
`simanneal<https://github.com/perrygeo/simanneal>`_ project, which
implements the Simulated Annealing metaheuristic, another widely used
and sucessful optimization method.


Support
-------

Please `open an issue<https://github.com/Gunnstein/lahc/issues/new>`_ for support.


Contributing
------------

Please contribute using `Github Flow
<https://guides.github.com/introduction/flow/>`_.
Create a branch, add commits, and
`open a pull request<https://github.com/Gunnstein/lahc/compare/>`_.
