from datetime import datetime

from pyworks import Task

LOGDIR="log"

ERROR=0
WARN=1
DEBUG=2

class Logger( object ):
    def __init__( self, name=None, logfile="logger" ):
        if isinstance( name, Task ):
            task = name
            self.name = task.get_name( )
        else:
            self.name = name
        self.level = 1
        self._log = open( "log/%s" % logfile, "a" )
        self._log.write( "***init***\n" )
        self._log.flush( )

    def set_level( self, level ):
        self.level = level

    def log( self, level, text ):
        msg = "%d %s: [%s] %s\n" % ( level, datetime.now( ).strftime( "%H%M%S" ), self.name, text )

        if( level <= self.level ):
            self._log.write( msg )
            self._log.flush( )

    def close( self ):
        self._log.close( )
