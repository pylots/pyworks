from pyworks import Task
from pyworks.util import Logger


class LoggerTask( Task ):
    def init( self ):
        self._echo = False
        self._level = 2
        self.logger = None

    def echoOn( self ):
        self._echo = True

    def set_level( self, level ):
        self._level = level

    def dolog( self, task, level, msg ):
        if self.logger == None :
            self.logger = Logger( task )
        self.logger.log( level, msg )
        if self._echo :
            print msg,
        
    def close( self ):
        self.logger.close( )
        self.logger = None
