from pyworks import Task


class WorkerTask(Task):
    def init(self):
        self.ntimeout = 0
        self.future = None

    def hello(self, n, msg):
        if n % 2345 == 0:
            size = self._manager.modules[self._name].runner.queue.qsize()
            self.log("%02d: worker hello: %s, size=%s" % (n, msg, size))
        return n

    def start_long_work(self, future):
        self.future = future
        self.log('starting to long work, return on %s' % self.future)

    def timeout(self):
        self.ntimeout += 1
        # self.log("timeout in worker: %d" % self.ntimeout)
        if self.ntimeout == 4:
            self.dispatch().worker_done("good-bye")

        if self.ntimeout == 5:
            self.log('setting value for long_work()....')
            self.future.set_value(42)

        if self.ntimeout == 8:
            self.log("Well thats it, bye")

    def close(self):
        self.closed()
