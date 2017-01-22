import threading
from pyworks import Task
from pyworks.taskmanager import ManagerManager
from web.views import app, init_db
from waitress import serve
from web.websocketserver import WebSocketServer, WebSocket


class WebServer(Task):
    def init(self):
        init_db()

    def start(self):
        app.config.update(dict(
                COWORKS=self._manager
               ))
        serve(app, host='0.0.0.0', port=5000)


class TestTask(Task):
    def init(self):
        self.n = 0

    def conf(self):
        self.wsocket = self.get_service("ws")

    def send(self, msg):
        self.wsocket.send("message:%s" % msg)

    def timeout(self):
        # print "Timeout in Test"
        self.wsocket.send("alarms:%d" % self.n)
        self.n += 1
        if self.n % 13 == 0:
            self.n = 0


class WsHandler(WebSocket):
    def handleConnected(self):
        manager = ManagerManager.get_manager()
        self.ws = manager.get_service("ws")
        self.ws.add_client(self)

    def handleClose(self):
        self.ws.del_client(self)

    def handleMessage(self):
        self.ws.message(self.data)


class SocketServer(Task):
    def init(self):
        self.clients = []

    def conf(self):
        self.server = WebSocketServer(self.host, self.port, WsHandler)
        self.ws_thread = threading.Thread(target=self.server.serveforever)
        self.ws_thread.daemon = True

    def start(self):
        self.ws_thread.start()

    def message(self, message):
        self.debug("Got a message from a client: %s" % message)

    def del_client(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def add_client(self, client):
        if client not in self.clients:
            self.clients.append(client)
            self.log("New client added")

    def send(self, message):
        for client in self.clients:
            self.debug("in send %s to %s" % (message, client))
            client.sendMessage(message)
