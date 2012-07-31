from pyworks.net import NetTask, ClientConnection

class EchoClientTask( NetTask ):
    def init( self ):
        self.client = None
        self.count = 0
        self.conn = None
        
    def conf( self ):
        self.add_listener( "netserver" )
        print "EchoClient conf...."
        
    def server_ready( self, address ):
        print 'The server is ready, connect...', address
        if self.conn is not None :
            print 'Up again ????'
            return
        self.conn = ClientConnection( self.get_service( ), address )
        self.conn.start()
        print 'client task started...'
        
    def net_up( self, conn ):
        print 'Client up: ', conn.address

    def net_down( self, conn ):
        print 'Client down: ', conn.address

    def net_received( self, conn, buf ):
        print 'Client received: <%s>' % buf
        conn.send( "Right back at you" )
        
    def net_timeout( self, conn ):
        print 'Client: net_timeout', conn.address
        conn.send( "Wake up" )
        
    def timeout( self ):
        print 'Client: timeout', self.conn
        if self.conn is not None :
            self.conn.send( 'Hello from Client: %d' % self.count )
            self.count += 1
