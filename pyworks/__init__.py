from threading import Lock
from Queue import Queue, Empty

class FutureShock( Exception ):
    pass


class State :
    def __init__( self, task ):
        self.task = task

    def __str__( self ):
        return self
    
    def set_state( self, state ):
        self.task._state = state( self.task )
        
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

    def getNid( self ):
        if self.parent == None :
            return self.nid
        return self.parent.getNid( ) + '.' + self.name

    def getVal( self ):
        return self.val
    
    def setVal( self, val ):
        if self.val != val :
            self.val = val
            self.notify( self )
        
    def getNode( self, nid ):
        return self.nodes[ nid ]

    def lookUp( self, nid ):
        node = self
        for k in nid.split( '.' ):
            if node.hasKey( k ):
                node = node.getNode( k )
        return node

    def hasNid( self, nid ):
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
    
    def set_state( self, state ):
        self._state = state( self )
        
    def log( self, msg ):
        self._manager.log( self, msg )
        
    def error( self, msg ):
        self._manager.error( self, msg )

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
    