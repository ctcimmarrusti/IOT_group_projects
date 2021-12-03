import ipaddress

class Route:
	def __init__(self, dest_ip, ip_path):
		self.dest = dest_ip
		self.path = ip_path #lsit expected will error in next line if anything else
		self.cost = len(ip_path) #option to set cost based on latency or throughput later

	def __str__(self):
		return "dest: " + str(self.dest) + "\npath: " + str(self.path) + "\ncost: " + str(self.cost)

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

#adds node to allnodes list, adds it to neighbors, creates new route and adds it to routetable
	def NewNeighbor(self, new_ip):
		if not (new_ip in self.allNodes):
			self.allNodes.append(new_ip)
		if not (new_ip in self.neighbors):
			self.neighbors.append(new_ip) #track new neighbor
		n = Route(new_ip, [new_ip]) #create route to new neighbor
		if(new_ip in self.route_table.keys()):
			if n.cost < self.route_table[new_ip].cost: #if new cost is less than current pathway cost, replace pathway
				self.route_table.update({new_ip: n}) #this allows only one path to any IP

a = Route(1,[3,2,1])
print(a)
print("-")
n = RoutingTable(1)
print(n)
print("-")
n.NewNeighbor(2)
n.routeFromNeighbor(2, [3,4])
print(n)
