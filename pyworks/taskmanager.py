try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
        
from threading import Thread
import sys, threading, time, os, traceback
from pyworks import Future, NoFuture, syslog
from .util import WARN, ERROR, DEBUG


class Module( object ):
    def __init__( self, name, conf, factory, task=None, proxy=None, runner=None ):
        self.name, self.conf, self.factory, self.task, self.proxy, self.runner = name, conf, factory, task, proxy, runner
        self.index = 0
        self.pid = 0
        self.prio = 5
        self.listeners = {}
        self.daemon = 0
        
    def get_listeners( self ):
        return self.listeners.values( )
    

class InternalFuture( Future ):
    # Methods for transparcy, so in stead of:
    #   n += task.method( ).get_value( )
    # you can do
    #   n += task.method( )
    def __add__(self, other): return self.get_value( ).__add__( other )
    def __sub__(self, other): return self.get_value( ).__sub__( other )
    def __mul__(self, other): return self.get_value( ).__mul__( other )
    def __floordiv__(self, other): return self.get_value( ).__floordiv__( other )
    def __mod__(self, other): return self.get_value( ).__mod__( other )
    def __divmod__(self, other): return self.get_value( ).__divmod__( other )
    def __pow__(self, other, modulo=1): return self.get_value( ).__pow__( other, modulo )
    def __lshift__(self, other): return self.get_value( ).__lshift__( other )
    def __rshift__(self, other): return self.get_value( ).__rshift__( other )
    def __and__(self, other): return self.get_value( ).__and__( other )
    def __xor__(self, other): return self.get_value( ).__xor__( other )
    def __or__(self, other): return self.get_value( ).__or__( other )
    def __div__(self, other): return self.get_value( ).__div__( other )
    def __truediv__(self, other): return self.get_value( ).__truediv__( other )
    def __radd__(self, other): return self.get_value( ).__radd__( other )
    def __rsub__(self, other): return self.get_value( ).__rsub__( other )
    def __rmul__(self, other): return self.get_value( ).__rmul__( other )
    def __rdiv__(self, other): return self.get_value( ).__rdiv__( other )
    def __rtruediv__(self, other): return self.get_value( ).__rtruediv__( other )
    def __rfloordiv__(self, other): return self.get_value( ).__rfloordiv__( other )
    def __rmod__(self, other): return self.get_value( ).__rmod__( other )
    def __rdivmod__(self, other): return self.get_value( ).__rdivmod__( other )
    def __rpow__(self, other): return self.get_value( ).__rpow__( other )
    def __rlshift__(self, other): return self.get_value( ).__rlshift__( other )
    def __rrshift__(self, other): return self.get_value( ).__rrshift__( other )
    def __rand__(self, other): return self.get_value( ).__rand__( other )
    def __rxor__(self, other): return self.get_value( ).__rxor__( other )
    def __ror__(self, other): return self.get_value( ).__ror__( other )
    def __iadd__(self, other): return self.get_value( ).__iadd__( other )
    def __isub__(self, other): return self.get_value( ).__isub__( other )
    def __imul__(self, other): return self.get_value( ).__imul__( other )
    def __idiv__(self, other): return self.get_value( ).__idiv__( other )
    def __itruediv__(self, other): return self.get_value( ).__itruediv__( other )
    def __ifloordiv__(self, other): return self.get_value( ).__ifloordiv__( other )
    def __imod__(self, other): return self.get_value( ).__imod__( other )
    def __ipow__(self, other, modulo=1): return self.get_value( ).__ipow__( other, modulo )
    def __ilshift__(self, other): return self.get_value( ).__ilshift__( other )
    def __irshift__(self, other): return self.get_value( ).__irshift__( other )
    def __iand__(self, other): return self.get_value( ).__iand__( other )
    def __ixor__(self, other): return self.get_value( ).__ixor__( other )
    def __ior__(self, other): return self.get_value( ).__ior__( other )
    def __neg__(self): return self.get_value( ).__neg__( )
    def __pos__(self): return self.get_value( ).__pos__( )
    def __abs__(self): return self.get_value( ).__abs__( )
    def __invert__(self): return self.get_value( ).__invert__( )
    def __complex__(self): return self.get_value( ).__complex__( )
    def __int__(self): return self.get_value( ).__int__( )
    def __long__(self): return self.get_value( ).__long__( )
    def __float__(self): return self.get_value( ).__float__( )
    def __oct__(self): return self.get_value( ).__oct__( )
    def __hex__(self): return self.get_value( ).__hex__( )
    def __index__(self): return self.get_value( ).__index__( )
    def __coerce__(self, other): return self.get_value( ).__coerce__( other )
    def __str__(self): return self.get_value( ).__str__( )
    def __repr__(self): return self.get_value( ).__repr__( )
    def __unicode__(self): return self.get_value( ).__unicode__( )


class DistributedMethod :
    def __init__( self, task, name, future, *args, **kwds ):
        self.task, self.name, self.future, self.args, self.kwds = task, name, future, args, kwds


class DispatchMethodWrapper:
    def __init__( self, task, method ):
        self.task, self.method = task, method

    def __call__( self, *args, **kwds ):
        # dispatch to all the listeners
        for listener in self.task.get_listeners( ):
            if listener[ 'filter' ].filter( self.method, *args, **kwds ):
                listener[ 'task' ].get_queue( ).put( DistributedMethod( self.task, self.method, NoFuture(), *args, **kwds))


class ProxyMethodWrapper:
    def __init__( self, task, queue, name ):
        self.task, self.queue, self.name = task, queue, name

    def __call__( self, *args, **kwds ):
        f = InternalFuture( )
        self.queue.put( DistributedMethod( self.task, self.name, f, *args, **kwds))
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
            return ProxyMethodWrapper( self._name, self._runner.queue, name )

    
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
                if not hasattr( self.task._state, m.name ):
                    syslog( "%s does not have %s" % ( self.task._state, m.name ))
                    self.task._state.not_implemented( m.name )
                    continue
                func = getattr( self.task._state, m.name )
                self.state = "Working"
                # print 'from %s, doing: %s' % ( m.task, func )
                try:
                    m.future.set_value( func( *m.args, **m.kwds ))
                except:
                    syslog( 'Exception: %s %s' % ( m.name, sys.exc_info( )[1]))
                    self.manager.log( self.task, "funccall %s failed: %s (%s)" % ( m.name, sys.exc_info( )[1], traceback.format_exc( ) ))
                    self.task._state.exception( m.name )
            except Empty :
                if self.state == "Ready" :
                    try:
                        self.task._state.timeout( )
                    except:
                        self.manager.log( self.task, "timeout %s failed: %s (%s)" % ( m.name, sys.exc_info( )[1], traceback.format_exc( ) ))
                        self.task._state.exception( m.name )
        self.state = "Stopped"


class Manager( object ):
    pid = 0
    def __init__( self, env="coworks" ):
        self.env = env
        self.modules = {}
        self.prio = 0
        self.name = "Manager"
        self.state = "Initial"
        
    def log( self, task, msg ):
        if self.state != "Running" :
            return
        module = self.modules[ "logger" ]
        qsize = module.runner.queue.qsize( )
        msg = "q:%d, %s" % ( qsize, msg )
        module.proxy.dolog( task, WARN, msg )
        
    def error( self, task, msg ):
        self.modules[ "logger" ].proxy.log( task, ERROR, msg )
    
    def loadModules( self, task_list, daemon=0 ):
        self.state = "Loading"
        index = 0
        for name, module in task_list.items( ) :
            module.name = name
            module.task = module.factory( module, self )
            module.task._dispatch = Dispatcher( module.task )
            module.runner = Runner( self, module )
            module.runner.daemon = daemon
            module.proxy = Proxy( module.runner, module.name )
            module.prio = self.prio
            module.index = index
            module.pid = Manager.pid
            module.daemon = daemon
            self.modules[ name ] = module
            index += 1
            Manager.pid += 1
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
                    if os.access( 'conf/%s.py' % self.env, os.R_OK ):
                        execfile( 'conf/%s.py' % self.env, { 'task' : module.task })
                    if module.conf :
                        if os.access( module.conf, os.R_OK ):
                            execfile( module.conf, { 'task' : module.task } )
                        else:
                            syslog( 'Warning: %s could not be read' % module.conf )
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
                    self.log( module.task, "%d: Starting runner: %s" % ( prio, name ))
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

    def get_module( self, name ):
        if name in self.modules :
            return self.modules[ name ]
        return None
    
