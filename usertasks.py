from client.client import ClientTask
from worker.worker import WorkerTask
from statetask.statetask import StateTask

conf.addTask( "worker", WorkerTask )
conf.addTask( "client1", ClientTask, conf="client/client.conf" )
conf.addTask( "client2", ClientTask, conf="client/client.conf" )
conf.addTask( "client3", ClientTask, conf="client/client.conf" )
conf.addTask( "stateclient", StateTask )
