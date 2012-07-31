from pyworks.net import NetTask, ServerConnection

class EchoServerTask( NetTask ):
    def init( self ):
        address = ('localhost', 0) # let the kernel give us a port
        self.conn = ServerConnection( self.get_service( ), address )
        self.count = 1
        
    def conf( self ):
        self.conn.start()
        print "EchoServer conf...."

    def net_ready( self, address ):
        print 'Net is ready....%s:%d' % address
        self.dispatch( ).server_ready( address )
        print 'DID dispatch...'
        
    def net_up( self, conn ):
        print 'Server up', conn.address
        
    def net_down( self, conn ):
        print 'Server down', conn.address
        
    def net_received( self, conn, buf ):
        print "Server received: <%s>" % buf
        conn.send( 'From Server count: %d' % self.count )
        self.count += 1
        
    def net_timeout( self, conn ):
        print 'Server: net_timeout'
        
    def activated( self ):
        print "ACTIVATED...."
        
        
