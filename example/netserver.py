from pyworks.net import NetActor, ServerConnection, AsciiProtocol, STXETXProtocol


class EchoServerTask(NetActor):
    def init(self):
        address = ('localhost', 8080)
        self.conn = ServerConnection(self.actor(), address, protocol=AsciiProtocol)
        self.count = 1

    def conf(self):
        self.conn.connect()

    def net_ready(self, address):
        self.log('Net is ready....%s:%d' % address)
        self.notify().server_ready(address)

    def net_up(self, conn, level):
        self.log('Server up %d, %s' % (level, conn.address))

    def net_down(self, conn, level):
        self.log('Server down %d, %s' % (level, conn.address))

    def net_received(self, conn, tlg):
        self.log("Server received: '%s'" % tlg)
        # conn.send('From Server count: %d' % self.count)
        self.count += 1

    def net_timeout(self, conn):
        self.log('Server: net_timeout')

    def timeout(self):
        # self.conn.send('timeout')
        pass

    def activated(self):
        self.log('ACTIVATED...')
