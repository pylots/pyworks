from client.task import ClientTask
from worker.task import WorkerTask
from statetask.task import StateTask

conf.addTask( "worker", WorkerTask )
conf.addTask( "client1", ClientTask, conf="client/client.conf" )
conf.addTask( "client2", ClientTask, conf="client/client.conf" )
conf.addTask( "client3", ClientTask, conf="client/client.conf" )
conf.addTask( "stateclient", StateTask )
