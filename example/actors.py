from pyworks.core import actor

from example.worker import WorkerActor
from example.client import ClientActor
from example.stateactor import StateActor
from example.netclient import EchoClientTask
from example.netserver import EchoServerTask

actors = [
    actor("worker", WorkerActor ),
    actor("client1", ClientActor, conf="example/conf/client.py" ),
    actor("client2", ClientActor, conf="example/conf/client.py" ),
    actor("client3", ClientActor, conf="example/conf/client.py" ),
    actor("stateclient", StateActor ),
    actor("netserver", EchoServerTask ),
    actor("netclient", EchoClientTask )
]

from example.ring import RingActor
for r in range(100):
    actors.append(actor("ring%d" % r, RingActor, index=r, conf="example/conf/ring.py"))
