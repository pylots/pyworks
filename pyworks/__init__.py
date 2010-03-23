from threading import Lock
from Queue import Queue, Empty

class FutureShock( Exception ):
    pass


class Future :
    def __init__( self ):
        self.queue = Queue( )
        
    def set_value( self, value ):
        self.queue.put( value )

    def get_value( self, timeout=Ellipsis ):
        if self.queue.qsize( ) == 0 :
            # The result is not ready yet
            if timeout == 0 :
                raise FutureShock( 'no value' )
            if timeout == Ellipsis :
                # wait forever for a result
                return self.queue.get( )
            else:
                # Will raise Empty on timeout
                try :
                    return self.queue.get( timeout=timeout )
                except Empty:
                    raise FutureShock( 'timeout' )
                
        return self.queue.get( )
    

class State :
    def __init__( self, task ):
        self.task = task

    def __str__( self ):
        return self
    
    def new_state( self, state ):
        self.task.state = state( self.task )
        
    def log( self, msg ):
        self.task.log( msg )

    def close( self ):
        pass
        

class Task :
    def __init__( self, name, manager ):
        self.name, self.manager = name, manager
        self.state = self
        self._dispatch = None

    def dispatch( self ):
        return self._dispatch
    
    def get_module( self ):
        return self.manager.modules[ self.name ]
    
    def get_listeners( self ):
        return self.get_module( ).listeners.values( )
    
    def get_queue( self ):
        return self.manager.modules[ self.name ].runner.queue

    def get_service( self, name ):
        return self.manager.get_service( name )
    
    def new_state( self, state ):
        self.state = state( self )
        
    def log( self, msg ):
        self.manager.log( self, msg )
        
    def error( self, msg ):
        self.manager.error( self, msg )

    def add_listener( self, name ):
        self.manager.modules[ name ].listeners[ self.name ] = self
        
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
    
