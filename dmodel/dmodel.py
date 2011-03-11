from pyworks import Task, Node

import re

class DomainState :
    def color( self ):
        return 'black'

class UnknownState( DomainState ):
    def color( self ):
        return 'black'

class ReadyState( DomainState ):
    def color( self ):
        return 'blue'

class RunningState( DomainState ) :
    def color( self ):
        return 'green'

class WarningState( RunningState ):
    def color( self ):
        return 'yellow'

class AlarmState( DomainState ):
    def color( self ):
        return 'red'


class DomainNode( Node ) :
    def __init__( self, nid, val=0, dtype='DomainNode', tag=None ):
        Node.__init__( self, nid, val )
        self.dtype = dtype
        self.state = self

    def __str__( self ):
        if self.val :
            return "%s: %s=%s" % ( self.dtype, self.getName(), self.val )
        return "%s: %s" % ( self.dtype, self.getName())

    def setState( self, state ):
        self.state = state

    def execute( self, command ):
        print "executing: %s.%s" % ( self.getName(), command )

    def setAlarm( self, nodeid, alarm ):
        self.parent.setAlarm( nodeid, alarm )

    def dump( self ):
        print "%*.*s%s" % ( self.level( ) * 4, self.level( ) * 4, " ", self )
        for node in self.nodes.values( ) :
            node.dump( )

class RootDomainNode( DomainNode ):
    def __init__( self, model, name ):
        DomainNode.__init__( self, name, dtype="RootDomainNode" )
        self.model = model
        self.observers = []

    def setAlarm( self, nodeid, alarm ):
        self.model.setAlarm( nodeid, alarm )

    def addObserver( self, observer ):
        self.observers.append( observer )

    def notify( self, node ):
        for observer in self.observers :
            observer.update( node )
    


class ExcelReader :
    def __init__( self, path ):
        self.path = path
        self.ex = Excel.ApplicationClass()   
        # self.ex.Visible = True
        self.ex.DisplayAlerts = False   
        self.wb = self.ex.Workbooks.Open(self.path)
        self.ws = self.wb.Worksheets[1]

    def read( self ):
        print "NOT IMPLEMENTED"

    def close( self ):
        self.wb.Close()
        self.ex.Quit( )
        self.wb = None
        self.ex = None
        GC.Collect( )

class ParameterListReader( ExcelReader ):
    def read( self, dm ):
        dtype = 'Domain'
        for i in range( 1, 1000 ):
            key = self.ws.Rows[i].Value2[0,0]
            if key == None :
                continue
            val = self.ws.Rows[i].Value2[0,1]
            key = '-'.join( key.split( ' ' ))
            key = key.lower( )
            dm.addNode( '.'.join( key.split( '_' )), val, dtype )


class IOListReader( ExcelReader ):
    def read( self, dm ):
        prefix = []
        levels = {}
        debth = 0
        skipping = True
        for i in range( 1, 1000 ):
            key = self.ws.Rows[i].Value2[0,1]
            if key == None :
                key = self.ws.Rows[i].Value2[0,2]
                if key == None :
                    continue
            if key[:2] == '(*' :
                skipping = False
                r = re.match( '\(\*([0-9.]+)\s+(.*)\*\)', key )
                if r :
                    h = r.group( 1 ) # Hub, Nacelle, etc
                    n = r.group( 2 ) # 1 2 2.1 2.2 etc
                    if h == "end" :
                        return
                    levels[h] = n
                    n = ""
                    prefix = []
                    for level in h.split( '.' ):
                        n = n + level
                        prefix.append( levels[ n ])
                        n = n + '.'
                continue
            if skipping :
                continue
            dtype = "Domain"
            if key[:3] == 'DI_' :
                key = key[3:]
                dtype = "DInput"
            if key[:3] == 'AI_' :
                key = key[3:]
                dtype = "AInput"
            if key[:3] == 'DQ_' :
                key = key[3:]
                dtype = "DOutput"
            if key[:3] == 'AQ_' :
                key = key[3:]
                dtype = "AOutput"
            if re.search( 'windspeed', key, re.I ):
                dtype = "WindSpeedInput"
            if key == "TempNacelle" :
                dtype = "TempNacelle"
            val = 0
            name = '.'.join( prefix ) + '.' + key
            name = '-'.join( name.split( ' ' ))
            name = name.lower( )
            dm.addNode( name, val, dtype )


class WindPark( DomainNode ):
    pass


class WTG( DomainNode ):
    def doStop( self ):
        if self.running :
            self.running = False
            self.notify( self )

    def doStart( self ):
        if not self.running :
            self.running = True
            self.notify( self )

    def isRunning( self ):
        return self.running

class WindSpeedInputNode( DomainNode ):
    def setValue( self, val ):
        if abs( self.val - val ) > 5 :
            self.val = val
            self.notify( self )

class VROT( DomainNode ):
    pass

class DInputNode( DomainNode ):
    def getState( self ):
        return self.state

class DOutputNode( DomainNode ):
    def setState( self, state ):
        self.state = state

    def getState( self ):
        return self.state

class AInputNode( DomainNode ):
    def getValue( self ):
        return self.value

class AOutputNode( DomainNode ):
    def setValue( self, value ):
        self.value = value

class TempNacelleNode( DomainNode ):
    def setValue( self, value ):
        if value > 60 :
            self.setAlarm( self.getName( ), "Temp to HOT" )
        if value > 55 :
            self.setAlarm( self.getName( ), "Nacelle getting warm" )


class Command :
    def execute( self, node ):
        pass

class StopCommand( Command ):
    def execute( self, node ):
        node.doStop( )

class StartCommand( Command ):
    def execute( self, node ):
        node.doStart( )

commands = {
    "stop" : StopCommand,
    "start" : StartCommand
}


class DomainModel:
    def __init__( self, task ):
        self.model = RootDomainNode( self, "wtg" )
        self.task = task

    def addObserver( self, observer ):
        self.model.addObserver( observer )

    def addNode( self, name, val, dtype ):
        # print '%s( %s, %s)' % ( dtype, name, val )
        node = self.model
        for n in name.split( '.' ):
            if not node.hasKey( n ):
                node.addNode( eval( '%sNode( n, dtype="%s" )' % ( dtype, dtype )))
            node = node.getNode( n )
        node.val = val

    def setValue( self, name, val ):
        node = self.model.find( name )
        node.setValue( val )

    def setAlarm( self, nodeid, alarm ):
        self.task.setAlarm( nodeid, alarm )

    def dump( self ):
        self.model.dump( )


class DomainModelService :
    def executeCommand( self, node, command ):
        pass

    def findNode( self ):
        """
        We need some way to read a current value. 
        Fx. when the GUI starts up, we need to return current windspeed
        """
        pass

class DomainModelOutput :
    def updateNode( self ):
        pass

class DomainModelTask( Task ):
    def init( self ):
        self._dm = DomainModel( self )

    def conf( self ):
        self._dm.addObserver( self )

    def dump( self ):
        self._dm.dump( )

    def getValue( self, node ):
        print "value of %s" % node
        return 42

    def setValue( self, node, val ):
        self._dm.setValue( node, val )

    def setAlarm( self, nodeid, text ):
        print "alalrm %s %s" % ( nodeid, text )
        self.dispatch( ).setAlarm( nodeid, text )

    def update( self, node ):
        self.dispatch( ).nodeUpdate( node.getName( ), node.val )

    def handleCommand( self, subject, nodeid, command ):
        subject.checkPermission( command )
        node = self._dm.model.find( nodeid )
        print "found %s for %s" % ( node.name, nodeid )
        cmd = commands[ command ]( )
        node.state.execute( cmd )

    def addListener( self, domainModelOutputListener ):
        pass




