import ipaddress
class Route:
	#route constructor, takes in dest_ip and a path(list of ip hops)
	def __init__(self, dest_ip, ip_path):
		self.dest = dest_ip
		self.path = ip_path #lsit expected will error in next line if anything else
		self.cost = len(ip_path) #option to set cost based on latency or throughput later


	def __repr__(self):
		return "dest: " + str(self.dest) + " path: " + str(self.path) + " cost: " + str(self.cost) + "--"

#returns ip of the next hop in the route
	def nextHop(self):

#returns dest of Route
	def getDest(self):

#returns cost of Route
	def getCost(self):

#removes 0th element and returns it
	def popHop(self):


#add hop to the front of a route and return new route i.e. take a route given
#by a neighbor and create a route out of it with the neighbor at the front then the rest of the route
#is called by the routeFromNeighbor() function of RoutingTable
	def newRoute(self, hop):

class RoutingTable:
	def __init__(self, own_ip):
		self.my_ip = own_ip
		self.allNodes = [own_ip] #List of all seen nodes in the network (connected or disconnected)
		self.neighbors = [] # list of all neighbors
		self.route_table = {} # the dict of routes, key = ip, value = Route

	def __str__(self):
		r = "ip: " + str(self.my_ip) + "\n"
		r+= "allNodes: " + str(self.allNodes) + "\n"
		r+= "neighbors: " + str(self.neighbors) + "\n"
		r+= "route_table: " + str(self.route_table)
		return r


#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
	def addRoute(self, newRoute):

#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
#adds node to allnodes list, adds it to neighbors, creates new route and adds it to routetable
	def addNeighbor(self, new_ip):

#returns list of available destinations
	def getAvailableDestinations(self):

#returns boolean as to if the desired dest is present
	def hasDestination(self, ip_dest):

#when a route is provided by a neighbor:
#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
	def routeFromNeighbor(self, nei_ip, nei_route):

#drops connection to neighbor
#drops all connections through that neighbor
#returns dictionary of dropped connections
	def dropNeighbor(self, nei_ip):

#after receiving alert that someone lost a connection
#drops all routes which include this connection
	def brokenConnection(ip1, ip2):
