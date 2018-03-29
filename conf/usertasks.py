from example.worker import WorkerActor
# conf.addTask( "worker", WorkerActor )

from example.client import ClientActor

# conf.addTask( "client1", ClientActor, conf="example/conf/client.py" )
# conf.addTask( "client2", ClientActor, conf="example/conf/client.py" )
# conf.addTask( "client3", ClientActor, conf="example/conf/client.py" )

from example.statetask import StateActor
# conf.addTask( "stateclient", StateActor )

from example.netserver import EchoServerTask
# conf.addTask( "netserver", EchoServerTask )

from example.netclient import EchoClientTask
# conf.addTask( "netclient", EchoClientTask )

from example.ring import RingActor
for r in range( 100 ):
    conf.add_task("ring%d" % r, RingActor, index=r, conf="example/conf/ring.py")
