import threading
import os

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound


def start(port, root, key):
    def static_file(request):
        path = os.path.join(root, request.matchdict["name"])
        
        if request.method == "GET":
            # TODO: use isfile
            if os.path.exists(path):
                with open(path) as f:
                    return Response(f.read())
            else:
                return HTTPNotFound()
                
        if request.method == "PUT":
            if request.GET.get("key") == key:
                if not os.path.exists(path):
                    with open(path, "w") as f:
                        f.write(request.body)
                return Response("OK")
            else:
                return Response("Bad key", status=403)
        
    
    config = Configurator()
    config.add_route('static_file', '/{name}')
    config.add_view(static_file, route_name='static_file')
    app = config.make_wsgi_app()
    
    server = make_server('0.0.0.0', port, app)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    
    return Server(server, server_thread)

class Server(object):
    def __init__(self, server, thread):
        self._server = server
        self._thread = thread
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self._server.shutdown()
        self._thread.join()
