import ipaddress
import threading
from communication_message import CommunicationMessage, loadCommunicationMessageFromJSON
from communication_server import CommunicationServer
from dc2 import Route, RoutingTable
from routing_server import RouteDto, RoutingServer, loadRouteDtoArrFromJSON, routineTableToJson
import json
import time

CONFIG_FILE = 'init.json'
ROUTING_PORT_KEY = 'routing_port'
COMMUNICATION_PORT_KEY = 'communication_port'
OWN_IP_KEY = 'own_ip'
DISPATCH_ROUTES_SECONDS = 5
dropped_neighbors = []

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

        self.groups = []

    # load the initial routes from the self.config config loaded TODO
    def loadInitialRoutes(self):
        for neighbor in self.config['neighbors']: 
            self.routing_table.addNeighbor(ipaddress.ip_address(neighbor))

    def dispatchRoutes(self):
        while(True):
            time.sleep(DISPATCH_ROUTES_SECONDS)
            try:
                routeJson = routineTableToJson(self.routing_table.route_table.items(), self.own_ip)
                neighbors = self.routing_table.neighbors
                for neighbor in neighbors:
                    self.route_server.sendRoutes(str(neighbor), self.routing_port, routeJson)
            except:
                print('\nError dispatching routes\n')


    def startDispatchRoutes(self):
        dispatch_thread = threading.Thread(target=self.dispatchRoutes)
        dispatch_thread.start()

    #loads the file-based config
    def loadConfig(self):
        config_file = open(CONFIG_FILE)
        config = json.load(config_file)
        return config

    # Choose to do with a message that was meant for self as destination node
    def consumeMessage(self, message, path, client, group_identifier = None):
        if not group_identifier is None and group_identifier in self.groups:
            print('\n\n','GROUP: ',group_identifier, '\n')
            print(message, '\n', 'Path: ', path, '\n\n')
        elif group_identifier is None:
            print('\n','FROM: ',client[0],': ', message, '\n', 'Path: ', path, '\n\n')

    #callback method for when routes are received from other nodes
    def onRoutesReceived(self, data, client):
        if client[0] in dropped_neighbors:
            return
        self.routing_table.addNeighbor(ipaddress.ip_address(client[0])) # probably should check if the routing table has this neighbor first before adding
        routeArr = loadRouteDtoArrFromJSON(data)
        for route in routeArr:
            r = Route(ipaddress.ip_address(route.destination_ip), [ipaddress.ip_address(client[0])] + route.path)
            self.routing_table.routeFromNeighbor(ipaddress.ip_address(client[0]), r)

        #if dropped node type, call drop_neighbor, else update routes. 

    def onCommunicationReceived(self, data, client):
        messageObj = loadCommunicationMessageFromJSON(data)
        if not messageObj.dropdest is None:
            self.routing_table.brokenConnection(messageObj.dropsource, messageObj.dropdest)
            return
        if messageObj.destination_ip == self.own_ip:
            self.consumeMessage(messageObj.getMessage(), messageObj.getPath(), client, messageObj.getGroupIdentifier())
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
    
    def newGroupMessage(self, message, group_identifier):
        all_destinations = self.routing_table.route_table.keys()
        for destination in all_destinations:
            packet = CommunicationMessage(message, str(destination), [self.own_ip], group_identifier)
            self.sendMessage(packet,str(destination))

    def dropNeighbor(self, droppedIP):
        self.routing_table.dropNeighbor(ipaddress.ip_address(droppedIP))
        all_destinations = self.routing_table.route_table.keys()
        for destination in all_destinations:
            packet = CommunicationMessage(None, str(destination), [self.own_ip], None, self.own_ip, droppedIP)
            self.sendMessage(packet,str(destination))
    
    def sendMessage(self, messageObj:CommunicationMessage, ip):
        try:
            if(self.routing_table.hasDestination(ipaddress.ip_address(ip))):
                route = self.routing_table.getRouteByDestinationIp(ipaddress.ip_address(ip))
                self.communication_server.sendMessage(str(route.nextHop()), self.communication_port, messageObj.toJSON())
            else:
                print('\n Destination unavailble \n')
        except Exception as e:
            print('\nError sending:',e,'\n')

    def joinGroup(self, group_identifier):
        if not group_identifier is None and not group_identifier in self.groups:
            self.groups.append(group_identifier)

    def leaveGroup(self, group_identifier):
        if not group_identifier is None and group_identifier in self.groups:
            self.groups.remove(group_identifier)
    #starts a command loop from terminal input.
    # 1) Send message to another IP      sendto:192.168.0.10:this is my message
    # 2) Drop neighbor                   drop:192.168.0.5
    # 3) Add neighbor                    add:192.168.0.5
    def start(self):
        while(True):
            destination_ip = None
            message = None
            c = input("")
            if c == "send":
                destination_ip = input("Enter destination: ")
                message = input("Enter message: ")
                self.newMessage(message, destination_ip)
            if c == "sendgroup":
                group_identifier = input("Enter group to send to: ")
                message = input("Enter message: ")
                self.newGroupMessage(message, group_identifier)
            elif c == "dropneighbor":
                ip = input("Enter dropped neighbor")
                dropped_neighbors.append(ip)
                self.dropNeighbor(ip)
            elif c == "restoreneighbor":
                ip = input("Enter restored neighbor")
                dropped_neighbors.remove(ip)
            elif c == "joingroup":
                group = input("What group would you like to join?: ")
                self.joinGroup(group)
            elif c == "leavegroup":
                group = input("What group would you like to leave?: ")
                self.leaveGroup(group)
            elif c == "printroutes":
                routeJson = routineTableToJson(self.routing_table.route_table.items(), self.own_ip)
                print('\n\n\n',routeJson,'\n\n\n')



main = Main()
main.start()