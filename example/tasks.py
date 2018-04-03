from pyworks.core import register

from example.worker import WorkerTask
from example.client import ClientTask
from example.statetask import StateTask
from example.netclient import EchoClientTask
from example.netserver import EchoServerTask


register.task("worker", WorkerTask)
register.task("client1", ClientTask, conf="example/conf/client.py")
register.task("client2", ClientTask, conf="example/conf/client.py")
register.task("client3", ClientTask, conf="example/conf/client.py")
register.task("statetask", StateTask)
register.task("netserver", EchoServerTask)
register.task("netclient", EchoClientTask)


from example.ring import RingActor
for r in range(100):
    register.task("ring%d" % r, RingActor, index=r, conf="example/conf/ring.py")
