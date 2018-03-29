from pyworks.core import actor

from .servers import WebServer, TestActor, SocketServer

actors = [
    actor("ux", WebServer, conf="./web/web.conf"),
    actor("wstest", TestActor, conf="./web/web.conf"),
    actor("ws", SocketServer, conf="./web/ws.conf")
]
