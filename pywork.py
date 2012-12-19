import sys, os

from pyworks.taskmanager import Module, Manager

from logger.logger import LoggerTask

sys_tasks = { "logger" : Module( "logger", "./logger/logger.conf", LoggerTask ) }

class Tasks :
    def __init__( self ):
        self.list = {}

    def addTask( self, name, factory, conf=None, index=None ):
        self.list[ name ] = Module( name, conf, factory )
        if index : # Overwriting default index/pid
            self.list[ name ].index = index 

def user_tasks( manager, conffile ):
    c = Tasks( )
    execfile( conffile, { 'conf' : c } )
    return c.list

if __name__ == "__main__" :
    m = Manager( )
    m.loadModules( sys_tasks )
    m.loadModules( user_tasks( m, 'conf/usertasks.py' ) )
    m.initModules( )
    m.confModules( )
    m.runModules( )

    for module in m.get_modules( ):
        exec( "%s=module.proxy" % ( module.name ))

    prompt = ">>"
    running = True
    while running :
        try:
            line = raw_input( prompt )
        except KeyboardInterrupt :
            os._exit( 0 )            
        if len( line ) == 0 :
            prompt = ".."
        if line == "exit" :
            running = False
            continue
        if line == "dump" :
            m.dumpModules( )
            continue
        try:
            exec( line )
            prompt = ">>"
        except:
            print "%s" % sys.exc_info( )[1]
            prompt = "?>>"

    m.closeModules( )
    m.shutdown( )
    
    # wait for all to close
    for name, module in m.modules.items( ) :
        module.runner.join( )
    
    
