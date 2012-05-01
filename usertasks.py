from worker.worker import WorkerTask
conf.addTask( "worker", WorkerTask )

from client.client import ClientTask
conf.addTask( "client1", ClientTask, conf="client/client.conf" )
conf.addTask( "client2", ClientTask, conf="client/client.conf" )
conf.addTask( "client3", ClientTask, conf="client/client.conf" )

from statetask.statetask import StateTask
conf.addTask( "stateclient", StateTask )

from ring.ring import RingTask
for r in range( 100 ):
    conf.addTask( "ring%d" % r, RingTask, index=r )
