from example.worker import WorkerTask
# conf.addTask( "worker", WorkerTask )

from example.client import ClientTask

# conf.addTask( "client1", ClientTask, conf="example/conf/client.py" )
# conf.addTask( "client2", ClientTask, conf="example/conf/client.py" )
# conf.addTask( "client3", ClientTask, conf="example/conf/client.py" )

from example.statetask import StateTask
# conf.addTask( "stateclient", StateTask )

from example.netserver import EchoServerTask
# conf.addTask( "netserver", EchoServerTask )

from example.netclient import EchoClientTask
# conf.addTask( "netclient", EchoClientTask )

from example.ring import RingTask
for r in range( 100 ):
    conf.addTask( "ring%d" % r, RingTask, index=r, conf="example/conf/ring.py" )
