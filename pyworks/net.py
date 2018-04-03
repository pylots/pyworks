import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from threading import Thread

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from pyworks import Task


class Protocol(object):

    def swrite(self, sock, buffer):
        sock.send(bytes(buffer, 'utf8'))

    def sread(self, sock):
        return sock.recv(4096)

    def send(self, sock, buffer):
        self.swrite(sock, buffer)

    def receive(self, sock):
        buffer = self.sread(sock)
        yield buffer

    def timeout(self, sock):
        return False


HUNT = 1
TELE = 2
SKIP = 3


class FramedProtocol(Protocol):

    def __init__(self, start='<', end='>', escape='\\'):
        self.start = start
        self.end = end
        self.escape = escape
        self.state = HUNT
        self.buffer = ""
        self.count = 0
        self.maxlen = 1000000

    def receive(self, sock):
        n = 0
        for line in str(self.sread(sock), 'utf8'):
            for c in line:
                n += 1
                if n > self.maxlen:
                    print("Telegram too long")
                    yield self.buffer

                if self.state == HUNT:
                    if c == self.start:
                        self.state = TELE
                elif self.state == SKIP:
                    self.buffer += c
                    self.state = TELE
                elif self.state == TELE:
                    if c == self.end:
                        yield self.buffer

                        self.state = HUNT
                        self.buffer = ""
                    elif c == self.escape:
                        self.state = SKIP
                    else:
                        self.buffer += c

    def send(self, sock, text):
        buffer = self.start
        for c in text:
            if c == self.start or c == self.end or c == self.escape:
                buffer += self.escape
            buffer += c
        buffer += self.end
        self.swrite(sock, buffer)


class TextProtocol(Protocol):
    pass


class AsciiProtocol(FramedProtocol):
    pass


class STXETXProtocol(FramedProtocol):

    def __init__(self):
        FramedProtocol.__init__(self, start='\x02', end='\x03', escape='\x1b')


class Connection(object):

    def __init__(self, actor, address, protocol=Protocol, connections=1):
        self.actor = actor
        self.address = address
        self.connections = connections
        self.q = Queue()
        self.sock = None
        self.protocol = protocol()
        self.t = None
        self.stop = False

    def connect(self):
        self.stop = False
        self.t = Thread(target=self.run)
        self.t.setDaemon(True)
        self.t.start()

    def disconnect(self):
        if self.stop == False and self.t is not None:
            self.stop = True
            while self.stop == True:
                time.sleep(1)

    def send(self, msg):
        self.q.put(msg)

    def level1(self):
        return True

    def level2(self):
        return True

    def level3(self):
        try:
            buf = self.q.get(False)
            self.protocol.send(self.sock, buf)
        except Empty:
            pass
        except Exception as e:
            self.actor.log("Send exception: %s" % e)
        try:
            inputs = [self.sock]
            # self.sock.setblocking(0) # Jython compatibility
            inp, outp, x = select(inputs, [], [], 0.1)
            if not inp:
                if self.protocol.timeout(self):
                    self.actor.net_timeout(self)
                return True

            for telegram in self.protocol.receive(self.sock):
                self.actor.net_received(self, telegram)
        except:
            self.actor.log("Exception in socket.recv: %s" % sys.exc_info()[1])
            return False

        return True

    def run(self):
        try:
            self.actor.log('%s running' % self)
            while self.stop is False:
                while self.level1() and self.stop is False:
                    self.actor.log("Level 1")
                    self.actor.net_up(self, 1)
                    while self.level2() and self.stop is False:
                        self.actor.log("Level 2")
                        self.actor.net_up(self, 2)
                        while self.level3() and self.stop is False:
                            pass
                        self.actor.net_down(self, 2)
                    self.actor.net_down(self, 1)
                    time.sleep(5)
                time.sleep(5)
        except:
            self.actor.log("Exception in run: %s" % sys.exc_info()[1])
            pass
        self.actor.log("closing socket")
        if self.sock:
            self.sock.close()
        self.sock = None
        self.stop = False
        self.actor.log('%s stopped' % self)


class ServerConnection(Connection):

    def level1(self):
        try:
            self.serversocket = socket(AF_INET, SOCK_STREAM)
            self.serversocket.bind((self.address))
            self.serversocket.listen(1)
            host, port = self.serversocket.getsockname()
            self.actor.net_ready((host, port))
        except:
            self.actor.log("ServerConnection Exception: %s" % sys.exc_info()[1])
            return False

        return True

    def level2(self):
        try:
            (self.sock, address) = self.serversocket.accept()
        except:
            self.actor.log('Exception in accept: %s' % sys.exc_info()[1])
            return False

        return True


class ClientConnection(Connection):

    def level2(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.address))
        except:
            self.actor.log("ClientConnect Exception: %s" % sys.exc_info()[1])
            return False

        return True


class NetTask(Task):

    def net_ready(self, address):
        pass

    def net_up(self, conn, level):
        pass

    def net_down(self, conn, level):
        pass

    def net_received(self, conn, msg):
        self.info("received: " + msg)

    def net_timeout(self, conn):
        pass
