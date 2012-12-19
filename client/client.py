from pyworks import Task, FutureShock, Filter, Future

from time import time

class ClientFilter( Filter ):
    def filter( self, method, *args, **kwargs ):
        # We just want everything
        return True
    
class ClientTask( Task ) :
    def setNtimeout( self, n ):
        self.ntimeout = n
        
    def init( self ):
        self.ntimeout = 0
        self.answers = []
        self.worker = self.get_service( "worker" )

    def conf( self ):
        self.add_listener( "worker", filter=ClientFilter( )  )

    def timeout( self ):
        self.log( "timeout: %d" % self.ntimeout )
        self.ntimeout += 1
        if self.ntimeout == 2 or self.ntimeout == 4 :
            return
            start = time()
            n = 10000 * self.ntimeout
            for i in range( n ):
                a = self.worker.hello( i, "hello, from %s: %d" % ( self.get_name( ), self.ntimeout ))
                self.answers.append( a )
            t = time() - start
            self.log( "%.0f msg/sec" % ( float( n ) / t ))

        if self.ntimeout == 3 :
            self.log( "Doing longwork" )
            future = Future( )
            self.worker.start_long_work( future )
            try:
                self.log ( "long answer 1 = %d" % future.get_value( 2 ))
            except FutureShock :
                self.log( "Ahh, I gave up waiting for longwork, try a little longer" )
                self.log ( "long answer 2 = %d" % future.get_value( 10 ))
                self.log ( "long answer 3 = %d" % future.get_value( ))

        if self.ntimeout == 5 :
            return
            sum = 0
            for r in self.answers :
                sum = sum + r
            self.log( "result = %s" % sum )

    def close( self ):
        self.log( "closing" )
        self.closed( )
        
    def worker_done( self, msg ):
        self.log( "The worker task is done: %s" % msg )
        
