from threading import Lock
from Queue import Queue, Empty

class FutureShock( Exception ):
    pass


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
        
class Filter :
    def __init__( self, task=None ):
        self.task = task

    def filter( self, method, *args, **kwds ):
        return True

class Task :
    def __init__( self, module, manager ):
        self.module, self.manager = module, manager
        self.name = module.name
        self.state = self
        self._dispatch = None
        self._timeout = 2
        
    def dispatch( self ):
        return self._dispatch
    
    def set_timeout( self, t ):
        self._timeout = t
        
    def get_module( self ):
        return self.manager.modules[ self.module.name ]
    
    def get_listeners( self ):
        return self.get_module( ).listeners.values( )
    
    def get_queue( self ):
        return self.module.runner.queue

    def get_service( self, name ):
        return self.manager.get_service( name )
    
    def new_state( self, state ):
        self.state = state( self )
        
    def log( self, msg ):
        self.manager.log( self, msg )
        
    def error( self, msg ):
        self.manager.error( self, msg )

    def add_listener( self, name, filter=Filter( ) ):
        self.manager.modules[ name ].listeners[ self.name ] = { 'task' : self, 'filter' : filter }
        
    def closed( self ):
        self.module.runner.running = False
        
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
    
