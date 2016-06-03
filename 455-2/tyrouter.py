#!/usr/bin/python
# Filename: router.py

import sys,socket,select, time, TDV #, readrouters
# How to use get sys arguments
#for i in sys.argv:
#	print i
# or use  sys.argv[1],2,3,4 for arguments
#from sys import argv #gets ARGV Variable

from readrouters import readrouters, readlinks, RouterInfo, LinkInfo
#We can now use these imported functions and class structures

myName = sys.argv[2]
testDir = sys.argv[1]

#print ("testDir  first -> %s" % testDir)
P = 0

if (len(sys.argv) < 3):
	print ("Two few arguments")
	sys.exit()
elif len(sys.argv) == 4:
	P = 0

print (sys.argv[1])

if sys.argv[1] == '-p': #string compare
	P = 1
	testDir = sys.argv[2]
	myName = sys.argv[3]
else:
	P = 0
	testDir = sys.argv[1]
	myName = sys.argv[2]

if P:
	print ("poision flag")
	time.sleep(1)

router_list = readrouters(testDir) #global info
router_link_list = readlinks(testDir, myName)#info about my neighbors

rFDs = []
wAddrs = {}
wFDs = []

rSockets = {}

rSelectFrom = []
wSelectFrom = []

DVTable = {}
DirectNeighborCost = {}
NDVTable = {}

def poisonBroadcastUpdates():

	normal_update_string = "U"
	specials = {}

	#get routers who I go to indirectly
	for router in router_list:
		normal_update_string = normal_update_string + " " + router + " " + str(DVTable[router].cost)

		nexthop = DVTable[router].nexthop

		if nexthop != router:
			#specials[nexthop] = DVTable[router]
			if nexthop != None:
				specials[nexthop] = specials.get(nexthop, {})
				specials[nexthop][router] = DVTable[router]




	for neighbor in router_link_list:
		if neighbor in specials:
			#build own string
			special_update_string = "U"
			#special_router = specials[neighbor].neighbor

			for router in router_list:
				if router in specials[neighbor]:
					special_update_string = special_update_string + " " + router + " " + "64"
				else:
					special_update_string = special_update_string + " " + router + " " + str(DVTable[router].cost)

			DVTable[neighbor].socket.send(special_update_string)


		else:
			DVTable[neighbor].socket.send(normal_update_string)

def broadcastUpdates():

	update_string = "U"

	for router in DVTable:
		update_string = update_string + " " + router + " " + str(DVTable[router].cost)

	for neighbor in router_link_list:
		DVTable[neighbor].socket.send(update_string)

class Update:
	def __init__(self, sender, dest, cost):
		self.sender = sender
		self.dest = dest
		self.cost = cost

def printMasterTable():

	print("")
	print ("DVTable of %s" % myName)
	for router in DVTable:
		cost = DVTable[router].cost
		nexthop = DVTable[router].nexthop
		print("distance to %s = %d | nexthop : %s" % (router, cost, nexthop))

	neighbor_string = ""
	for neighbor in NDVTable:
		neighbor_string = neighbor + ":"
		for neighborsneighbor in NDVTable[neighbor]:
			neighbor_string = neighbor_string + " " + neighborsneighbor + " " + str(NDVTable[neighbor][neighborsneighbor].cost) + " |"
		print (neighbor_string)

	print("")


def uMessage(data, sender):
	data = data[2:]
	data = data.split()

	i = 0
	updates = []
	neighbor = sender
	cost = 0

	for d in data:
	
		if i % 2 == 0:
			neighbor = d

		else:
			cost = int(d)
			updates.append(Update(sender, neighbor, cost))

		i = i + 1

	changed = 0

	for update in updates:
		current_cost = NDVTable[sender][update.dest].cost

		if current_cost != update.cost:
			changed = 1
			NDVTable[sender][update.dest].cost = update.cost

	if not changed:
		print ("nothing changed")
		return

	#go thruu all routers in table and see if there is a faster way to get there
	for router1 in DVTable:
		if router1 == myName: #router1 is router we want to get to
			continue
		
		for router2 in NDVTable: #check our neighbors to see if they have after way to get to this node
			our_cost_to_router = DVTable[router1].cost
			our_cost_to_neighbor = DVTable[router2].cost
			neighbor_cost_to_router = NDVTable[router2][router1].cost

			cost_thru_neighbor = our_cost_to_neighbor + neighbor_cost_to_router

			if cost_thru_neighbor < our_cost_to_router:
				DVTable[router1].nexthop = DVTable[router2].nexthop
				DVTable[router1].cost = cost_thru_neighbor

	#i think we only need to check if the sender now has a faster way to get somewhere
	#for router in DVTable:
	#	if router == myName: #no way to get to me faster than thru me
	#		continue

	#	our_cost_to_router = DVTable[router].cost
	#	our_cost_to_sender = DVTable[sender].cost
	#	sender_cost_to_router = NDVTable[sender][router].cost

	#	cost_thru_sender = our_cost_to_sender + sender_cost_to_router

	#	if cost_thru_sender < our_cost_to_router:
	#		DVTable[router].cost = cost_thru_sender
	#		DVTable[router].nexthop = sender



	#broadcastUpdates()
	if P: poisonBroadcastUpdates()
	else : broadcastUpdates()


def lMessage(data):
	data = data[2:]
	data = data.split()

	neighbor = data[0]
	cost = int(data[1])

	if not neighbor in router_link_list:
		print ("can't do that update because %s is not my neighbor" % (neighbor))

	print ("new between me (%s) and %s is now %d" % (myName, neighbor, cost))

	update = Update(neighbor, myName, cost)

	current_cost = DVTable[neighbor].cost

	changed = 0

	if current_cost != update.cost:
		changed = 1
		DVTable[neighbor].cost = update.cost
		DVTable[neighbor].nexthop = neighbor
		#NDVTable[neighbor][myName].cost = 64

		#we now think we can't get to any node with nexthop of sender
		#sender will send us new info
		#we sender can't get to us anymore and we set all nodes with nexthop of sender to infinity
		print ("neighbor: %s " % neighbor)
		# for router in DVTable:
		# 	print ("%s nh %s" % (router, DVTable[router].nexthop))
		# 	if DVTable[router].nexthop == neighbor:
			
		# 		DVTable[router].nexthop = None
		# 		DVTable[router].cost = 64

		# for router in NDVTable:
		# 	for router2 in NDVTable[router]:
		# 		NDVTable[router][router2].cost = 64
				

	if not changed:
		print ("nothing changed")
		return

	# for router1 in DVTable:
	# 	if router1 == myName: #router1 is router we want to get to
	# 		continue
		
	# 	for router2 in NDVTable: #check our neighbors to see if they have after way to get to this node
	# 		our_cost_to_router = DVTable[router1].cost
	# 		our_cost_to_neighbor = DVTable[router2].cost
	# 		neighbor_cost_to_router = NDVTable[router2][router1].cost

	# 		cost_thru_neighbor = our_cost_to_neighbor + neighbor_cost_to_router

	# 		if cost_thru_neighbor < our_cost_to_router:
	# 			DVTable[router1].nexthop = router2
	# 			DVTable[router1].cost = cost_thru_neighbor

	if P: poisonBroadcastUpdates()
	else : broadcastUpdates()



if __name__ == '__main__':

	print "Router %s initialization started...\n" % myName

	for name in router_list:
		print ("RouterName: %s, port# %d" % (name ,router_list[name].baseport))

	print("")

	for name in router_link_list:
		print "Neighbor: %s, Link Cost: %d" % (name, router_link_list[name].cost)

	print("")
	print ('initialization...')
	# Create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#server.setblocking(0)

	# Bind the socket to the port
	myHost = router_list[myName].host
	myBaseport = router_list[myName].baseport

	server.bind((myHost, myBaseport))

	DVTable[myName] = TDV.VectorTableEntry(myName, 0, myName, server)
	rSelectFrom.append(server)

	#Initialize our sockets of neighbors and pass into
	for router in router_list:
		if not (router in router_link_list):
			#not our neighbor
			if router != myName:
				DVTable[router] = TDV.VectorTableEntry(router, 64, None, None) #no nexthop and no socket
			else:
				DVTable[router] = TDV.VectorTableEntry(router, 0, myName, server) #no nexthop and no socket

		else:
			rSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			host = myHost
			localOffset = router_link_list[router].locallink
			port = myBaseport + localOffset

			rSock.bind((host, port))

			nhost = router_list[router].host
			nbaseport = router_list[router].baseport
			remoteOffset = router_link_list[router].remotelink
			nport = nbaseport + remoteOffset

			#connect socket to the write end of the communication link
			rSock.connect((nhost, nport))
			rSock.setblocking(1)

			rSelectFrom.append(rSock)
			cost = int(router_link_list[router].cost)

			DVTable[router] = TDV.VectorTableEntry(router, cost, router, rSock)
			NDVTable[router] = {}

			for r in router_list:
				NDVTable[router][r] = TDV.VectorTableEntry(r, 64, r, None)


			print("")
			print ("%s will read from port(%d) to revc from router %s" % (myName, port, router))
			print ("%s will read from fd(%d) to recv from %s" %(myName, rSock.fileno(), router))
			print ("%s will write to port(%d) to send to router %s" % (myName, nport, router))
			print ("")

	time.sleep(3)

	printMasterTable()

	#broadcastUpdates()
	if P: poisonBroadcastUpdates()
 	else : broadcastUpdates()

	time.sleep(3)

	timeout = 7

	init_count = 0

	
	while rSelectFrom :
		readable, writable, exceptional = select.select(rSelectFrom, wSelectFrom, rSelectFrom, timeout)

		#if not readable:
			#broadcastUpdates()


		for s in readable:
			data = s.recv(256);
			senderfileno = s.fileno()

			sender = ""

			for neighbor in router_link_list:
				if DVTable[neighbor].socket.fileno() == senderfileno:
					sender = neighbor
					break

			print("recv'd \"%s\" from %s" % (data, sender))

			if len(data) <= 0: 
				print ("no data sender? %s" % sender)
				continue

			if data[0] == "U" and init_count < len(NDVTable.keys()): #this is initial init
				print("init update")
				init_count = init_count + 1
				uMessage(data, sender)
				printMasterTable()

				if init_count == len(NDVTable.keys()):
					print ("network init complete!")
					

			elif data[0] == "U":
				init_count = init_count + 1
				uMessage(data, sender)
				printMasterTable()
				print("reg update %d" % init_count)
				#time.sleep(1)


			if data[0] == "L":
				lMessage(data)
				printMasterTable()
				time.sleep(7)



else:
	print 'I have no import use, please run as main\n'


