from pyworks.taskmanager import Module, Manager
from gui.task import WorkApp

from logger.task import LoggerTask

sys_tasks = { "logger" : Module( "logger", None, LoggerTask ) }

class Tasks :
    def __init__( self ):
        self.list = {}

    def addTask( self, name, factory, conf=None ):
        self.list[ name ] = Module( name, conf, factory )
        
def user_tasks( manager, conffile ):
    c = Tasks( )
    execfile( conffile, { 'conf' : c } )
    return c.list

if __name__ == "__main__" :
    m = Manager( )
    m.loadModules( sys_tasks )
    m.loadModules( user_tasks( m, 'usertasks.py' ) )
    m.initModules( )
    m.confModules( )
    m.runModules( )

    app = WorkApp( m )
    app.MainLoop()
    
    print "DONE GUI"
    
    m.shutdown( )
    
    # wait for all to close
    for name, module in m.modules.items( ) :
        module.runner.join( )
    
    
