import sys
from socket import *
from select import select
from threading import Thread
from Queue import Queue, Empty

from pyworks import Task


class Connection( Thread ):
    def __init__( self, task, address, connections=1 ):
        Thread.__init__( self )
        self.task = task
        self.address = address
        self.connections = connections
        self.setDaemon( True )
        self.q = Queue( )
        self.sock = None
        print 'Thread init......................'
        
    def send( self, msg ):
        self.q.put( msg )
        
    def level1( self ):
        return True

    def level2( self ):
        return True

    def level3( self ):
        try:
            buf = self.q.get( False )
            self.sock.send( buf )
        except Empty :
            pass
        try :
            inputs = [ self.sock ]
            outputs = []
            self.sock.setblocking( 0 ) # Jython compatibility
            input, output, x = select( inputs, [], [], 1 )
            if not input :
                self.task.net_timeout( self )
                return True
            msg = self.sock.recv( 4096 )
            self.task.net_received( self, msg )
        except:
            print "Exception in recv", sys.exc_info()
            self.task.net_down( self )
            return False
        return True
    
    def run( self ):
        print 'level1.'
        while self.level1( ):
            print 'level2..'
            while self.level2( ):
                print 'level3...'
                while self.level3( ):
                    pass


class Protocol :
    pass


class ServerConnection( Connection ):
    def level1( self ):
        self.serversocket = socket( AF_INET, SOCK_STREAM )
        self.serversocket.bind((self.address))
        self.serversocket.listen( 1 )
        host, port = self.serversocket.getsockname( )
        self.task.net_ready(( host, port ))
        return True
        
    def level2( self ):
        try :
            (self.sock, address) = self.serversocket.accept()
        except:
            print 'Exception: ', sys.exc_info()[1]
            self.task.net_down( self )
            return False
        self.task.net_up( self )
        return True


class ClientConnection( Connection ):
    def level2( self ):
        self.sock = socket( AF_INET, SOCK_STREAM)
        print 'connecting to: ', self.address
        self.sock.connect((self.address))
        self.task.net_up( self )
        return True


class NetTask( Task ):
    def net_ready( self, address ):
        pass
    
    def net_up( self, conn ):
        pass
        
    def net_down( self, conn ):
        pass
        
    def net_received( self, conn, msg ):
        pass

    def net_timeout( self, conn ):
        pass
        

