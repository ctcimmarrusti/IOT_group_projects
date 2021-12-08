import ipaddress
import threading
from communication_message import CommunicationMessage, loadCommunicationMessageFromJSON
from communication_server import CommunicationServer
from dc2 import Route, RoutingTable
from routing_server import RouteDto, RoutingServer, loadRouteDtoArrFromJSON
import json
import time

CONFIG_FILE = 'init.json'
ROUTING_PORT_KEY = 'routing_port'
COMMUNICATION_PORT_KEY = 'communication_port'
OWN_IP_KEY = 'own_ip'

# Main logic and control script
class Main:
    #loads initial config from the json file and initializes the initial routing table, own ip, ports and starts routing and communications server
    def __init__(self):
        self.config = self.loadConfig()
        self.own_ip = self.config[OWN_IP_KEY]
        self.routing_port = self.config[ROUTING_PORT_KEY]
        self.communication_port = self.config[COMMUNICATION_PORT_KEY]

        self.routing_table = RoutingTable(self.own_ip)
        self.loadInitialRoutes()

        self.route_server = RoutingServer(self.own_ip, self.routing_port, self.onRoutesReceived)
        self.communication_server = CommunicationServer(self.own_ip, self.communication_port, self.onCommunicationReceived)

        self.route_server.start()
        self.communication_server.start()
        self.startDispatchRoutes()

    # load the initial routes from the self.config config loaded TODO
    def loadInitialRoutes(self):
        for neighbor in self.config['neighbors']: 
            self.routing_table.addNeighbor(ipaddress.ip_address(neighbor))

    def dispatchRoutes(self):
        while(True):
            time.sleep(5)
            routes = []
            for route in self.routing_table.route_table.items():
                if route[1].dest != self.own_ip:
                    routes.append(RouteDto(route[1].dest, route[1].path))
            routeJson = json.dumps(routes, default=lambda o: o.__dict__, sort_keys=True)
            neighbors = self.routing_table.neighbors
            for neighbor in neighbors:
                self.route_server.sendRoutes(str(neighbor), self.routing_port, routeJson)

    def startDispatchRoutes(self):
        dispatch_thread = threading.Thread(target=self.dispatchRoutes)
        dispatch_thread.start()

    #loads the file-based config
    def loadConfig(self):
        config_file = open(CONFIG_FILE)
        config = json.load(config_file)
        return config

    # Choose to do with a message that was meant for self as destination node
    def consumeMessage(self, message, client):
        print('FROM: ',client[0],': ', message, '\n') 

    #callback method for when routes are received from other nodes
    def onRoutesReceived(self, data, client):
        self.routing_table.addNeighbor(ipaddress.ip_address(client[0])) # probably should check if the routing table has this neighbor first before adding
        routeArr = loadRouteDtoArrFromJSON(data)
        for route in routeArr:
            r = Route(ipaddress.ip_address(route.destination_ip), [ipaddress.ip_address(client[0])] + route.path)
            self.routing_table.routeFromNeighbor(ipaddress.ip_address(client[0]), r)

    def onCommunicationReceived(self, data, client):
        messageObj = loadCommunicationMessageFromJSON(data)
        if messageObj.destination_ip == self.own_ip:
            self.consumeMessage(messageObj.getMessage(), client)
        else:
            if len(messageObj.getPath()) > 4:
                print('\n Path getting too large\n')
                return
            
            if self.own_ip in messageObj.getPath():
                print('\n Circular reference. Aborting')
                return

            messageObj.appendToPath(self.own_ip)
            self.sendMessage(messageObj, messageObj.destination_ip)
               
    # Sends a message to another node by IP
    # First lookup IP via routing table and get next hop
    # Create CommunicationMessage obj and send serialized object
    def newMessage(self, message, ip):
        packet = CommunicationMessage(message, ip, [self.own_ip])
        self.sendMessage(packet,ip)
    
    def sendMessage(self, messageObj:CommunicationMessage, ip):
        if(self.routing_table.hasDestination(ipaddress.ip_address(ip))):
            route = self.routing_table.getRouteByDestinationIp(ipaddress.ip_address(ip))
            self.communication_server.sendMessage(str(route.nextHop()), self.communication_port, messageObj.toJSON())
        else:
            print('\n Destination unavailble \n')

    #starts a command loop from terminal input.
    # 1) Send message to another IP      sendto:192.168.0.10:this is my message
    # 2) Drop neighbor                   drop:192.168.0.5
    # 3) Add neighbor                    add:192.168.0.5
    def start(self):
        while(True):
            c = input("Please enter command: ")
            cArr = c.split(":")
            command = cArr[0]
            if command == "sendto":
                if len(cArr) != 3:
                    continue
                self.newMessage(cArr[2], cArr[1])
            elif command == "drop":
                pass
            elif command == "add":
                pass

main = Main()
main.start()