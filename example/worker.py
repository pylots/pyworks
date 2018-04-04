import logging
from pyworks import Task


class WorkerTask(Task):
    def pw_initialized(self):
        self.ntimeout = 0
        self.future = None
        self.math = self.actor('math')
        self.result = None

    def hello(self, n, msg):
        if n % 7 == 0:
            size = self.pw_process().runner.queue.qsize()
            self.log("%02d: worker hello: %s, size=%s" % (n, msg, size))
        return n

    def start_long_work(self, future):
        self.future = future
        self.log('starting to long work, return on %s' % self.future)

    def pw_timeout(self):
        self.ntimeout += 1
        self.log("timeout(): %d" % self.ntimeout)
        if self.result and self.result.is_ready():
            r = "%s" % self.result.get_value()
            self.log("result from factorial, has %d digits" % len(r))
            self.result = None

        if self.ntimeout % 3 == 0:
            self.notify.worker_done("Good work...")

        if self.ntimeout % 4 == 0:
            self.log("Starting math job")
            self.result = self.math.factorial(200000)

        if self.ntimeout == 5:
            self.log('setting value for long_work()....')
            self.future.set_value(42)

        if self.ntimeout == 8:
            self.log("Well thats it, bye")