from pyworks import Task, FutureShock, Filter

from time import time

class RingTask( Task ) :
    """
    Send messages to next Task in Ring
    """        
    def init( self ):
        self.count = 1
        self.n = self.index + 1
        if self.index == 99 :
            self.n = 0
        self.log( "%s: ring%d->ring%d" % ( self.name, self.index, self.n ))
        self.next = self.get_service( "ring%d" % self.n )

    def conf( self ):
        self.add_listener( "ring%d" % self.n )

    def setCount( self, count ):
        self.count = count

    def setMessages( self, nmsg ):
        self.nmsg = nmsg
        
    def ringop( self, name, n ):
        if n % 10001 == 0 :
            self.log( "%s: from %s n=%d" % ( self.name, name, n ))
        if n < 1000000 :
            self.next.ringop( self.name, n + 1 )
        if n == 1000000 :
            self.log( "Done: %d secs" % ( time() - self.start ))
        
    def timeout( self ):
        self.start = time()
        if self.count > 0 and self.index == 0 :
            self.log( "%s calling next with %d" % ( self.name, self.n ))
            self.next.ringop( self.name, self.n )
        self.count -= 1
