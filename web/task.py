from pyworks import Task
from web.coworks import app, init_db
from wsgiref.simple_server import make_server


class WebTask( Task ):
    def init( self ):
        init_db( )

    def start( self ):
        app.config.update(dict(
                COWORKS=self._manager
                ))
        httpd = make_server('localhost', 5000, app)
        httpd.serve_forever( )
