import os

from .core import pyworks_settings, load_settings

class Settings(object):
    def __getattr__(self, item):
        if item in pyworks_settings:
            var = pyworks_settings[item]
            if isinstance(var, tuple):
                return var[0]
            return var
        return None

#
load_settings()
settings = Settings()
