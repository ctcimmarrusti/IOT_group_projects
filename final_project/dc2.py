import ipaddress

class Route:
	def __init__(self, dest_ip, ip_path):
		self.dest = dest_ip
		self.path = ip_path #lsit expected will error in next line if anything else
		self.cost = len(ip_path) #option to set cost based on latency or throughput later

	def __repr__(self):
		return "dest: " + str(self.dest) + " path: " + str(self.path) + " cost: " + str(self.cost) + "--" 

class RoutingTable:
	def __init__(self, own_ip):
		self.my_ip = own_ip
		self.allNodes = [own_ip] #List of all seen nodes in the network
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
		if(newRoute.dest in self.route_table.keys()):
			if n.cost < self.route_table[new_ip].cost: #if new cost is less than current pathway cost, replace pathway
				self.route_table.update({new_ip: n}) #this allows only one path to any IP
				return 1
			else:
				return -1
		else:
			self.route_table[new_ip] = newRoute
			return 0

#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
#adds node to allnodes list, adds it to neighbors, creates new route and adds it to routetable
	def NewNeighbor(self, new_ip):
		if not (new_ip in self.allNodes):
			self.allNodes.append(new_ip)
		if not (new_ip in self.neighbors):
			self.neighbors.append(new_ip) #track new neighbor
		newR = Route(new_ip, [new_ip]) #create route to new neighbor
		return self.addRoute(newR)



#when a route is provided by a neighbor:
#returns 0 if this is the first pathway to the node
#returns 1 if this is a superior route to the previously tracked route
#returns -1 if this is an inferior route and ignores the route
	def routeFromNeighbor(self, nei_ip, nei_route):
		nei_route.path.insert(0, nei_ip)
		nei_route.cost += 1  #LATER: be some sort of reference to cost of the best path to this neighbor
		return self.addRoute(nei_route)

a = Route(1,[3,2,1])
print(a)
print("-")
n = RoutingTable(1)
print(n)
print("-")
n.NewNeighbor(2)
r2 = Route(4, [3,4])
p = n.routeFromNeighbor(2, r2)
print(p)
print(n)
