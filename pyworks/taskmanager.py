from Queue import Queue, Empty
from threading import Thread
import sys, threading, time, os

class Module :
    def __init__( self, name, conf, factory, task=None, proxy=None, runner=None ):
        self.name, self.conf, self.factory, self.task, self.proxy, self.runner = name, conf, factory, task, proxy, runner
        self.prio = 5
        self.listeners = {}

    def get_listeners( self ):
        return self.listeners.values( )
    

class NoFuture :
    def set_value( self, value ): pass
    def get_value( self ): return None

class Future :
    def __init__( self ):
        self.queue = Queue( )
        
    def is_ready( self ):
        return self.queue.qsize( ) > 0

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
    

class DistributedMethod :
    def __init__( self, name, future, *args, **kwds ):
        self.name, self.future, self.args, self.kwds = name, future, args, kwds


class DispatchMethodWrapper:
    def __init__( self, task, method ):
        self.task, self.method = task, method

    def __call__( self, *args, **kwds ):
        # dispatch to all the listeners
        for listener in self.task.get_listeners( ):
            if listener[ 'filter' ].filter( self.method, *args, **kwds ):
                listener[ 'task' ].get_queue( ).put( DistributedMethod( self.method, NoFuture(), *args, **kwds))


class ProxyMethodWrapper:
    def __init__( self, queue, name ):
        self.queue, self.name = queue, name

    def __call__( self, *args, **kwds ):
        f = Future( )
        self.queue.put( DistributedMethod( self.name, f, *args, **kwds))
        return f


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

    
class Runner( Thread ) :
    def __init__( self, manager, module ):
        Thread.__init__(self, name=module.name)
        self.manager, self.module, self.name, self.task = manager, module, module.name, module.task
        self.queue = Queue( )
        self.running = True
        
    def stop( self ):
        self.running = False
        
    def run( self ):
        while self.queue.qsize( ) or self.running :
            try:
                m = self.queue.get( timeout=self.task._timeout )
                func = getattr( self.task.state, m.name )
                try:
                    m.future.set_value( func( *m.args, **m.kwds ))
                except:
                    self.manager.log( self.task, "funccall %s failed: %s" % ( m.name, sys.exc_value ))
            except Empty :
                self.task.state.timeout( )


class Manager :
    def __init__( self ):
        self.modules = {}
        self.prio = 0
        self.name = "Manager"
        
    def log( self, task, msg ):
        module = self.modules[ "logger" ]
        msg = "q:%d, %s" % ( module.runner.queue.qsize( ), msg )
        module.proxy.log( task, 2, msg )
        
    def error( self, task, msg ):
        self.modules[ "logger" ].proxy.log( task, 1, msg )
    
    def loadModules( self, task_list ):
        for name, module in task_list.items( ) :
            module.name = name
            module.task = module.factory( module, self )
            module.task._dispatch = Dispatcher( module.task )
            module.runner = Runner( self, module )
            module.proxy = Proxy( module.runner, module.name )
            module.prio = self.prio
            self.modules[ name ] = module
        # Every time loadModules is called it is Task's with lower prio
        self.prio += 1
        
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
        for prio in [ 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 ] :
            stopped = False
            self.log( self, "closing level %d" % prio )
            for name, module in self.modules.items( ): # Send close to all tasks
                if module.prio == prio :
                    self.log( module.task, "closing %s level %d" % ( module.task.name, prio ))
                    module.proxy.close( )
                    stopped = True
            if stopped :
                time.sleep( 3 )                             # A little time to settle down
            for name, module in self.modules.items( ): # Stop the threads
                if module.prio == prio :
                    module.runner.stop( )
                    module.runner.join( )
                    
    def closeModules( self ):
        for name, module in self.modules.items( ) :
            module.task.close( )
            module.runner.stop( )  
            module.runner.join( )
            
    def get_service( self, service ):
        return self.modules[ service ].proxy

    def get_modules( self ):
        return self.modules.values()

