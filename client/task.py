from pyworks import Task, Future, FutureShock

from time import time

class ClientTask( Task ) :
    def setNtimeout( self, n ):
        self.ntimeout = n
        
    def init( self ):
        self.ntimeout = 0
        self.answers = []
        self.worker = self.get_service( "worker" )

    def conf( self ):
        self.add_listener( "worker" )

    def timeout( self ):
        self.log( "timeout: %d" % self.ntimeout )
        if self.ntimeout == 2 :
            start = time()
            n = 10000
            for i in range( n ):
                f = Future( )
                self.worker.hello( i, "hello, from %s: %d" % ( self.name, self.ntimeout ), future=f )
                self.answers.append( f )
            t = time() - start
            self.log( "%.0f msg/sec" % ( float( n ) / t ))

        if self.ntimeout == 3 :
            x = Future( )
            self.worker.longwork( future=x )
            try:
                self.log ( "long answer = %d" % x.get_value( 2 ))
            except FutureShock :
                self.log( "Ahh, I gave up waiting for longwork" )

        if self.ntimeout == 5 :
            sum = 0
            for r in self.answers :
                sum = sum +r.get_value( )
            self.log( "result = %s" % sum )
        self.ntimeout += 1

    def worker_done( self, msg ):
        self.log( "The worker task is done: %s" % msg )
        
