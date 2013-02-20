import threading
import os
import mimetypes
import errno

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound


def start(port, root, key):
    def static_file(request):
        default_file_type = (None, None)
        web_path = request.matchdict["name"]
        physical_path = os.path.join(root, web_path)
        
        if request.method == "GET":
            return get_file(physical_path, web_path)
                
        if request.method == "PUT":
            return put_file(request, physical_path, web_path)
    
    
    def get_file(physical_path, web_path):
        if os.path.isfile(physical_path):
            content_type, encoding = mimetypes.guess_type(web_path) or default_file_type
            with open(physical_path) as f:
                return Response(f.read(), content_type=content_type)
        else:
            return HTTPNotFound()
            
            
    def put_file(request, physical_path, web_path):
        if request.GET.get("key") == key:
            if os.path.basename(physical_path) == "":
                return Response("Cannot overwrite directory", status=403)
            else:
                if not os.path.exists(physical_path):
                    # TODO: locking
                    _mkdir_p(os.path.dirname(physical_path))
                    with open(physical_path, "w") as f:
                        f.write(request.body)
                return Response("OK")
        else:
            return Response("Bad key", status=403)
        
    
    config = Configurator()
    config.add_route('static_file', '/{name:.*}')
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


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as error:
        if not (error.errno == errno.EEXIST and os.path.isdir(path)):
            raise
