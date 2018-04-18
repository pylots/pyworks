from pyworks.core import register

from .worker import WorkerTask
from .client import ClientTask
from .statetask import StateTask
from .netclient import EchoClientTask
from .netserver import EchoServerTask
from .mathactor import MathActor

register.task(WorkerTask, name="worker")
register.task(ClientTask, name="client1", conf="example/conf/client.py")
register.task(ClientTask, name="client2", conf="example/conf/client.py")
register.task(ClientTask, name="client3", conf="example/conf/client.py")
register.task(StateTask)
register.task(EchoServerTask, name="netserver")
register.task(EchoClientTask, name="netclient")
register.actor(MathActor)

from example.ring import RingActor

#for r in range(100):
#    register.task(RingActor, name="ring%d" % r, index=r, conf="example/conf/ring.py")

from .timeout import TimePingTask, TimeoutTask

register.task(TimeoutTask)
register.task(TimePingTask)
