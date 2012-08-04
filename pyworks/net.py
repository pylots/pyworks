import sys, time
from socket import *
from select import select
from threading import Thread
from Queue import Queue, Empty

from pyworks import Task

class Protocol :
    def __init__( self ):
        pass
    
    def encode( self, msg ):
        return msg

    def decode( self, msg ):
        return msg
    
    def receive( self, sock ):
        tlg = sock.recv( 4096 )
        msg = self.decode( tlg )
        return msg
    
    def send( self, sock, msg ):
        tlg = self.encode( msg )
        sock.send( tlg )

    def timeout( self, sock ):
        return True

    
class AsciiProtocol( Protocol ):
    def encode( self, msg ):
        return "<<%s>>" % msg

    def decode( self, msg ):
        return msg[2:-2]

class STXETXProtocol( Protocol ):
    def encode( self, msg ):
        return "\x02%s\x03" % msg

    def decode( self, msg ):
        if msg[0] == 0x02 and msg[:-1] == 0x03 :
            print '<STX>%s<ETX>' % msg[1:-1]
            return msg[1:-1]
        

class Connection :
    def __init__( self, task, address, protocol=Protocol, connections=1 ):
        self.task = task
        self.address = address
        self.connections = connections
        self.q = Queue( )
        self.sock = None
        self.protocol = protocol( )
        
    def connect( self ):
        t = Thread( target=self.run )
        t.setDaemon( True )
        t.start( )
    
    def send( self, msg ):
        self.q.put( msg )
        
    def level1( self ):
        return True

    def level2( self ):
        return True

    def level3( self ):
        try:
            buf = self.q.get( False )
            self.protocol.send( self.sock, buf )
        except Empty :
            pass
        try :
            inputs = [ self.sock ]
            outputs = []
            self.sock.setblocking( 0 ) # Jython compatibility
            input, output, x = select( inputs, [], [], 1 )
            if not input :
                if self.protocol.timeout( self ):
                    self.task.net_timeout( self )
                return True
            tlg = self.protocol.receive( self.sock )
            self.task.net_received( self, tlg )
        except:
            self.task.log( "Exception in socket.recv: %s" % sys.exc_info()[1] )
            return False
        return True
    
    def run( self ):
        print '%s running' % self
        while True :
            while self.level1( ):
                self.task.net_up( self, 1 )
                while self.level2( ):
                    self.task.net_up( self, 2 )
                    while self.level3( ):
                        pass
                    self.task.net_down( self, 2 )
                self.task.net_down( self, 1 )
            time.sleep( 5 )


class ServerConnection( Connection ):
    def level1( self ):
        try:
            self.serversocket = socket( AF_INET, SOCK_STREAM )
            self.serversocket.bind((self.address))
            self.serversocket.listen( 1 )
            host, port = self.serversocket.getsockname( )
            self.task.net_ready(( host, port ))
        except:
            self.task.log( "ServerConnection Exception: %s" % sys.exc_info( )[1] )
            return False
        return True
        
    def level2( self ):
        try :
            (self.sock, address) = self.serversocket.accept()
        except:
            self.task.log( 'Exception in accept: %s' % sys.exc_info( )[1] )
            return False
        return True


class ClientConnection( Connection ):
    def level2( self ):
        try:
            self.sock = socket( AF_INET, SOCK_STREAM)
            self.sock.connect( (self.address) )
        except:
            self.task.log( "ClientConnect Exception: %s" % sys.exc_info( )[1] )
            return False
        return True


class NetTask( Task ):
    def net_ready( self, address ):
        pass
    
    def net_up( self, conn, level ):
        pass
        
    def net_down( self, conn, level ):
        pass
        
    def net_received( self, conn, msg ):
        pass

    def net_timeout( self, conn ):
        pass
        

