import os
import argparse
from jinja2 import Template
from .core import runserver
import logging

parser = argparse.ArgumentParser(description='Example with non-optional arguments')

parser.add_argument(
    '--create-project',
    action="store",
    dest="project",
    help="Create a pyworks project structure",
)
parser.add_argument(
    '--create-subsys', action="store", dest="subsys", help="Create a pyworks sub system"
)
parser.add_argument('--run', '-r', action="store_true", help="run pyworks")
parser.add_argument('--debug', '-d', action="store_true", help="debug mode")

project_template = Template(
    """#!/usr/bin/env python
#
# pyworks - an Task Framework
#
# Copyright (C) __PYLOTS__
#
# Project: {{ target }}
#
import sys


if __name__ == '__main__':
    from pyworks.cli import commandline

    commandline()

"""
)

settings_template = Template(
    """import os

PRODIR = os.path.dirname(os.path.realpath(__file__))
LOGDIR = os.path.join(PRODIR, 'log')

SUBSYSTEMS = [
    # 'somesys',
    # 'someothersys',
]

"""
)

subsys_template = Template(
    """from pyworks import Task
from pyworks.core import actor


class {{ target|capitalize }}Task(Task):
    def pw_initialized(self):
        pass
        
    def pw_configured(self):
        pass
        
    def pw_started(self):
        pass
        
    def pw_timeout(self):
        pass
        
    def pw_exception(self, method_name):
        pass
        
    def pw_invoke(self, method_name):
        pass
        

tasks = [
    task("{{target}}", {{ target|capitalize }}Task),
]

"""
)


def make_init(path):
    file = "%s/__init__.py" % path
    with open(file, "w") as fd:
        pass


def create_project(target):
    if os.path.exists(target):
        print("Already exists: %s" % target)
        return

    os.makedirs(target)
    path = "%s/pywork.py" % target
    with open(path, "w") as fd:
        fd.write(project_template.render(target=target))
    os.chmod(path, 0o755)
    print("created: %s" % path)
    path = "%s/settings.py" % target
    with open(path, "w") as fd:
        fd.write(settings_template.render(target=target))
    os.makedirs("%s/log" % target)


def create_subsys(target):
    if os.path.exists(target):
        print("Already exists: %s" % target)
        return

    os.makedirs(target)
    make_init(target)
    path = "%s/tasks.py" % target
    with open(path, "w") as fd:
        fd.write(subsys_template.render(target=target))


FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-5s %(message)s"


def commandline():
    ns = parser.parse_args()
    if ns.project:
        create_project(ns.project)
    elif ns.subsys:
        create_subsys(ns.subsys)
    elif ns.run:
        from pyworks.util import settings

        logger = logging.getLogger('pyworks')
        level = logging.INFO
        if settings.DEBUG:
            level = logging.DEBUG
        logging.basicConfig(
            filename=os.path.join(settings.LOGDIR, 'pyworks.log'),
            format=FORMAT,
            datefmt='%y%m%d %H%M%S',
            level=level,
        )
        runserver(logger, ns.debug)
