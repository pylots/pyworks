from time import time
from pyworks import Task

pingtime = 3

class TimeoutTask(Task):
    def pw_configured(self):
        self.tout = 10
        self.pw_set_timeout(self.tout)
        self.last = int(time())
        self.last_ping = int(time())
        
    def ping(self):
        now = int(time())
        diff = (self.last_ping + pingtime) - now
        if diff != 0:
            self.log("BAD ping time: %d " % diff)
        else:
            self.log("TimeoutTask.ping")
        self.last_ping = int(time())
        
    def pw_timeout(self):
        now = int((time() + 1))
        if self.last + self.tout > (now + 1):
            self.log("Early timeout: %d" % (now - self.last))
        elif self.last + self.tout < (now - 1):
            self.log("Late timeout: %d" % (now - self.last))
            print('late....%d' % (now - self.last))
        else:
            self.log("TimeoutTask.timeout: %d" % (now - self.last))
        self.last = now

class TimePingTask(Task):
    def pw_configured(self):
        global pingtime
        self.pw_set_timeout(pingtime)
        self.timeouttask = self.actor('TimeoutTask')
        
    def pw_timeout(self):
        self.timeouttask.ping()
        
    
