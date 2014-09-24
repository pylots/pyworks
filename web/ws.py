import struct, time
import SocketServer
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO

import threading, time

from pyworks.util import Logger, DEBUG, WARN, ERROR

class WebSocketsHandler(SocketServer.StreamRequestHandler):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        # print "connection established: %s on %s" % ( self.client_address, threading.current_thread( ).name )
        self.handshake_done = False
        self.wserver = None
        self.logger = Logger( name="ws", logfile="web" )
        print "Logger is ", self.logger
        self.logger.log( WARN, "Ready...")

    def handle(self):
        while True:
            if not self.handshake_done:
                try:
                    self.handshake( )
                except:
                    if self.wserver :
                        self.wserver.del_client( self )
                        self.wserver = None
                if self.handshake_done and self.wserver == None :
                    self.wserver = self.manager.get_service( "ws" )
                    self.wserver.add_client( self )
                else:
                    time.sleep( 1 )
            else:
                self.read_next_message()
 
    def read_next_message(self):
        start = self.rfile.read( 2 )
        if len( start ) == 0 :
            self.logger.log( WARN, "read_next_message: read 0" )
            self.handshake_done = False
            return
        if len( start ) < 2 :
            self.logger.log( WARN, "read_next_message: read < 2" )
            return
        # length = ord(self.rfile.read(2)[1]) & 127
        length = ord( start[ 1 ]) & 127
        if length == 126:
            length = struct.unpack(">H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self.rfile.read(8))[0]
        masks = [ord(byte) for byte in self.rfile.read(4)]
        decoded = ""
        for char in self.rfile.read(length):
            decoded += chr(ord(char) ^ masks[len(decoded) % 4])
        self.on_message(decoded)
 
    def send_message(self, message):
        self.request.send(chr(129))
        length = len(message)
        if length <= 125:
            self.request.send(chr(length))
        elif length >= 126 and length <= 65535:
            self.request.send(126)
            self.request.send(struct.pack(">H", length))
        else:
            self.request.send(127)
            self.request.send(struct.pack(">Q", length))
        self.request.send(message)
 
    def handshake(self):
        data = self.request.recv(1024).strip()
        if len( data ) < 1 :
            return
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None) != "websocket":
            return
        self.logger.log( DEBUG, 'Handshaking...' )
        key = headers['Sec-WebSocket-Key']
        digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
        response = 'HTTP/1.1 101 Switching Protocols\r\n'
        response += 'Upgrade: websocket\r\n'
        response += 'Connection: Upgrade\r\n'
        response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
        self.handshake_done = self.request.send(response)
        return self.handshake_done
    
    def on_message(self, message):
        self.wserver.message( message )
 

class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

        
class ws_server( object ):
    def __init__( self, host, port, manager ):
        self.host = host
        self.port = port
        self.manager = manager
        self.handler = WebSocketsHandler
        self.handler.manager = manager
        self.server = ThreadedServer(( host, port ), self.handler )
        
    def serve_forever( self ):
        self.server.serve_forever( )
