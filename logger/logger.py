from datetime import datetime

from pyworks import Task

class LoggerTask( Task ):
    def init( self ):
        self._log = open( "log/logger", "a" )
        self._log.write( "***init***\n" )
        self._log.flush( )
        self._echo = False

    def echoOn( self ):
        self._echo = True

    def log( self, task, level, msg ):
        msg = "%s: [%s] %s\n" % ( datetime.now( ).strftime( "%H%M%S" ), task.get_name( ), msg )
        if self._log == None :
            print "LOG IS CLOSED: %s" % msg
        else:
            self._log.write( msg )
            self._log.flush( )
        if self._echo :
            print msg,
        
    def close( self ):
        self._log.write( "*** stopped ***\n" )
        self._log.close( )
        self._log = None
