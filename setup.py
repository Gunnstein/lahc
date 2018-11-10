# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

LONG_DESCRIPTION = """`lahc` is a python implementation of the
[Late Acceptance Hill Climbing optimization](http://en.wikipedia.org/wiki/Late_acceptance_hill_climbing)
technique. Late Acceptance Hill Climbing is a metaheuristic search
method used to find a close-to-optimal solution in optimization
problems.

In contrast to several other metaheuristics it only relies on a single
parameter (the history length), but has still shown to be competitive
with more complex heuristics for many applications.

   For more information see

        E. K. Burke, Y. Bykov, The late acceptance Hill-Climbing heuristic.
        European Journal of Operational Research. 258, 70–78 (2017).
"""

# Parse the version from the module.
with open('lahc/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

setup(
    name='lahc',
    version=version,
    description='Late Acceptance Hill Climbing in Python',
    license='MIT',
    author='Gunnstein T. Frøseth',
    author_email='gunnstein@mailbox.org',
    url='https://github.com/gunnstein/lahc',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(exclude=["test"]),
    install_requires=[])
