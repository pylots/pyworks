import time

from pyworks import Task

class WorkerTask( Task ) :
    def init( self ):
        self.ntimeout = 0
        
    def hello( self, n, msg ):
        if n % 2345 == 0 :
            size = self.manager.modules[ self.name ].runner.queue.qsize( )
            self.log( "%02d: worker hello: %s, size=%s" % ( n, msg, size ))
        return n
        
    def longwork( self ):
        time.sleep( 5 )
        return 42
    
    def timeout( self ):
        self.ntimeout += 1
        self.log( "timeout in worker: %d" % self.ntimeout )
        if self.ntimeout == 4 :
            self.dispatch( ).worker_done( "good-bye" )

        if self.ntimeout == 5 :
            self.log( "Well thats it, bye" )
        
    def close( self ):
        self.closed( )
        
