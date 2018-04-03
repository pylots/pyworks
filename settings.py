import os

PRODIR = os.path.dirname(os.path.realpath(__file__))
LOGDIR = os.path.join(PRODIR, 'log')

DEBUG = False

SUBSYSTEMS = [
    'web',
    'example'
]
