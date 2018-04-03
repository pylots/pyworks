from pyworks import Task

from time import time

class RingActor(Task) :
    """
    Send messages to next Task in Ring
    """
    def pw_initialized(self):
        self.count = 1
        self.n = self.pw_index() + 1
        if self.pw_index() >= 99 :
            self.n = 0
        self.log("%s: ring%d->ring%d" % (self.pw_name(), self.pw_index(), self.n))
        self.next = self.actor("ring%d" % self.n)

    def pw_configured(self):
        self.observe("ring%d" % self.n)

    def setCount(self, count):
        self.count = count

    def setMessages(self, nmsg):
        self.nmsg = nmsg

    def ringop(self, name, n):
        if n % 50000 == 0:
            self.log("%s: from %s n=%d" % (self.pw_name(), name, n))
        if n < 100000:
            self.next.ringop(self.pw_name(), n + 1)
        if n >= 100000:
            self.log("Done: %d secs" % (time() - self.start))

    def pw_timeout(self):
        self.start = time()
        if self.count > 0 and self.pw_index() == 0:
            self.log("%s calling next with %d" % (self.pw_name(), self.n))
            self.next.ringop(self.pw_name(), self.n)
        self.count -= 1
