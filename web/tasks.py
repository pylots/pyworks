import threading
from pyworks import Task
from web.views import app, init_db
from wsgiref.simple_server import make_server
from web.ws import ws_server

class WebServer( Task ):
    def init( self ):
        init_db( )

    def start( self ):
        app.config.update(dict(
                COWORKS=self._manager
                ))
        httpd = make_server( '0.0.0.0', 5000, app )
        httpd.serve_forever( )

class TestTask( Task ):
    def init( self ):
        self.n = 0

    def conf( self ):
        self.wsocket = self.get_service( "ws" )
        
    def send( self, msg ):
        self.wsocket.send( "message:%s" % msg )
        
    def timeout( self ):
        # print "Timeout in Test"
        self.wsocket.send( "alarms:%d" % self.n )
        self.n += 1
        if self.n % 13 == 0 :
            self.n = 0

class SocketServer( Task ):
    def init( self ):
        self.clients = []

    def conf( self ):
        self.server = ws_server( self.host, self.port, self.get_manager( ))
        self.ws_thread = threading.Thread( target=self.server.serve_forever )
        self.ws_thread.daemon = True

    def start( self ):
        self.ws_thread.start( )
    
    def message( self, message ):
        self.log( "Got a message from a client: %s" % message )
        
    def del_client( self, client ):
        if client in self.clients :
            self.clients.remove( client )
                
    def add_client( self, client ):
        if not client in self.clients :
            self.clients.append( client )
            self.log( "New client added" )
            
    def send( self, message ):
        for client in self.clients :
            self.log( "in send %s to %s" % ( message, client ))
            client.send_message( message )
