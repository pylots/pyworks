from client.task import ClientTask
from worker.task import WorkerTask
from statetask.task import StateTask
from dmodel.task import DomainModelTask
from opc.task import OPCTask
from gui.task import GUITask
from security.task import SecurityTask
from alarm.task import AlarmTask

#conf.addTask( "worker", WorkerTask )
#conf.addTask( "client1", ClientTask, conf="client/client.conf" )
#conf.addTask( "client2", ClientTask, conf="client/client.conf" )
#conf.addTask( "client3", ClientTask, conf="client/client.conf" )
#conf.addTask( "stateclient", StateTask )
conf.addTask( "dmodel", DomainModelTask, conf="dmodel/dmodel.conf" )
conf.addTask( "opc", OPCTask )
conf.addTask( "gui", GUITask )
conf.addTask( "security", SecurityTask )
conf.addTask( "alarm", AlarmTask )

