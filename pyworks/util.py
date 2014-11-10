from datetime import datetime

LOGDIR="log"

ERROR=0
WARN=1
INFO=2
DEBUG=3

levels = [ 'ERROR', 'WARN', 'INFO', 'DEBUG']

class Logger( object ):
    def __init__( self, name=None, logfile="logger" ):
        self.name = name
        self.level = INFO
        self._log = open( "log/%s" % logfile, "a" )
        self._log.write( "***init***\n" )
        self._log.flush( )

    def set_level( self, level ):
        self.level = level

    def log( self, level, text ):
        msg = "%s %s [%s] %s\n" % ( datetime.now( ).strftime( "%y%m%d:%H%M%S" ), levels[ level ], self.name, text )

        if( level <= self.level ):
            self._log.write( msg )
            self._log.flush( )

    def close( self ):
        self._log.close( )
