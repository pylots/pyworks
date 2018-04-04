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


class LogMixin(object):

    def __init__(self, module):
        self._pw_logger = module.logger

    def debug(self, msg, *args, **kwargs):
        self._pw_logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._pw_logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._pw_logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._pw_logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._pw_logger.critical(msg, *args, **kwargs)
