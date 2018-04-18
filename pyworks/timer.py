from pyworks import Task
from pyworks.core import sysreg

class Timer(object):
    pass

class TimerTask(Task):
    timers = {}
    
    def set_timer(self, timer):
        pass

    def timeout(self):
        pass
    
sysreg.task(TimerTask)
