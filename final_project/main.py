import ipaddress
import threading
from communication_message import CommunicationMessage, loadCommunicationMessageFromJSON
from communication_server import CommunicationServer
from dc2 import Route, RoutingTable
from routing_server import RouteDto, RoutingServer, loadRouteDtoArrFromJSON, routineTableToJson
import json
import time
from GUI_App import GUI_App
from datetime import datetime
import re
import sys

COMMAND_LINE_ONLY = False
if(len(sys.argv) > 1 and sys.argv[1] == "c"):
    COMMAND_LINE_ONLY = True

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
                self.print_message('Error dispatching routes')


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
        message_string = ""
        if not group_identifier is None and group_identifier in self.groups:
            message_string = "Group " + message_string + "\nGroup: " + group_identifier
        elif group_identifier is None:
            message_string += "\nFrom: "  + str(client[0])
            message_string += "\nMessage: " + str(message)
            message_string += '\nPath: ' + str(path)
        self.print_message(message_string)
    #callback method for when routes are received from other nodes
    def onRoutesReceived(self, data, client):
        if client[0] in dropped_neighbors:
            return
        self.routing_table.addNeighbor(ipaddress.ip_address(client[0])) # probably should check if the routing table has this neighbor first before adding
        routeArr = loadRouteDtoArrFromJSON(data)
        neighbor_routing_table = RoutingTable(client[0])
        for route in routeArr:
            r = Route(ipaddress.ip_address(route.destination_ip), route.path)
            neighbor_routing_table.addRoute(r)
            self.routing_table.routingTableComparison(neighbor_routing_table)

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
                self.print_message('Path getting too large')
                return
            
            if self.own_ip in messageObj.getPath():
                self.print_message('Circular reference. Aborting')
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
                self.print_message('Destination unavailble')
        except Exception as e:
            self.print_message('Error sending:',e)

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
                self.print_message(routeJson)
    def print_message(*args):
        global gui
        datetime_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Ignore first param, first param is self
        message_string = " ".join(str(v) for v in args[1:])
        message_string = "{0} - {1}".format(datetime_string, message_string)

        if COMMAND_LINE_ONLY :
            print(message_string)
        else:
            gui.append_output(message_string)

def gui_send_message(*args):
    global gui, main
    
    id_addr = gui.ip_entry_var.get()
    message = gui.message_entry.get("1.0", "end-1c")

    if(re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', id_addr) == None):
        main.print_message("Invalid IP Address")
    elif(message == ""):
        main.print_message("Message cannot be blank")
    else:
        main.print_message("Sending Message\nTo: {0}\nMessage: {1}".format(id_addr, message))
        main.newMessage(message, id_addr)

    

main = Main()
gui = None

if COMMAND_LINE_ONLY :
    main.start()
else:
    gui = GUI_App()
    gui.send_button.configure(command=gui_send_message)
    gui.mainloop()
