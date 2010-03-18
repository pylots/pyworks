from pyworks import Task, State

class BaseState( State ):
    def timeout( self ):
        self.task.log( "Timeout in BaseState" )
        
class InitialState( BaseState ):
    def timeout( self ):
        self.log( "timeout in initial state" )
        self.new_state( TimeoutState )

class TimeoutState( BaseState ):
    def timeout( self ):
        self.log( "timeout in timeout state" )
        

class StateTask( Task ):
    def init( self ):
        self.log( "StateTask init" )
        self.state.new_state( InitialState )
        
