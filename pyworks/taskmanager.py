from Queue import Queue, Empty
from threading import Thread
import sys, threading, time, os

class Module :
    def __init__( self, name, conf, factory, task=None, proxy=None, runner=None ):
        self.name, self.conf, self.factory, self.task, self.proxy, self.runner = name, conf, factory, task, proxy, runner
        self.listeners = {}

    def get_listeners( self ):
        return self.listeners.values( )
    

class DistributedMethod :
    def __init__( self, name, *args, **kwds ):
        self.name, self.args, self.kwds = name, args, kwds


class DispatchMethodWrapper:
    def __init__( self, task, method ):
        self.task, self.method = task, method

    def __call__( self, *args, **kwds ):
        # dispatch to all the listeners
        for listener in self.task.get_listeners( ):
            listener.get_queue( ).put( DistributedMethod( self.method, *args, **kwds))


class ProxyMethodWrapper:
    def __init__( self, queue, name ):
        self.queue, self.name = queue, name

    def __call__( self, *args, **kwds ):
        self.queue.put( DistributedMethod( self.name, *args, **kwds))


class Dispatcher(object):
    def __init__( self, task ):
        self._task = task
        
    def __getattribute__( self, name ):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        else:
            return DispatchMethodWrapper( self._task, name )


class Proxy(object):
    def __init__( self, runner, name ):
        self._runner, self._name = runner, name

    def __getattribute__( self, name ):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        else:
            return ProxyMethodWrapper( self._runner.queue, name )

class NoFuture :
    def set_value( self, value ): pass
    def get_value( self ): return None
    
class Runner( Thread ) :
    def __init__( self, manager, name, task ):
        Thread.__init__(self, name=name)
        self.manager, self.name, self.task = manager, name, task
        self.queue = Queue( )
        self.running = True
        
    def stop( self ):
        self.running = False
        
    def run( self ):
        while self.queue.qsize( ) or self.running :
            try:
                m = self.queue.get( timeout=2 )
                try:
                    func = getattr( self.task.state, m.name )
                    if 'future' in m.kwds :
                        f = m.kwds[ 'future' ]
                        del( m.kwds[ 'future' ])
                    else:
                        f = NoFuture( )
                    f.set_value( func( *m.args, **m.kwds ))
                except:
                    print "funccall %s failed: %s" % ( m.name, sys.exc_value )
                    self.manager.log( self.task, "funccall %s failed: %s" % ( m.name, sys.exc_value ))
            except Empty :
                self.task.state.timeout( )


class Manager :
    def __init__( self ):
        self.modules = {}
        
    def log( self, task, msg ):
        self.modules[ "logger" ].proxy.log( task, 2, msg )
        
    def error( self, task, msg ):
        self.modules[ "logger" ].proxy.log( task, 1, msg )
    
    def loadModules( self, task_list ):
        for name, module in task_list.items( ) :
            module.task = module.factory( name, self )
            module.task._dispatch = Dispatcher( module.task )
            module.runner = Runner( self, module.name, module.task )
            module.proxy = Proxy( module.runner, module.name )
            self.modules[ name ] = module

    def initModules( self ):
        for name, module in self.modules.items( ) :
            module.task.init( )

    def confModules( self ):
        for name, module in self.modules.items( ) :
            if module.conf and os.access( module.conf, os.R_OK ):
                execfile( module.conf, { 'task' : module.task } )
            module.task.conf( )

    def runModules( self ):
        for name, module in self.modules.items( ) :
            self.log( module.task, "Starting runner: %s" % name )
            module.runner.start( )
            
    def shutdown( self ):                 
        for name, module in self.modules.items( ): # Send close to all tasks
            module.proxy.close( )
        time.sleep( 3 )                             # A little time to settle down
        for name, module in self.modules.items( ): # Stop the threads
            module.runner.stop( )

    def closeModules( self ):
        for name, module in self.modules.items( ) :
            module.task.close( )
            module.runner.stop( )  
            module.runner.join( )
            
    def get_service( self, service ):
        return self.modules[ service ].proxy


