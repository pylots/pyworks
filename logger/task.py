from pyworks import Task

class LoggerTask( Task ):
    def log( self, task, level, msg ):
        print "[%s] %s" % ( task.name, msg )
        
