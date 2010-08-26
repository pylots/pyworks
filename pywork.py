import sys

from pyworks.taskmanager import Module, Manager

from logger.task import LoggerTask

sys_tasks = { "logger" : Module( "logger", "./logger/logger.conf", LoggerTask ) }

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

    for module in m.get_modules( ):
        exec( "%s=module.proxy" % ( module.name ))

    prompt = ">>"
    running = True
    while running :
        line = raw_input( prompt )
        if len( line ) == 0 :
            prompt = ".."
        if line == "exit" :
            running = False
            continue
        try:
            exec( line )
            prompt = ">>"
        except:
            print "%s" % sys.exc_info( )[1]
            prompt = "?>>"

    m.shutdown( )
    
    # wait for all to close
    for name, module in m.modules.items( ) :
        module.runner.join( )
    
    
