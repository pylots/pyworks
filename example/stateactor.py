from pyworks import Actor, State


class BaseState(State):
    def pw_timeout(self):
        self.log("Timeout in BaseState")

    def worker_done(self, msg):
        self.log("Received worker_done in Wrong state: %s" % self)

    def close(self):
        self.actor.closed()


class InitialState(BaseState):
    def pw_timeout(self):
        self.log("timeout in InitialState")
        self.pw_state(TimeoutState)


class TimeoutState(BaseState):
    def pw_timeout(self):
        # self.log("timeout in TimeoutState")
        pass

    def worker_done(self, msg):
        self.log("The worker is done, going back to TimeoutState")
        self.pw_state(InitialState)

    def close(self):
        self.actor.close()


class StateActor(Actor):
    def pw_initialized(self):
        self.log("StateActor init")
        self.pw_state(InitialState)

    def pw_configured(self):
        self.observe("worker")
