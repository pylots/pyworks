from Queue import Queue, Empty
from threading import Thread
import sys, threading, time, os

class Module :
    def __init__( self, name, conf, factory, task=None, proxy=None, runner=None ):
        self.name, self.conf, self.factory, self.task, self.proxy, self.runner = name, conf, factory, task, proxy, runner
        self.index = 0
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
        
    # Methods for transparcy, so in stead of:
    #   n += task.method( ).get_value( )
    # you can do
    #   n += task.method( )
    def __int__( self ): return self.get_value( )
    def __float__( self ): return self.get_value( )
    def __add__( self, other ): return self.get_value( ).__add__( other )
    def __sub__( self, other ): return self.get_value( ).__sub__( other )
    def __mul__( self, other ): return self.get_value( ).__mul__( other )
    def __div__( self, other ): return self.get_value( ).__div__( other )
    def __radd__(self, other): return self.__add__(other)    

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
        self.state = "Init"
        
    def stop( self ):
        self.state = "Stopping"
        
    def run( self ):
        while self.state != "Stopping" :
            try:
                self.state = "Ready"
                m = self.queue.get( timeout=self.task._timeout )
                func = getattr( self.task._state, m.name )
                self.state = "Working"
                try:
                    m.future.set_value( func( *m.args, **m.kwds ))
                except:
                    print 'Exception: %s %s' % ( m.name, sys.exc_info( )[1])
                    self.manager.log( self.task, "funccall %s failed: %s" % ( m.name, sys.exc_info( )[1] ))
            except Empty :
                if self.state == "Ready" :
                    self.task._state.timeout( )
        self.state = "Stopped"


class Manager :
    def __init__( self ):
        self.modules = {}
        self.prio = 0
        self.name = "Manager"
        self.state = "Initial"
        
    def log( self, task, msg ):
        if self.state != "Running" :
            return
        module = self.modules[ "logger" ]
        msg = "q:%d, %s" % ( module.runner.queue.qsize( ), msg )
        module.proxy.log( task, 2, msg )
        
    def error( self, task, msg ):
        self.modules[ "logger" ].proxy.log( task, 1, msg )
    
    def loadModules( self, task_list ):
        self.state = "Loading"
        index = 0
        for name, module in task_list.items( ) :
            module.name = name
            module.task = module.factory( module, self )
            module.task._dispatch = Dispatcher( module.task )
            module.runner = Runner( self, module )
            module.proxy = Proxy( module.runner, module.name )
            module.prio = self.prio
            module.index = index
            self.modules[ name ] = module
            index += 1
        # Every time loadModules is called it is Task's with lower prio
        self.prio += 1
        self.state = "Loaded prio: %d" % self.prio
        
    def initModules( self ):
        self.state = "Initializing"
        for name, module in self.modules.items( ) :
            module.task.init( )
        self.log( self, "All Tasks initialized" )
        self.state = "Initialized"
            
    def confModules( self ):
        self.state = "Configuration"
        prio = 0
        while prio < self.prio :
            for name, module in self.modules.items( ) :
                if module.prio == prio :
                    if os.access( 'conf/global.conf', os.R_OK ):
                        execfile( 'conf/global.conf', { 'task' : module.task })
                    if module.conf :
                        if os.access( module.conf, os.R_OK ):
                            execfile( module.conf, { 'task' : module.task } )
                        else:
                            print 'Warning: %s could not be read' % module.conf
                    module.task.conf( )
            prio += 1
        self.state = "Configured"
            
    def runModules( self ):
        self.state = "Starting"
        prio = 0
        while prio < self.prio :
            for name, module in self.modules.items( ) :
                if module.prio == prio:
                    module.runner.start( )
                    module.proxy.start( )
                    self.log( module.task, "Starting runner: %s" % name )
            prio += 1
        self.state = "Running"

    def closeModules( self ):
        self.state = "Closing"
        prio = self.prio
        while prio >= 1 :
            prio -= 1
            stopped = False
            for name, module in self.modules.items( ) :
                if module.prio == prio :
                    module.proxy.close( )
                    stopped = True
            if stopped :
                time.sleep( 1 )                             # A little time to settle down
        self.state = "Closed"
            
    def shutdown( self ):                 
        self.state = "Shutting"
        while self.prio > 0 :
            self.prio -= 1
            self.log( self, "Shutdown level %d" % self.prio )
            for name, module in self.modules.items( ): # Stop the threads
                if module.prio == self.prio :
                    module.runner.stop( )
        self.state = "Shutdown"
                    
    def dumpModules( self ):
        template = "{0}\t{1}\t{2}"
        print( template.format( "Task", "State", "Queue" ))
        for name, module in list( self.modules.items( )):
            print( template.format( name, module.runner.state, module.runner.queue.qsize( )))
                   
    def get_service( self, service ):
        return self.modules[ service ].proxy

    def get_modules( self ):
        return self.modules.values()

