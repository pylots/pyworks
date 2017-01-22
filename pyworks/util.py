from datetime import datetime

LOGDIR = "log"

ERROR = 0
WARN = 1
INFO = 2
DEBUG = 3

levels = ['ERROR', 'WARN', 'INFO', 'DEBUG']


class Logger(object):
    def __init__(self, name=None, logfile="logger"):
        self.name = name
        self.logfile = logfile
        self.level = DEBUG
        self._open_log( )
        self.month = datetime.now().strftime("%m")

    def _open_log(self):
        self._log = open("log/%s-%s" % (datetime.now().strftime("%m"), self.logfile), "a")
        self._log.write("***init***: %s\n" % self.name)
        self._log.flush()

    def set_level(self, level):
        self.level = level

    def log(self, level, text):
        if(level > self.level):
            return
        if self.month != datetime.now().strftime("%m"):
            self._log.write("*** Closing month %s ***" % self.month)
            self.close()
            self._open_log()
        msg = "%s %s [%s] %s\n" % (datetime.now().strftime("%y%m%d:%H%M%S"), levels[level], self.name, text)
        self._log.write(msg)
        self._log.flush()

    def close(self):
        self._log.close()
