from datetime import datetime

from pyworks import Task


class LoggerTask( Task ):
    def init( self ):
        self._log = open( "log/logger", "a" )
        self._log.write( "***init***\n" )
        self._log.flush( )
        self._echo = False
        self._level = 2

    def echoOn( self ):
        self._echo = True

    def set_level( self, level ):
        self._level = level

    def dolog( self, task, level, msg ):
        msg = "%d %s: [%s] %s\n" % ( level, datetime.now( ).strftime( "%H%M%S" ), task._name, msg )
        if level < self._level :
            print 'level to low, not printing: %s' % msg
            return
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
