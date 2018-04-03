from pyworks import Task, State


class BaseState(State):
    def pw_timeout(self):
        self.log("Timeout")

    def worker_done(self, msg):
        self.log("worker_done(): Wrong state: %s" % self)

class InitialState(BaseState):
    def pw_timeout(self):
        self.log("timeout(): Going to TimeoutState")
        self.state_set(TimeoutState)


class TimeoutState(BaseState):
    def pw_timeout(self):
        # self.log("timeout in TimeoutState")
        pass

    def worker_done(self, msg):
        self.task.count += 1
        self.log("Worker done at %d, set InitialState" % self.task.count)
        self.state_set(InitialState)

    def pw_close(self):
        self.actor.pw_close()


class StateTask(Task):

    def pw_initialized(self):
        self.state_set(InitialState)
        self.count = 0
        self.log("StateTask init")

    def pw_configured(self):
        self.observe("worker")
