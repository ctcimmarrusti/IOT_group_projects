import ipaddress
from communication_message import CommunicationMessage, loadCommunicationMessageFromJSON
from communication_server import CommunicationServer
from dc2 import Route, RoutingTable
from routing_server import RoutingServer
import json
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

    # load the initial routes from the self.config config loaded TODO
    def loadInitialRoutes(self):
        for neighbor in self.config['initial_routes']:
            for route in neighbor['routes']:
                path = list(map(lambda p: ipaddress.ip_address(p), route['path']))
                r = Route(ipaddress.ip_address(route['destination_ip']), path)
                self.routing_table.routeFromNeighbor(ipaddress.ip_address(neighbor['neighbor_ip']), r)

    #loads the file-based config
    def loadConfig(self):
        config_file = open(CONFIG_FILE)
        config = json.load(config_file)
        return config

    #callback method for when routes are received from other nodes
    def onRoutesReceived(self, data):
        print('---')
        #TODO process routes into self.routing_table
        print(data)
        print('---')

    def onCommunicationReceived(self, data):
        messageObj = loadCommunicationMessageFromJSON(data)
        messageObj.destination_ip
        
        print('---')
        # data is json of type CommunicationMessage
        #TODO process message. Either consume the message if destination is own_ip or forward to destination_ip of message
        print(data)
        print('---')
    
    # Sends a message to another node by IP
    # First lookup IP via routing table and get next hop
    # Create CommunicationMessage obj and send serialized object
    def sendMessage(self, message, ip):
        route = self.routing_table.getRouteByDestinationIp(ipaddress.ip_address(ip))
        packet = CommunicationMessage(message, ip, [self.own_ip])
        self.communication_server.sendMessage(str(route.nextHop()), self.communication_port, packet.toJSON())

    #starts a command loop from terminal input. TODO parse input to either
    # 1) Send message to another IP
    # 2) Drop neighbor
    # 3) Add neighbor
    def start(self):
        while(True):
            command = input("Please enter command: ")
            print(command)
            #self.route_server.sendRoutes('0.0.0.0', 8090, "testtest")
            self.sendMessage('test message','0.0.0.0')



main = Main()
main.start()