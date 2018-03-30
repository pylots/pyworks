import os
login_manager = None
import threading

from pyworks import Actor
from pyworks.manager import ManagerManager
from pyworks.util import settings
from waitress import serve
from web.views import app, init_db
from web.websocketserver import WebSocketServer, WebSocket


class WebServer(Actor):

    def init(self):
        app.config.update(dict(
            PYWORKS=self._manager,
            DATABASE=os.path.join(settings.PRODIR, 'db', 'pyworks.db'),
            DEBUG=True,
            SECRET_KEY="IWKbfXW2UdK/WFVvmMQ96fKtKwFNs0WqDmYyyC3Wm0y5x7SKOCkcXYdF7aWqX51"
        ))
        init_db()

    def start(self):
        serve(app, host='0.0.0.0', port=5000)


class TestActor(Actor):

    def init(self):
        self.n = 0

    def conf(self):
        self.wsocket = self.actor("ws")

    def send(self, msg):
        self.wsocket.send("message:%s" % msg)

    def timeout(self):
        # print "Timeout in Test"
        self.wsocket.send("alarms:%d" % self.n)
        self.n += 1
        if self.n % 13 == 0:
            self.n = 0


class WsHandler(WebSocket):
    def __init__(self, server, sock, address):
        self.ws = None
        super().__init__(server, sock, address)

    def handle_connected(self):
        manager = ManagerManager.get_manager()
        self.ws = manager.get_actor("ws")
        self.ws.add_client(self)

    def handle_close(self):
        self.ws.del_client(self)

    def handle_message(self):
        self.ws.message(self.data)


class SocketServer(Actor):

    def init(self):
        self.clients = []

    def conf(self):
        self.server = WebSocketServer(self.host, self.port, WsHandler)
        self.ws_thread = threading.Thread(target=self.server.serveforever)
        self.ws_thread.daemon = True

    def start(self):
        self.ws_thread.start()

    def message(self, message):
        self.log("Got a message from a client: %s" % message)

    def del_client(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def add_client(self, client):
        if client not in self.clients:
            self.clients.append(client)
            self.log("New client added")

    def send(self, message):
        for client in self.clients:
            self.log("in send %s to %s" % (message, client))
            client.send_message(message)
