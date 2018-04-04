import sys
import logging

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty


def actor(self, instance):
    pass


class FutureShock(Exception):
    pass


class NoFuture(object):

    def set_value(self, value):
        pass

    def get_value(self):
        return None


class Future(object):

    def __init__(self):
        self.queue = Queue()
        self.has_value = False
        self.value = None
        self.ready = False

    def is_ready(self):
        if self.has_value:
            return True

        return self.queue.qsize() > 0

    def set_value(self, value):
        if self.has_value:
            raise Exception("Trying to set_value more than once")

        self.queue.put(value)

    def get_value(self, timeout=Ellipsis):
        if self.has_value:
            return self.value

        if self.queue.qsize() == 0:
            # The result is not ready yet
            if timeout == 0:
                raise FutureShock('no value')

            if timeout == Ellipsis:
                # wait forever for a result
                self.value = self.queue.get()
                self.has_value = True
                return self.value

            else:
                # Will raise Empty on timeout
                try:
                    self.value = self.queue.get(timeout=timeout)
                    self.has_value = True
                    return self.value

                except Empty:
                    raise FutureShock('timeout')

        self.value = self.queue.get()
        self.has_value = True
        return self.value


class Actor(object):

    def __init__(self, process):
        self._pw_process = process
        self._pw_manager = process.manager

    def __str__(self):
        return "%s:%d" % (self._pw_process.name, self._pw_process.index)

    def log(self, msg, *args, **kwargs):
        self._pw_process.logger.info("[%s] %s" % (self, msg), *args, **kwargs)

    def pw_state(self):
        return self

    def pw_name(self):
        return self._pw_process.name

    def actor(self, name=None):
        """
        Get an async interface to an Actor or Task running in a seperate thread

        :param name: Name of the Task as registred in settings
        :return: An Async proxy to the Task
        """
        if not name:
            return self._pw_process.proxy

        return self._pw_manager.get_actor(name)

    @property
    def notify(self):
        """
        Usage:
            self.notify.some_method(someargs)

        Send a some_method() message to all observers on this Task
        :return:
        """
        return self._pw_dispatch

    def observe(self, name):
        """
        Start observing the Task identified by name
        :param name: Name of Task to observe
        :return:
        """
        self._pw_manager.get_process(name).add_observer(self)


class State(Actor):

    def __init__(self, process):
        super().__init__(process)
        self._pw_timeout = 5

    def __str__(self):
        return "%s:%s" % (super().__str__(), self.__class__.__name__)

    @property
    def task(self):
        return self.pw_process().actor

    def pw_process(self):
        return self._pw_process

    def pw_queue(self):
        return self._pw_process.runner.queue

    def pw_observers(self):
        return self.pw_process().get_observers()

    def pw_name(self):
        return self._pw_process.name

    def pw_manager(self):
        return self._pw_manager

    def pw_pid(self):
        return self._pw_process.pid

    def pw_index(self):
        return self._pw_process.index

    def pw_initialized(self):
        pass

    def pw_configured(self):
        pass

    def pw_started(self):
        pass

    def pw_exception(self, method_name):
        pass

    def pw_invoke(self, name):
        pass

    def pw_timeout(self):
        pass

    def pw_close(self):
        pass

    def pw_set_timeout(self, t):
        self._pw_timeout = t

    def pw_state(self):
        return self._pw_process.actor._pw_state

    # State handling methods

    def state_leave(self):
        pass

    def state_enter(self):
        pass

    def state_set(self, state):
        self._pw_process.actor._pw_state.state_leave()
        self._pw_process.actor._pw_state = state(self._pw_process)
        self._pw_process.actor._pw_state.state_enter()


class Task(State):

    def __init__(self, process):
        super().__init__(process)
        self._pw_state = self

    def state_set(self, state):
        self._pw_state = state(self._pw_process)
        self._pw_state.state_enter()
