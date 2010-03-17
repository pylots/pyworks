from threading import Lock
class Future :
    def __init__( self ):
        self.state = 0
        self.value = None
        
    def set_value( self, value ):
        self.value = value
        self.state = 1


    def get_value( self, wait=True ):
        # Should implement timeout/wait one day :-)
        if wait and self.state == 0 :
            return None
        return self.value
    

class State :
    def __init__( self, task ):
        self.task = task

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
    
