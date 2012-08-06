from pyworks.net import NetTask, ServerConnection, AsciiProtocol, STXETXProtocol


class EchoServerTask( NetTask ):
    def init( self ):
        address = ('localhost', 0) # let the kernel give us a port
        self.conn = ServerConnection( self.get_service( ), address, protocol=AsciiProtocol )
        self.count = 1
        
    def conf( self ):
        self.conn.connect( )

    def net_ready( self, address ):
        print 'Net is ready....%s:%d' % address
        self.dispatch( ).server_ready( address )
        
    def net_up( self, conn, level ):
        self.log( 'Server up %d, %s' % ( level, conn.address ))
        
    def net_down( self, conn, level ):
        self.log( 'Server down %d, %s' % ( level, conn.address ))
        
    def net_received( self, conn, tlg ):
        self.log( "Server received: '%s'" % tlg )
        conn.send( 'From Server count: %d' % self.count )
        self.count += 1
        
    def net_timeout( self, conn ):
        self.log( 'Server: net_timeout' )

    def timeout( self ):
        conn.send( 'timeout')
        
    def activated( self ):
        self.log( 'ACTIVATED...' )
        
        
