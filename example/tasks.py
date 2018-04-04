from pyworks.core import register

from .worker import WorkerTask
from .client import ClientTask
from .statetask import StateTask
from .netclient import EchoClientTask
from .netserver import EchoServerTask
from .mathactor import MathActor

register.task("worker", WorkerTask)
register.task("client1", ClientTask, conf="example/conf/client.py")
register.task("client2", ClientTask, conf="example/conf/client.py")
register.task("client3", ClientTask, conf="example/conf/client.py")
register.task("statetask", StateTask)
register.task("netserver", EchoServerTask)
register.task("netclient", EchoClientTask)
register.actor('math', MathActor)

from example.ring import RingActor

for r in range(100):
    register.task("ring%d" % r, RingActor, index=r, conf="example/conf/ring.py")
