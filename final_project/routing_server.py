import json
import socket
import socketserver
import threading


from socket_handler import handler_factory

class RoutingServer:
    def __init__(self, host_ip, host_port, onMessage):
        self.host_ip = host_ip
        self.host_port = host_port 
        self.onMessage = onMessage
    
    def sendRoutes(self, ip, port, routes):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:  
            sock.sendto(bytes(routes + "\n", "utf-8"), (ip, port))

    # Starts a UDP server that doesnt quit until the main program quits
    def start_server(self):
        with socketserver.UDPServer((self.host_ip, self.host_port), handler_factory(self.onMessage)) as server:
            server.serve_forever()

    # Start the server on a separate thread        
    def start(self):
        thread = threading.Thread(target=self.start_server)
        thread.start()
        return thread

class RouteDto:
    def __init__(self, destination_ip, path):    
        self.destination_ip = str(destination_ip)
        self.path = list(map(lambda p: str(p), path))

# When a message is received, can create an object from the json
def loadRouteDtoArrFromJSON(jsonStr):
    retArr = []
    routeDtoArr = json.loads(jsonStr)
    for route in routeDtoArr:
        retArr.append(RouteDto(**route))
    return retArr   

def routineTableToJson(routing_table, own_ip):
    routes = []
    for route in routing_table:
        if route[1].dest != own_ip:
            routes.append(RouteDto(route[1].dest, route[1].path))
    routeJson = json.dumps(routes, default=lambda o: o.__dict__, sort_keys=True)
    return routeJson