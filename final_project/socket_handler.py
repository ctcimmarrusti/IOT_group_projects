import socketserver

class UDPHandler(socketserver.BaseRequestHandler):
    def __init__(self, callback, *args, **keys):
        self.callback = callback
        socketserver.BaseRequestHandler.__init__(self, *args, **keys)

    def handle(self):
        data = self.request[0].strip()
        self.callback(data)

def handler_factory(callback):
    def createHandler(*args, **keys):
        return UDPHandler(callback, *args, **keys)
    return createHandler