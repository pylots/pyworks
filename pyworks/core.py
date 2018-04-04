import importlib

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from threading import Thread
import sys, time, os, traceback
from pyworks import Future, NoFuture, Actor, Task


pyworks_settings = globals()


def load_settings():
    import importlib

    module = os.environ.get('PYWORKS_SETTINGS_MODULE', 'settings')
    mod = importlib.import_module(module)

    for setting in dir(mod):
        if setting.isupper():
            var = getattr(mod, setting)
            pyworks_settings[setting] = var
    return pyworks_settings


class Registry(object):
    tasks = {}

    @classmethod
    def task(cls, name, factory, conf=None, index=None):
        cls.tasks[name] = Process(name, factory, conf)
        if index:
            cls.tasks[name].index = index
        return cls.tasks[name]

    @classmethod
    def actor(cls, name, factory):
        cls.tasks[name] = Process(name, factory)
        return cls.tasks[name]


register = Registry()


def runserver(logger, debug=False):
    load_settings()
    m = Manager(logger=logger, debug=debug)
    m.load_subsys()
    m.load_processes(register.tasks)
    m.init_processes()
    m.conf_processes()
    m.run_processes()

    for process in m.get_processes():
        exec("%s=process.proxy" % (process.name))

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
            m.dump_processes()
            continue

        try:
            exec(line)
            prompt = ">>"
        except:
            print("%s" % sys.exc_info()[1])
            prompt = "?>>"

    m.close_processes()
    m.shutdown()

    # wait for all to close
    for name, process in m.processes.items():
        if not process.daemon:
            process.runner.join()


class Process(object):

    def __init__(self, name, factory, conf=None):
        self.name, self.factory, self.conf = name, factory, conf
        # Below set by manager during initialization
        self.actor = None
        self.proxy = None
        self.runner = None
        self.index = 0
        self.pid = 0
        self.prio = 5
        self.observers = {}
        self.daemon = 0
        self.manager = None
        self.logger = None

    def get_observers(self):
        return self.observers.values()

    def add_observer(self, actor):
        name = actor.pw_name()
        if name in self.observers:
            self.logger.warning(
                'add_observer(%s): Already observing %s'.format(actor, self.name)
            )
            return

        self.observers[name] = {'actor': actor}


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
        # dispatch to all the observers
        for observer in self.actor.pw_observers():
            observer['actor'].pw_queue().put(
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

    def __init__(self, manager, process):
        Thread.__init__(self, name=process.name)
        self.manager, self.process, self.name, self.actor = manager, process, process.name, process.actor
        self.queue = Queue()
        self.state = "Init"

    def stop(self):
        self.state = "Stopping"

    def run(self):
        while self.state != "Stopping":
            try:
                self.state = "Ready"
                actor = self.actor
                timeout = None
                if isinstance(actor, Task):
                    actor = self.actor._pw_state
                    timeout = actor._pw_timeout
                m = self.queue.get(timeout=timeout)
                if not hasattr(actor, m.name):
                    if isinstance(actor, Task):
                        actor.pw_invoke(m.name)
                    else:
                        self.manager.logger.warning(
                            "%s does not have %s" % (self.actor._pw_state, m.name)
                        )
                    continue

                func = getattr(actor, m.name)
                self.state = "Working"
                # print 'from %s, doing: %s' % (m.actor, func)
                try:
                    m.future.set_value(func(*m.args, **m.kwds))
                except:
                    self.manager.logger.warning(
                        'Exception: %s %s' % (m.name, sys.exc_info()[1])
                    )
                    self.manager.log(
                        self.actor,
                        "funccall %s failed: %s (%s)" %
                        (m.name, sys.exc_info()[1], traceback.format_exc()),
                    )
                    actor.pw_exception(m.name)
            except Empty:
                if self.state == "Ready" and isinstance(actor, Task):
                    try:
                        actor.pw_timeout()
                    except:
                        self.manager.log(
                            self.actor,
                            "timeout %s failed: %s (%s)" %
                            (m.name, sys.exc_info()[1], traceback.format_exc()),
                        )
                        actor.pw_exception(m.name)
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
        self.processes = {}
        self.prio = 0
        self.name = "Manager"
        self.state = "Initial"
        self.logger = logger
        self.debug = debug
        ManagerManager.set_manager(self)

    def log(self, actor, msg):
        if self.state is not "Running":
            return

        msg = "%s: %s" % (actor.pw_name(), msg)
        self.logger.info(msg)

    def get_logger(self):
        return self.logger

    def error(self, actor, msg):
        self.logger.error("%s: %s" % (actor.pw_name(), msg))

    def load_subsys(self):
        if not 'SUBSYSTEMS' in pyworks_settings:
            self.logger.warning('SUBSYSTEMS missing from settings')
            return

        for subsys in pyworks_settings['SUBSYSTEMS']:
            self.logger.debug("Load subsys: %s" % subsys)
            mod = importlib.import_module('%s.tasks' % subsys)

    def load_processes(self, actor_list, daemon=0):
        self.state = "Loading"
        index = 0
        for name, process in actor_list.items():
            self.logger.debug("load_process: %s" % name)
            process.manager = self
            process.logger = self.logger
            process.name = name
            process.actor = process.factory(process)
            process.is_task = isinstance(process.actor, Task)
            process.actor._pw_dispatch = Dispatcher(process.actor)
            process.runner = Runner(self, process)
            process.runner.daemon = daemon
            process.proxy = Proxy(process.runner, process.name)
            process.prio = self.prio
            process.index = index
            process.pid = Manager.pid
            process.daemon = daemon
            self.processes[name] = process
            index += 1
            Manager.pid += 1
        # Every time load_processes is called it is Task's with lower prio
        self.prio += 1
        self.state = "Loaded prio: %d" % self.prio

    def init_processes(self):
        self.state = "Initializing"
        for name, process in self.processes.items():
            if process.is_task:
                process.actor.pw_initialized()
        self.log(self, "All actors initialized")
        self.state = "Initialized"

    def conf_processes(self):
        self.state = "Configuration"
        prio = 0
        while prio < self.prio:
            for name, process in self.processes.items():
                if process.prio == prio and process.conf:
                    if os.access(process.conf, os.R_OK):
                        f = open(process.conf)
                        code = compile(f.read(), process.conf, 'exec')
                        exec(code, {'actor': process.actor})
                    else:
                        self.logger.warning(
                            'conf_processes(): %s could not be read' % process.conf
                        )
                if process.is_task:
                    process.actor._pw_state.pw_configured()
            prio += 1
        self.state = "Configured"
        self.logger.debug("Configured")

    def run_processes(self):
        self.state = "Starting"
        prio = 0
        while prio < self.prio:
            for name, process in self.processes.items():
                if process.prio == prio:
                    process.runner.start()
                    if process.is_task:
                        process.proxy.pw_started()
                    self.log(process.actor, "%d: Starting runner: %s" % (prio, name))
            prio += 1
        self.state = "Running"
        self.logger.debug("Running")

    def close_processes(self):
        self.state = "Closing"
        prio = self.prio
        while prio >= 1:
            prio -= 1
            stopped = False
            for name, process in self.processes.items():
                if process.prio == prio and process.is_task:
                    process.proxy.pw_close()
                    stopped = True
            if stopped:
                time.sleep(1)  # A little time to settle down
        self.state = "Closed"

    def shutdown(self):
        self.state = "Shutting"
        while self.prio > 0:
            self.prio -= 1
            self.log(self, "Shutdown level %d" % self.prio)
            for name, process in self.processes.items():  # Stop the threads
                if process.prio == self.prio:
                    process.runner.stop()
        self.state = "Shutdown"

    def dump_processes(self):
        template = "{0}\t{1}\t{2}\t{3}"
        print(template.format("Task", "State", "Queue", "Conf"))
        for name, process in list(self.processes.items()):
            print(
                template.format(
                    name,
                    process.runner.state,
                    process.runner.queue.qsize(),
                    process.conf,
                )
            )

    def get_actor(self, actor):
        return self.processes[actor].proxy

    def get_processes(self):
        return self.processes.values()

    def get_process(self, name):
        if name in self.processes:
            return self.processes[name]

        self.logger.debug("get_process(%s): No such process")
        return None
