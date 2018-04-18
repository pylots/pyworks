import logging

from pyworks import Task
from pyworks.core import sysreg

logger = logging.getLogger()

class LoggerTask(Task):
    def pw_initialized(self):
        self.level = logger.INFO
        
    def log(self, msg):
        logger.log(self.level, msg)

    def set_level(self, level):
        self.level = level
        
sysreg.task(LoggerTask)
