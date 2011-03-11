from pyworks import Task, FutureShock, Filter

from time import time

class ClientFilter( Filter ):
    def filter( self, method, *args, **kwargs ):
        print "filter: %s" % method
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
        # self.log( "timeout: %d" % self.ntimeout )
        if self.ntimeout == 2 :
            start = time()
            n = 100
            for i in range( n ):
                a = self.worker.hello( i, "hello, from %s: %d" % ( self.name, self.ntimeout ))
                self.answers.append( a )
            t = time() - start
            self.log( "%.0f msg/sec" % ( float( n ) / t ))

        if self.ntimeout == 3 :
            self.log( "Doing longwork" )
            x = self.worker.longwork( )
            try:
                self.log ( "long answer = %d" % x )
            except FutureShock :
                self.log( "Ahh, I gave up waiting for longwork" )

        if self.ntimeout == 5 :
            sum = 0
            for r in self.answers :
                sum = sum + r
            self.log( "result = %s" % sum )
        self.ntimeout += 1

    def close( self ):
        self.log( "closing" )
        self.closed( )
        
    def worker_done( self, msg ):
        self.log( "The worker task is done: %s" % msg )
        
