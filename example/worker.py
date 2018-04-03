from pyworks import Task


class WorkerTask(Task):
    def pw_initialized(self):
        self.ntimeout = 0
        self.future = None

    def hello(self, n, msg):
        if n % 7 == 0:
            size = self.pw_module().runner.queue.qsize()
            self.log("%02d: worker hello: %s, size=%s" % (n, msg, size))
        return n

    def start_long_work(self, future):
        self.future = future
        self.log('starting to long work, return on %s' % self.future)

    def pw_timeout(self):
        self.ntimeout += 1
        self.log("timeout(): %d" % self.ntimeout)
        if self.ntimeout % 3 == 0:
            self.notify.worker_done("Good work...")

        if self.ntimeout == 5:
            self.log('setting value for long_work()....')
            self.future.set_value(42)

        if self.ntimeout == 8:
            self.log("Well thats it, bye")

    def close(self):
        self.closed()
