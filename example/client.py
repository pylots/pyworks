from time import time

from pyworks import Actor, FutureShock, Future


class ClientActor(Actor) :
    def pw_timeout(self, n):
        self.ntimeout = n
        self.count = 1

    def pw_initialized(self):
        self.ntimeout = 0
        self.answers = []
        self.worker = self.actor("worker")

    def pw_configured(self):
        self.observe("worker")

    def pw_timeout(self):
        self.ntimeout += 1
        if self.ntimeout % 100 == 0:
            self.log("timeout: %d" % self.ntimeout)
        if self.ntimeout == 2 or self.ntimeout == 4:
            return
            start = time()
            n = self.count * self.ntimeout
            for i in range(n):
                a = self.worker.hello(i, "hello, from %s: %d" % (self.pw_name(), self.ntimeout))
                self.answers.append(a)
            t = time() - start
            self.log("%.0f msg/sec" % (float(n) / t))

        if self.ntimeout == 3:
            self.log("Doing longwork")
            future = Future()
            self.worker.start_long_work(future)
            try:
                self.log("long answer 1 = %d" % future.get_value(2))
            except FutureShock:
                self.log("Ahh, I gave up waiting for longwork, try a little longer")
                try:
                    self.log("long answer 2 = %d" % future.get_value(10))
                except FutureShock:
                    self.log("long answer 3 = %d" % future.get_value())

        if self.ntimeout == 5:
            return
            sum = 0
            for r in self.answers:
                sum = sum + r
            self.log("result = %s" % sum)

    def close(self):
        self.log("closing")
        self.closed()

    def worker_done(self, msg):
        self.log("The worker Actor is done: %s" % msg)
