from pyworks.core import register

from .servers import WebServer, TestTask, SocketServer

register.task("ux", WebServer, conf="./web/web.conf"),
register.task("wstest", TestTask, conf="./web/web.conf"),
register.task("ws", SocketServer, conf="./web/ws.conf")
