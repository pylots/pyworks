
import os
import sys
import importlib

from pyworks.manager import Module, Manager


pyworks_settings = globals()
def load_settings():
    import importlib

    module = os.environ.get('PYWORKS_SETTINGS_MODULE', 'settings')
    mod = importlib.import_module(module)

    for setting in dir(mod):
        if setting.isupper():
            var = getattr(mod, setting)
            pyworks_settings[setting] = var[0]


user_actors = {}
def actor(name, factory, conf=None, index=None):
    user_actors[name] = Module(name, conf, factory)
    if index:
        user_actors[name].index = index
    return user_actors[name]


def subsys(name):
    mod = importlib.import_module('%s.actors' % name)

def execute_from_command_line(args):
    s = load_settings()
    m = Manager()
    m.load_modules(user_actors)
    m.init_modules()
    m.dump_modules()
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
