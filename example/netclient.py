from pyworks.net import NetTask, ClientConnection, AsciiProtocol, STXETXProtocol


class EchoClientTask(NetTask):
    def pw_initialized(self):
        self.client = None
        self.count = 0
        self.conn = None

    def pw_configured(self):
        self.observe("netserver")

    def server_ready(self, address):
        self.log('The server is ready, connect...%s:%d' % (address))
        if self.conn is not None:
            self.log("Connection already UP!")
            return
        self.conn = ClientConnection(self.actor(), address, protocol=AsciiProtocol)
        self.conn.connect()
        
    def net_up(self, conn, level):
        self.log('Client up: %d, %s' % (level, conn.address))

    def net_down(self, conn, level):
        self.log('Client down: %d, %s' % (level, conn.address))

    def net_received(self, conn, tlg):
        # self.log("Client received: '%s'" % tlg)
        conn.send("Right back at you")

    def net_timeout(self, conn):
        self.log('Client: net_timeout: %s:%s' % (conn.address))
        conn.send("Wake up")

    def pw_timeout(self):
        if self.conn is not None:
            self.log('Client: timeout: %s:%d' % (self.conn.address))
            self.conn.send('Hello from Client: %d' % self.count)
            self.count += 1
