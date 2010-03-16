class Future :
    def __init__( self ):
        self.state = 0
        self.value = None
        
    def set_value( self, value ):
        self.value = value
        self.state = 1
        
    def get_value( self, timeout=0 ):
        # Should implement timeout one day :-)
        if self.state == 0 :
            return None
        return self.value
    

class NoFuture :
    def set_value( self, value ): pass
    def get_value( self ): return None


class Task :
    def __init__( self, name, manager ):
        self.name, self.manager = name, manager
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
    
