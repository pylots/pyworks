import sys
import logging
from queue import Queue, Empty


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
            logger.warning("Trying to set_value more than once")
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


class State:

    def __init__(self, actor):
        self.actor = actor

    def __str__(self):
        return self

    def enter(self):
        pass

    def leave(self):
        pass

    def set_state(self, state):
        self.actor._state.leave()
        self.actor._state = state(self.actor)
        self.actor._state.enter()

    def log(self, msg):
        self.actor.log(msg)

    def start(self):
        pass

    def exception(self, method_name):
        pass

    def timeout(self):
        pass

    def close(self):
        pass


class Filter:

    def __init__(self, actor=None):
        self.actor = actor

    def filter(self, method, *args, **kwds):
        return True


class Node:

    def __init__(self, nid, val):
        self.nid = nid
        self.val = val
        self.nodes = {}
        self.parent = None

    def notify(self, node):
        self.parent.notify(node)

    def add_node(self, node):
        node.parent = self
        self.nodes[node.nid] = node
        return node

    def get_nodeid(self):
        if self.parent == None:
            return self.nid

        return self.parent.get_nodeid() + '.' + self.name

    def get_val(self):
        return self.val

    def set_val(self, val):
        if self.val != val:
            self.val = val
            self.notify(self)

    def get_node(self, nid):
        return self.nodes[nid]

    def lookup(self, nid):
        node = self
        for k in nid.split('.'):
            if node.hasKey(k):
                node = node.get_node(k)
        return node

    def has_nodeid(self, nid):
        return nid in self.nodes

    def level(self):
        if self.parent == None:
            return 0

        return self.parent.level() + 1


class Adapter:

    def __init__(self):
        pass


class Actor:

    def __init__(self, module, manager):
        self._module, self._manager = module, manager
        self._name = module.name
        self._index = module.index
        self._state = self
        self._dispatch = None
        self._timeout = 2
        self._logger = manager.get_logger()

    @property
    def observers(self):
        return self._dispatch

    def log(self, msg, *args, **kwargs):
        self._manager.log(self, msg, *args, **kwargs)

    def set_timeout(self, t):
        self._timeout = t

    def get_module(self):
        return self._manager.modules[self._module.name]

    def get_observers(self):
        return self.get_module().listeners.values()

    def get_queue(self):
        return self._module.runner.queue

    def actor(self, name=None):
        if not name:
            return self._module.proxy

        return self._manager.get_actor(name)

    def get_name(self):
        return self._name

    def get_manager(self):
        return self._manager

    def get_pid(self):
        return self._module.pid

    def get_index(self):
        return self._index

    def set_state(self, state):
        self._state = state(self)
        self._state.enter()

    def observe(self, name, filter=Filter()):
        self._manager.modules[name].listeners[self._name] = {
            'actor': self, 'filter': filter
        }

    def closed(self):
        self._module.runner.running = False

    def init(self):
        pass

    def conf(self):
        pass

    def close(self):
        pass

    def start(self):
        pass

    def timeout(self):
        pass

    def exception(self, method):
        pass

    def not_implemented(self, name):
        self.error("Method not implemented: %s" % name)


