from pyworks.core import register

from .servers import WebServer, TestTask, SocketServer

register.task(WebServer, name="ux", conf="web/web.conf"),
register.task(TestTask, name="wstest", conf="web/web.conf"),
register.task(SocketServer, name="ws", conf="web/ws.conf")
