from time import time

from pyworks import Task, FutureShock, Future

from pyworks.util import settings


class ClientTask(Task):

    def pw_timeout(self, n):
        self.ntimeout = n
        self.count = 1

    def pw_initialized(self):
        self.ntimeout = 0
        self.answers = []
        self.worker = self.actor("worker")
        self.count = 0

    def pw_configured(self):
        self.observe("worker")

    def pw_timeout(self):
        self.ntimeout += 1
        if self.ntimeout % 10 == 0:
            self.log("timeout: %d" % self.ntimeout)
        if self.ntimeout % 2 == 0:
            start = time()
            n = self.count * self.ntimeout
            for i in range(n):
                a = self.worker.hello(
                    i, "hello, from %s: %d" % (self.pw_name(), self.ntimeout)
                )
                self.answers.append(a)
            t = time() - start
            self.log("%.0f msg/sec" % (float(n) / t))

        if self.ntimeout % 5 == 0:
            self.log("Doing longwork")
            future = Future()
            self.worker.start_long_work(future)
            try:
                self.log("long answer 1 = %d" % future.get_value(2))
            except FutureShock:
                self.log("Hmm: Gave up waiting for longwork, try a little longer")
                try:
                    self.log("Yes: long answer 2 = %d" % future.get_value(10))
                except FutureShock:
                    self.log("Nope no answer....")

        if self.ntimeout % 7 == 0:
            sum = 0
            for r in self.answers:
                sum = sum + r
            self.log("result = %s" % sum)

    def pw_close(self):
        self.log("closing")

    def worker_done(self, msg):
        self.log("Worker Task done: %s" % msg)
