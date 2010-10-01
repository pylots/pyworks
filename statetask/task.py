from pyworks import Task, State

class BaseState( State ):
    def timeout( self ):
        self.task.log( "Timeout in BaseState" )

    def worker_done( self, msg ):
        self.log( "Received worker_done in Wrong state: %s" % self )
    
    def close( self ):
        self.task.closed( )
        
class InitialState( BaseState ):
    def timeout( self ):
        self.log( "timeout in InitialState" )
        self.new_state( TimeoutState )

class TimeoutState( BaseState ):
    def timeout( self ):
        self.log( "timeout in TimeoutState" )
        
    def worker_done( self, msg ):
        self.log( "The worker is done, going back to TimeoutState" )
        self.new_state( InitialState )
        
    def close( self ):
        self.task.close( )
        
class StateTask( Task ):
    def init( self ):
        self.log( "StateTask init" )
        self.state.new_state( InitialState )
        
    def conf( self ):
        self.add_listener( "worker" )
        
