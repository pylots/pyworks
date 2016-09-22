from threading import Lock
import threading
from datetime import datetime
from queue import Queue, Empty

from .util import Logger, DEBUG, INFO, WARN, ERROR

class FutureShock( Exception ):
    pass

class NoFuture( object ):
    def set_value( self, value ): pass
    def get_value( self ): return None

lock = Lock( )
_syslog_file = open( "log/syslog", "a" )
def syslog( msg ):
    lock.acquire( )
    try:
        _syslog_file.write( "%s: [%s] %s\n" % ( datetime.now( ).strftime( "%H%M%S" ), threading.current_thread( ), msg ))
        _syslog_file.flush( )
    finally:
        lock.release( )
syslog( "***Ready***" )

debug_flag = False
def debug( msg ):
    if debug_flag :
        syslog( msg )
        
class Future( object ):
    def __init__( self ):
        self.queue = Queue( )
        self.has_value = False
        self.value = None
        self.ready = False
        self.lock = Lock( )

    def is_ready( self ):
        if self.has_value :
            return True
        return self.queue.qsize( ) > 0

    def set_value( self, value ):
        if self.has_value :
            syslog( "Trying to set_value more than once" )
        self.queue.put( value )
        
    def get_value( self, timeout=Ellipsis ):
        if self.has_value :
            return self.value
        if self.queue.qsize( ) == 0 :
            # The result is not ready yet
            if timeout == 0 :
                raise FutureShock( 'no value' )
            if timeout == Ellipsis :
                # wait forever for a result
                self.value = self.queue.get( )
                self.has_value = True
                return self.value
            else:
                # Will raise Empty on timeout
                try :
                    self.value = self.queue.get( timeout=timeout )
                    self.has_value = True
                    return self.value
                except Empty:
                    raise FutureShock( 'timeout' )
        self.value = self.queue.get( )
        self.has_value = True
        return self.value
    

class State :
    def __init__( self, task ):
        self.task = task

    def __str__( self ):
        return self
    
    def enter( self ):
        pass

    def leave( self ):
        pass

    def set_state( self, state ):
        self.task._state.leave( )
        self.task._state = state( self.task )
        self.task._state.enter( )
        
    def log( self, msg ):
        self.task.log( msg )

    def start( self ):
        pass

    def exception( self, method_name ):
        pass

    def timeout( self ):
        pass

    def close( self ):
        pass
        

class Filter :
    def __init__( self, task=None ):
        self.task = task

    def filter( self, method, *args, **kwds ):
        return True


class Node :
    def __init__( self, nid, val ):
        self.nid = nid
        self.val = val
        self.nodes = {}
        self.parent = None

    def notify( self, node ):
        self.parent.notify( node )

    def addNode( self, node ):
        node.parent = self
        self.nodes[ node.nid ] = node
        return node

    def get_nodeid( self ):
        if self.parent == None :
            return self.nid
        return self.parent.get_nodeid( ) + '.' + self.name

    def get_val( self ):
        return self.val
    
    def set_val( self, val ):
        if self.val != val :
            self.val = val
            self.notify( self )
        
    def get_node( self, nid ):
        return self.nodes[ nid ]

    def lookup( self, nid ):
        node = self
        for k in nid.split( '.' ):
            if node.hasKey( k ):
                node = node.get_node( k )
        return node

    def has_nodeid( self, nid ):
        return nid in self.nodes

    def level( self ):
        if self.parent == None :
            return 0
        return self.parent.level( ) + 1


class Adapter :
    def __init__( self ):
        pass

    
class Task :
    def __init__( self, module, manager ):
        self._module, self._manager = module, manager
        self._name = module.name
        self._index = module.index
        self._state = self
        self._dispatch = None
        self._timeout = 2
        self._logger = Logger( self.get_name( ))
        
    def dispatch( self ):
        return self._dispatch
    
    def set_timeout( self, t ):
        self._timeout = t
        
    def get_module( self ):
        return self._manager.modules[ self._module.name ]
    
    def get_listeners( self ):
        return self.get_module( ).listeners.values( )
    
    def get_queue( self ):
        return self._module.runner.queue

    def get_service( self, name=None ):
        if not name :
            return self._module.proxy
        return self._manager.get_service( name )

    def get_name( self ):
        return self._name

    def get_manager( self ):
        return self._manager
    
    def get_pid( self ):
        return self._module.pid

    def get_index( self ):
        return self._index
    
    def set_state( self, state ):
        self._state = state( self )
        self._state.enter( )
        
    def set_level( self, level ):
        self._logger.set_level( level )
        
    def debug( self, msg ):
        self._logger.log( DEBUG, msg )

    def warn( self, msg ):
        self._logger.log( WARN, msg )
        
    def log( self, msg ):
        self._logger.log( INFO, msg )
        
    def error( self, msg ):
        self._logger.log( ERROR, msg )

    def add_listener( self, name, filter=Filter( ) ):
        self._manager.modules[ name ].listeners[ self._name ] = { 'task' : self, 'filter' : filter }
        
    def closed( self ):
        self._module.runner.running = False
        
    def init( self ):
        pass
    
    def conf( self ):
        pass
    
    def close( self ):
        pass
    
    def start( self ):
        pass
    
    def timeout( self ):
        pass

    def exception( self, method ):
        pass
        
    def not_implemented(self, name):
        self.error("Not implemented: %s" % name)
        
