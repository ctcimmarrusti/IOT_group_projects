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
		if len(self.path) < 2: # if you are at ultimate or penultimate location return dest.
			return self.dest
		else:
			return self.path[0]

#returns dest of Route
	def getDest(self):
		return self.dest

#returns cost of Route
	def getCost(self):
		return self.cost

#removes 0th element and returns it
	def popHop(self):
		returnee = self.path.pop(0)
		self.cost = len(self.ip_path)
		return returnee

#add hop to the front of a route and return new route i.e. take a route given by a neighbor and create a route out of it
#is called by the routeFromNeighbor() function of RoutingTable
	def newRoute(self, hop):
		returnee = Route(self.dest, self.path)
		returnee.path.insert(0, hop)
		returnee.cost = len(returnee.path)
		return returnee

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
		new_ip = newRoute.dest
		if(newRoute.getDest() in self.route_table.keys()):
			if newRoute.getCost() < self.route_table[new_ip].getCost(): #if new cost is less than current pathway cost, replace pathway
				self.route_table.update({new_ip: newRoute}) #this allows only one path to any IP
				return 1
			else:
				return -1
		else:
			self.route_table[new_ip] = newRoute
			self.allNodes.append(new_ip)
			return 0

#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
#adds node to allnodes list, adds it to neighbors, creates new route and adds it to routetable
	def addNeighbor(self, new_ip):
		if not (new_ip in self.neighbors):
			self.neighbors.append(new_ip) #track new neighbor
		newR = Route(new_ip, [new_ip]) #create route to new neighbor
		return self.addRoute(newR)


#returns list of available destinations
	def getAvailableDestinations(self):
		returnee = []
		for k in self.route_table:
			returnee.append(k)
		return returnee

	def hasDestination(self, ip_dest):
		return ip_dest in self.route_table

#when a route is provided by a neighbor:
#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
	def routeFromNeighbor(self, nei_ip, nei_route):
		nei_route.newRoute(nei_ip)
		return self.addRoute(nei_route)

#drops connection to neighbor
#drops all connections through that neighbor
#returns dictionary of dropped connections
	def dropNeighbor(self, nei_ip):
		droppees = {}
		if(nei_ip in self.neighbors):
			self.neighbors.remove(nei_ip)
		if(nei_ip in self.allNodes):
			self.allNodes.remove(nei_ip)
		for k, v in self.route_table.items(): #for each route
			for ip in v.path: #for each ip stop in the route
				if ip == nei_ip: #if the neighbor being dropped is in the route
					droppees.update({k:v})
					break
		for k in droppees: #must wait till end of loop to drop in order to avoid iterator error
			del self.route_table[k]
		return droppees

#after receiving alert that someone lost a connection
#drops all routes which include this connection
	def brokenConnection(self, ip1, ip2):
		droppees = {}
		for k, v in self.route_table.items(): #for each route
			last_ip = False
			for ip in v.path:
				if not last_ip: #if first element in list continue
					last_ip = ip
					continue
				if (ip1 == last_ip and ip2 == ip) or (ip1 == ip and ip2 ==last_ip):#if the path contains this connection
					droppees[k] = v
					break
				last_ip = ip
		for k in droppees: #must wait till end of loop to drop in order to avoid iterator error
			self.dropRouteToDest(k)
		return droppees

	def hasDest(self, d):
		return d in self.route_table

#drops route and removes the node from all Nodes
	def dropRouteToDest(self, d):
		del self.route_table[d]
		self.allNodes.remove(d)

#get the route in the hashed route table by the ultimate destination
	def getRouteByDestinationIp(self, dest):
		return self.route_table[dest]

#compare to see if neighbor has lost routes I route through him --drop those route
#attempt to add all of neighbors routes, if any are new or superior they will be added
	def routingTableComparison(self, rt2):
		droppees = []
		myip = self.my_ip
		rt2ip = rt2.my_ip
		print("my IP: " + str(myip))
		print("rt2IP: " + str(rt2ip))
		for k, v in self.route_table.items():
			if(v.path[0] == rt2ip):
				if not rt2.hasDest(k):
					droppees.append(k)
		self.dropRouteToDest(k)
		for v in rt2.route_table.values():
			print("---------------------------------------")
			print(v)
			if v.dest == myip:
				print("found me")
				continue
			self.routeFromNeighbor(rt2ip, v)




# a = Route(ipaddress.ip_address('192.168.0.4'),[ipaddress.ip_address('192.168.0.3'),ipaddress.ip_address('192.168.0.2'),ipaddress.ip_address('192.168.0.1')])
# # print(a)
# # print("-")
# n = RoutingTable(ipaddress.ip_address('192.168.0.1'))
# # print(n)
# # print("-")
# n.addNeighbor(ipaddress.ip_address('192.168.0.2'))
# n.addNeighbor(ipaddress.ip_address('192.168.0.5'))
# r2 = Route(ipaddress.ip_address('192.168.0.4'), [ipaddress.ip_address('192.168.0.3'),ipaddress.ip_address('192.168.0.4')])
# n.routeFromNeighbor(ipaddress.ip_address('192.168.0.2'), r2)
# # print("------------add route from neighbor: 2,3,4")
# # print(n)
# t2 = RoutingTable(ipaddress.ip_address('192.168.0.5'))
# t2.addNeighbor(ipaddress.ip_address('192.168.0.1'))
# t2.addNeighbor(ipaddress.ip_address('192.168.0.17'))
# print("-------t2---------")
# print(t2)
# r3 = Route(ipaddress.ip_address('192.168.0.7'), [ipaddress.ip_address('192.168.0.7')])
# n.routeFromNeighbor(ipaddress.ip_address('192.168.0.5'), r3)
# print("------------Add route: 5, 7")
# print(n)
# print("------------routing table comparison")
#
# # n.brokenConnection(ipaddress.ip_address('192.168.0.3'),ipaddress.ip_address('192.168.0.4'))
# n.routingTableComparison(t2)
# print(n)
