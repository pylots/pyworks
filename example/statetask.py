from pyworks import Actor, State


class BaseState(State):
    def timeout(self):
        self.log("Timeout in BaseState")

    def worker_done(self, msg):
        self.log("Received worker_done in Wrong state: %s" % self)

    def close(self):
        self.task.closed()


class InitialState(BaseState):
    def timeout(self):
        self.log("timeout in InitialState")
        self.set_state(TimeoutState)


class TimeoutState(BaseState):
    def timeout(self):
        # self.log("timeout in TimeoutState")
        pass

    def worker_done(self, msg):
        self.log("The worker is done, going back to TimeoutState")
        self.set_state(InitialState)

    def close(self):
        self.task.close()


class StateActor(Actor):
    def init(self):
        self.log("StateActor init")
        self.set_state(InitialState)

    def conf(self):
        self.observe("worker")
