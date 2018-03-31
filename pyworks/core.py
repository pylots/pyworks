import importlib
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from threading import Thread
import sys, time, os, traceback
from pyworks import Future, NoFuture

pyworks_settings = globals()
def load_settings():
    import importlib

    module = os.environ.get('PYWORKS_SETTINGS_MODULE', 'settings')
    mod = importlib.import_module(module)

    for setting in dir(mod):
        if setting.isupper():
            var = getattr(mod, setting)
            pyworks_settings[setting] = var


user_actors = {}
def actor(name, factory, conf=None, index=None):
    user_actors[name] = Module(name, conf, factory)
    if index:
        user_actors[name].index = index
    return user_actors[name]

subsystems = []
def subsys(name):
    subsystems.append(name)

def runserver(logger, debug=False):
    s = load_settings()
    m = Manager(logger=logger, debug=debug)
    m.load_subsys(subsystems)
    m.load_modules(user_actors)
    m.init_modules()
    m.conf_modules()
    m.run_modules()

    for module in m.get_modules():
        exec("%s=module.proxy" % (module.name))

    prompt = ">>"
    running = True
    while running:
        try:
            line = input(prompt)
        except KeyboardInterrupt:
            os._exit(0)
        if len(line) == 0:
            prompt = ".."
        if line == "exit":
            running = False
            continue

        if line == "dump":
            m.dump_modules()
            continue

        try:
            exec(line)
            prompt = ">>"
        except:
            print("%s" % sys.exc_info()[1])
            prompt = "?>>"

    m.close_modules()
    m.shutdown()

    # wait for all to close
    for name, module in m.modules.items():
        if not module.daemon:
            module.runner.join()


class Module(object):

    def __init__(self, name, conf, factory, actor=None, proxy=None, runner=None):
        self.name, self.conf, self.factory, self.actor, self.proxy, self.runner = name, conf, factory, actor, proxy, runner
        self.index = 0
        self.pid = 0
        self.prio = 5
        self.listeners = {}
        self.daemon = 0

    def get_listeners(self):
        return self.listeners.values()


class InternalFuture(Future):
    # Methods for transparcy, so in stead of:
    #   n += actor.method().get_value()
    # you can do
    #   n += actor.method()

    def __add__(self, other):
        return self.get_value().__add__(other)

    def __sub__(self, other):
        return self.get_value().__sub__(other)

    def __mul__(self, other):
        return self.get_value().__mul__(other)

    def __floordiv__(self, other):
        return self.get_value().__floordiv__(other)

    def __mod__(self, other):
        return self.get_value().__mod__(other)

    def __divmod__(self, other):
        return self.get_value().__divmod__(other)

    def __pow__(self, other, modulo=1):
        return self.get_value().__pow__(other, modulo)

    def __lshift__(self, other):
        return self.get_value().__lshift__(other)

    def __rshift__(self, other):
        return self.get_value().__rshift__(other)

    def __and__(self, other):
        return self.get_value().__and__(other)

    def __xor__(self, other):
        return self.get_value().__xor__(other)

    def __or__(self, other):
        return self.get_value().__or__(other)

    def __div__(self, other):
        return self.get_value().__div__(other)

    def __truediv__(self, other):
        return self.get_value().__truediv__(other)

    def __radd__(self, other):
        return self.get_value().__radd__(other)

    def __rsub__(self, other):
        return self.get_value().__rsub__(other)

    def __rmul__(self, other):
        return self.get_value().__rmul__(other)

    def __rdiv__(self, other):
        return self.get_value().__rdiv__(other)

    def __rtruediv__(self, other):
        return self.get_value().__rtruediv__(other)

    def __rfloordiv__(self, other):
        return self.get_value().__rfloordiv__(other)

    def __rmod__(self, other):
        return self.get_value().__rmod__(other)

    def __rdivmod__(self, other):
        return self.get_value().__rdivmod__(other)

    def __rpow__(self, other):
        return self.get_value().__rpow__(other)

    def __rlshift__(self, other):
        return self.get_value().__rlshift__(other)

    def __rrshift__(self, other):
        return self.get_value().__rrshift__(other)

    def __rand__(self, other):
        return self.get_value().__rand__(other)

    def __rxor__(self, other):
        return self.get_value().__rxor__(other)

    def __ror__(self, other):
        return self.get_value().__ror__(other)

    def __iadd__(self, other):
        return self.get_value().__iadd__(other)

    def __isub__(self, other):
        return self.get_value().__isub__(other)

    def __imul__(self, other):
        return self.get_value().__imul__(other)

    def __idiv__(self, other):
        return self.get_value().__idiv__(other)

    def __itruediv__(self, other):
        return self.get_value().__itruediv__(other)

    def __ifloordiv__(self, other):
        return self.get_value().__ifloordiv__(other)

    def __imod__(self, other):
        return self.get_value().__imod__(other)

    def __ipow__(self, other, modulo=1):
        return self.get_value().__ipow__(other, modulo)

    def __ilshift__(self, other):
        return self.get_value().__ilshift__(other)

    def __irshift__(self, other):
        return self.get_value().__irshift__(other)

    def __iand__(self, other):
        return self.get_value().__iand__(other)

    def __ixor__(self, other):
        return self.get_value().__ixor__(other)

    def __ior__(self, other):
        return self.get_value().__ior__(other)

    def __neg__(self):
        return self.get_value().__neg__()

    def __pos__(self):
        return self.get_value().__pos__()

    def __abs__(self):
        return self.get_value().__abs__()

    def __invert__(self):
        return self.get_value().__invert__()

    def __complex__(self):
        return self.get_value().__complex__()

    def __int__(self):
        return self.get_value().__int__()

    def __long__(self):
        return self.get_value().__long__()

    def __float__(self):
        return self.get_value().__float__()

    def __oct__(self):
        return self.get_value().__oct__()

    def __hex__(self):
        return self.get_value().__hex__()

    def __index__(self):
        return self.get_value().__index__()

    def __coerce__(self, other):
        return self.get_value().__coerce__(other)

    def __str__(self):
        return self.get_value().__str__()

    def __repr__(self):
        return self.get_value().__repr__()

    def __unicode__(self):
        return self.get_value().__unicode__()


class DistributedMethod(object):

    def __init__(self, actor, name, future, *args, **kwds):
        self.actor, self.name, self.future, self.args, self.kwds = actor, name, future, args, kwds

    def __str__(self):
        return "DisMeth: %s.%s" % (self.actor, self.name)


class DispatchMethodWrapper(object):

    def __init__(self, actor, method):
        self.actor, self.method = actor, method

    def __call__(self, *args, **kwds):
        # dispatch to all the listeners
        for listener in self.actor.pw_observers():
            listener['actor'].pw_queue().put(
                DistributedMethod(self.actor, self.method, NoFuture(), *args, **kwds)
            )


class ProxyMethodWrapper:

    def __init__(self, actor, queue, name):
        self.actor, self.queue, self.name = actor, queue, name

    def __call__(self, *args, **kwds):
        f = InternalFuture()
        self.queue.put(DistributedMethod(self.actor, self.name, f, *args, **kwds))
        return f


class Dispatcher(object):

    def __init__(self, actor):
        self._actor = actor

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        else:
            return DispatchMethodWrapper(self._actor, name)


class Proxy(object):

    def __init__(self, runner, name):
        self._runner, self._name = runner, name

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        else:
            return ProxyMethodWrapper(self._name, self._runner.queue, name)


class Runner(Thread):

    def __init__(self, manager, module):
        Thread.__init__(self, name=module.name)
        self.manager, self.module, self.name, self.actor = manager, module, module.name, module.actor
        self.queue = Queue()
        self.state = "Init"

    def stop(self):
        self.state = "Stopping"

    def run(self):
        while self.state != "Stopping":
            try:
                self.state = "Ready"
                m = self.queue.get(timeout=self.actor._timeout)
                if self.manager.debug: print("m=%s" % m)
                if not hasattr(self.actor._state, m.name):
                    self.manager.logger.warning("%s does not have %s" % (self.actor._state, m.name))
                    self.actor._state.pw_unimplemented(m.name)
                    continue

                func = getattr(self.actor._state, m.name)
                self.state = "Working"
                # print 'from %s, doing: %s' % (m.actor, func)
                try:
                    m.future.set_value(func(*m.args, **m.kwds))
                except:
                    self.manager.logger.warning('Exception: %s %s' % (m.name, sys.exc_info()[1]))
                    self.manager.log(
                        self.actor,
                        "funccall %s failed: %s (%s)" %
                        (m.name, sys.exc_info()[1], traceback.format_exc()),
                    )
                    self.actor._state.pw_exception(m.name)
            except Empty:
                if self.state == "Ready":
                    try:
                        self.actor._state.pw_timeout()
                    except:
                        self.manager.log(
                            self.actor,
                            "timeout %s failed: %s (%s)" %
                            (m.name, sys.exc_info()[1], traceback.format_exc()),
                        )
                        self.actor._state.pw_exception(m.name)
        self.state = "Stopped"


class ManagerManager(object):
    _manager = None

    @staticmethod
    def get_manager():
        return ManagerManager._manager

    @staticmethod
    def set_manager(manager):
        if ManagerManager._manager is not None:
            print("manager already set to: %s" % ManagerManager._manager)
        ManagerManager._manager = manager


class PrintLogger(object):

    def debug(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        print(msg, *args, **kwargs)


class Manager(object):
    pid = 0

    def __init__(self, env="pyworks", logger=PrintLogger(), debug=False):
        self.env = env
        self.modules = {}
        self.prio = 0
        self.name = "Manager"
        self.state = "Initial"
        self.logger = logger
        self.debug = debug
        ManagerManager.set_manager(self)

    def log(self, actor, msg):
        if self.state is not "Running":
            return
        msg = "%s: %s" % (actor._name, msg)
        self.logger.info(msg)

    def get_logger(self):
        return self.logger

    def error(self, actor, msg):
        self.logger.error("%s: %s" % (actor._name, msg))

    def load_subsys(self, subsystems):
        for subsys in subsystems:
            if self.debug: print("Load subsys: %s" % subsys)
            mod = importlib.import_module('%s.actors' % subsys)

    def load_modules(self, actor_list, daemon=0):
        self.state = "Loading"
        index = 0
        for name, module in actor_list.items():
            if self.debug: print("Load: %s" % name)
            module.name = name
            module.actor = module.factory(module, self)
            module.actor._dispatch = Dispatcher(module.actor)
            module.runner = Runner(self, module)
            module.runner.daemon = daemon
            module.proxy = Proxy(module.runner, module.name)
            module.prio = self.prio
            module.index = index
            module.pid = Manager.pid
            module.daemon = daemon
            self.modules[name] = module
            index += 1
            Manager.pid += 1
        # Every time loadModules is called it is Actor's with lower prio
        self.prio += 1
        self.state = "Loaded prio: %d" % self.prio

    def init_modules(self):
        self.state = "Initializing"
        for name, module in self.modules.items():
            module.actor.pw_initialized()
        self.log(self, "All actors initialized")
        self.state = "Initialized"

    def conf_modules(self):
        self.state = "Configuration"
        prio = 0
        while prio < self.prio:
            for name, module in self.modules.items():
                if module.prio == prio:
                    filename = 'conf/%s.py' % self.env
                    if os.access(filename, os.R_OK):
                        f = open(filename)
                        code = compile(f.read(), filename, 'exec')
                        exec(code, {'actor': module.actor})
                    if module.conf:
                        if os.access(module.conf, os.R_OK):
                            f = open(module.conf)
                            code = compile(f.read(), module.conf, 'exec')
                            exec(code, {'actor': module.actor})
                        else:
                            self.logger.warning('%s could not be read' % module.conf)
                    module.actor.pw_configured()
            prio += 1
        self.state = "Configured"
        if self.debug: print("Configured")

    def run_modules(self):
        self.state = "Starting"
        prio = 0
        while prio < self.prio:
            for name, module in self.modules.items():
                if module.prio == prio:
                    module.runner.start()
                    module.proxy.pw_started()
                    self.log(module.actor, "%d: Starting runner: %s" % (prio, name))
            prio += 1
        self.state = "Running"
        if self.debug: print("Running")

    def close_modules(self):
        self.state = "Closing"
        prio = self.prio
        while prio >= 1:
            prio -= 1
            stopped = False
            for name, module in self.modules.items():
                if module.prio == prio:
                    module.proxy.pw_close()
                    stopped = True
            if stopped:
                time.sleep(1)  # A little time to settle down
        self.state = "Closed"

    def shutdown(self):
        self.state = "Shutting"
        while self.prio > 0:
            self.prio -= 1
            self.log(self, "Shutdown level %d" % self.prio)
            for name, module in self.modules.items():  # Stop the threads
                if module.prio == self.prio:
                    module.runner.stop()
        self.state = "Shutdown"

    def dump_modules(self):
        template = "{0}\t{1}\t{2}\t{3}"
        print(template.format("Actor", "State", "Queue", "Conf"))
        for name, module in list(self.modules.items()):
            print(
                template.format(name, module.runner.state, module.runner.queue.qsize(), module.conf)
            )

    def get_actor(self, actor):
        return self.modules[actor].proxy

    def get_modules(self):
        return self.modules.values()

    def get_module(self, name):
        if name in self.modules:
            return self.modules[name]

        return None
