import sys
import logging
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty


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


class Loggable(object):
    def __init__(self, logger):
        self._logger = logger

    def log(self, msg, *args, **kwargs):
        self._logger.info("[%s] %s" % (self, msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)


class ActorInterface(Loggable):
    def pw_initialized(self):
        pass

    def pw_configured(self):
        pass

    def pw_started(self):
        pass

    def pw_exception(self, method_name):
        pass

    def pw_timeout(self):
        pass

    def pw_close(self):
        pass

    def pw_unimplemented(self, name):
        pass


class State(ActorInterface):

    def __init__(self, actor):
        self._actor = actor
        super(ActorInterface, self).__init__(self._actor._logger)

    def pw_enter(self):
        pass

    def pw_leave(self):
        pass

    def pw_state(self, state):
        self._actor._state.pw_leave()
        self._actor._state = state(self._actor)
        self._actor._state.pw_enter()


class Actor(ActorInterface):

    def __init__(self, module, manager):
        self._module, self._manager = module, manager
        self._name = module.name
        self._index = module.index
        self._state = self
        self._dispatch = None
        self._timeout = 5
        self._logger = manager.get_logger()
        super(ActorInterface, self).__init__(self._logger)

    def __str__(self):
        return "%s:%d" % (self._name, self._index)

    def pw_set_timeout(self, t):
        self._timeout = t

    def pw_module(self):
        return self._manager.modules[self._module.name]

    def pw_queue(self):
        return self._module.runner.queue

    def pw_observers(self):
        return self.pw_module().listeners.values()

    def pw_name(self):
        return self._name

    def pw_manager(self):
        return self._manager

    def pw_pid(self):
        return self._module.pid

    def pw_index(self):
        return self._index

    def pw_state(self, state):
        self._state = state(self)
        self._state.pw_enter()

    def actor(self, name=None):
        """
        Get an async interface to an Actor running in a seperate thread

        :param name: Name of the Actor as registred in settings
        :return: An Async proxy to the Actor
        """
        if not name:
            return self._module.proxy
        return self._manager.get_actor(name)

    @property
    def notify(self):
        """
        Usage:
            self.notify.some_method(someargs)

        Send a some_method message to all observers on this Actor
        :return:
        """
        return self._dispatch

    def observe(self, name):
        """
        Start observing the Actor identified by name
        :param name: Name of Actor to observe
        :return:
        """
        self._manager.modules[name].listeners[self._name] = {'actor': self}

