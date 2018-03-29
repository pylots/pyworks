import os

from pyworks.core import actor, subsys

PRODIR = os.path.dirname(os.path.realpath(__file__))

INSTALLED_ACTORS = [
    subsys('web'),
    subsys('example')
]

