import os

from .core import pyworks_settings


class Settings(object):
    prodir = None

    def __getattr__(self, item):
        if item == 'PRODIR':
            if not self.prodir:
                self.prodir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            return self.prodir
        if item in pyworks_settings:
            var = pyworks_settings[item]
            if isinstance(var, tuple):
                return var[0]
            return pyworks_settings[item]
        return None


settings = Settings()
