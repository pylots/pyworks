from pyworks.net import NetActor, ServerConnection, AsciiProtocol, STXETXProtocol


class EchoServerTask(NetActor):
    def init(self):
        address = ('localhost', 5050)
        self.conn = ServerConnection(self.actor(), address, protocol=AsciiProtocol)
        self.count = 1
        self.log("Server conn: %s" % self.conn)

    def conf(self):
        self.conn.connect()
        self.log("Server connected...")

    def net_ready(self, address):
        self.log('Server is ready....%s:%d' % address)
        self.observers.server_ready(address)

    def net_up(self, conn, level):
        self.log('Server up %d, %s' % (level, conn.address))

    def net_down(self, conn, level):
        self.log('Server down %d, %s' % (level, conn.address))

    def net_received(self, conn, tlg):
        self.log("Server received: '%s'" % tlg)
        conn.send('From Server count: %d' % self.count)
        self.count += 1

    def net_timeout(self, conn):
        self.log('Server: net_timeout')

    def timeout(self):
        # self.conn.send('timeout')
        pass

    def activated(self):
        self.log('ACTIVATED...')
