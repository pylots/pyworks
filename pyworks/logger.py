from pyworks import Task
from pyworks.util import Logger, WARN, ERROR, DEBUG


class LoggerTask( Task ):
    def init( self ):
        self._echo = False
        self.logger = Logger( self )

    def echoOn( self ):
        self._echo = True

    def set_level( self, level ):
        self.logger.set_level( level )

    def dolog( self, task, level, msg ):
        self.logger.log( level, "(%s): %s" % ( task, msg ))
        if self._echo :
            print msg,
        
    def log( self, level, msg ):
        self.dolog( self, level, msg )

    def close( self ):
        self.logger.close( )
        self.logger = None
