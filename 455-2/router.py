#!/usr/bin/python
# Filename: router.py

import sys,socket,select, time, DV #, readrouters
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
	time.sleep(10)

rFDs = []
wAddrs = {}
wFDs = []

rSockets = {}
oldData = {}

rSelectFrom = []
wSelectFrom = []

MasterDVTable = {}

def broadcastUpdates():

	update_string = "U"
	# for fd in MasterDVTable:
	# 	neighbor = MasterDVTable[fd].name
	# 	cost = MasterDVTable[fd].cost
	# 	update_string = update_string + " " + neighbor + " " + str(cost)

	# for fd in MasterDVTable:
	# 	if fd != server.fileno():
	# 		MasterDVTable[fd].socket.send(update_string + "")
	for fd in MasterDVTable:
	    update_string = "U"
	    if fd != server.fileno():
	        for Dest in MasterDVTable:
			    if Dest != server.fileno():
			        neighbor = MasterDVTable[fd].name
			    	if P == 1: 
			        	if neighbor in MasterDVTable[server.fileno()].DVTable:
			        		cost = MasterDVTable[Dest].cost
			        	elif neighbor in MasterDVTable[fd].DVTable:
			        		cost = 64
					else:
						cost = MasterDVTable[Dest].cost
				else: #if no poison reverse just send Dest Cost
			            cost = MasterDVTable[Dest].cost			
			        neighbor = MasterDVTable[Dest].name
				update_string = update_string + " " + neighbor + " " + str(cost)
		MasterDVTable[fd].socket.send(update_string + "")


class Update:
	def __init__(self, from_fd, dest, cost):
		self.from_fd = from_fd
		self.dest = dest
		self.cost = cost

	def do(self):
		#if myName == "A":
		#	print ("cost to %s was %d or %d" % (self.dest, MasterDVTable[self.from_fd].cost, MasterDVTable[self.from_fd].DVTable["A"]))
		#print ("update me %s for %s" % (myName, self.neighbor))
		MasterDVTable[self.from_fd].updateNeighbor(self.dest, self.cost)


		if self.dest == myName and (self.from_fd in MasterDVTable): #and sender from_fd is my neighbor
			#print ("update me %s for %s" % (myName, self.neighbor))
			MasterDVTable[self.from_fd].cost = self.cost
			MasterDVTable[server.fileno()].updateNeighbor(MasterDVTable[self.from_fd].name, self.cost)

		#	if myName == "A":
		#		print ("cost to %s is now %d or %d" % (self.dest, MasterDVTable[self.from_fd].cost, MasterDVTable[self.from_fd].DVTable["A"]))
		#		print ("cost to %s is now %d" % (self.dest, MasterDVTable[server.fileno()].DVTable[MasterDVTable[self.from_fd].name]))
		#		print("")
def printMasterTable():

	print("")
	print ("MasterDVTable of %s" % myName)
	for router in router_list:
		d = distanceTo(router)
		nh = nexthop(router)
		print("distance to %s = %d | nexthop : %s" % (router, d, nh))
	print("")


def updateTable(data, sender):
	data = data[2:]
	data = data.split()

	i = 0
	updates = []
	neighbor = ""
	cost = 0

	for d in data:
	
		if i % 2 == 0:
			neighbor = d

		else:
			cost = int(d)
			updates.append(Update(sender, neighbor, cost))

		i = i + 1

	for update in updates:
		update.do()

def lupdateTable(data):
	data = data[2:]
	data = data.split()

	neighbor = data[0]
	cost = int(data[1])

	for fd in MasterDVTable:
		if MasterDVTable[fd].name == neighbor:
			MasterDVTable[fd].updateNeighbor(myName, cost)
			MasterDVTable[fd].cost = distanceTo(neighbor)
			MasterDVTable[fd].nexthop = nexthop(neighbor)
	#printMasterTable()

def distanceTo(neighbor):

	min_distance = 99
	for fd in MasterDVTable:
		if MasterDVTable[fd].name == neighbor:
			return MasterDVTable[fd].cost

	#if we get here, neighbor is not a drect neighbor

	for fd in MasterDVTable:
		if neighbor in MasterDVTable[fd].DVTable:
			if MasterDVTable[fd].DVTable[neighbor] + MasterDVTable[fd].cost < min_distance:
				min_distance = MasterDVTable[fd].DVTable[neighbor] + MasterDVTable[fd].cost

	if min_distance < 99:
		return min_distance
	else:
		return 64

def nexthop(neighbor):
	nexthop = ""
	min_distance = 99

	for fd in MasterDVTable:
		if MasterDVTable[fd].name == neighbor:
			min_distance = MasterDVTable[fd].cost #cost to direct neighbor 
			nexthop = MasterDVTable[fd].name

	for fd in MasterDVTable:
		if neighbor in MasterDVTable[fd].DVTable :
			if MasterDVTable[fd].DVTable[neighbor] + MasterDVTable[fd].cost < min_distance: #distance to router(neighbor variable) + cost to our neigh
				min_distance = MasterDVTable[fd].DVTable[neighbor] + MasterDVTable[fd].cost
				nexthop = MasterDVTable[fd].name


	if min_distance < 99:
		return nexthop
	else:
		return None

if __name__ == '__main__':

	print "Router %s initialization started...\n" % myName

	router_list = readrouters(testDir) #global info
	router_link_list = readlinks(testDir, myName)#info about my neighbors

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

	MasterDVTable[server.fileno()] = DV.VectorTableEntry(myName, myName, 0, server, myName)
	rSelectFrom.append(server)

	#Initialize our sockets of neighbors and pass into

	for neighbor in router_link_list:

		rSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		host = myHost
		localOffset = router_link_list[neighbor].locallink
		port = myBaseport + localOffset

		#bind socket to the read end of the communication link
		rSock.bind((host, port))
		rFDs.append(port)

		nhost = router_list[neighbor].host
		nbaseport = router_list[neighbor].baseport
		remoteOffset = router_link_list[neighbor].remotelink
		nport = nbaseport + remoteOffset

		wAddrs[neighbor] = (nhost, nport)

		#connect socket to the write end of the communication link
		rSock.connect(wAddrs[neighbor])
		rSock.setblocking(1)

		rSockets[neighbor] = rSock
		rSelectFrom.append(rSock)

		cost = int(router_link_list[neighbor].cost)

		MasterDVTable[rSock.fileno()] = DV.VectorTableEntry(neighbor, myName, cost, rSock, neighbor)
		MasterDVTable[server.fileno()].updateNeighbor(neighbor, cost)

		print("")
		print ("%s will read from %d to revc from router %s" % (myName, port, neighbor))
		print ("%s will write to %d to send to router %s" % (myName, nport, neighbor))
		print ("%s will read from fd(%d) to recv from %s" %(myName, rSock.fileno(), neighbor))
		print ("")
		oldData[neihbor] = ""

	time.sleep(5)
	#if myName == "B":
	#	while 1:
			#send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#send_sock.connect(wAddrs["A"])
			#send_sock.send("Hello A, message from B!!!")
	#		print ("send to E")
	#		rSockets["E"].send("U C 10 A 10 E 6")
	#		time.sleep(200);
	printMasterTable()
	# for neighbor in router_list:
	# 	d = distanceTo(neighbor)
	# 	nh = nexthop(neighbor)
	# 	print("distance to %s = %d | nexthop : %s" % (neighbor, d, nh))


	broadcastUpdates()

	time.sleep(5)
	timeout = 5

	
	while rSelectFrom :
		readable, writable, exceptional = select.select(rSelectFrom, wSelectFrom, rSelectFrom, timeout)

		# if timeoutleft > 0:
		# 	timeout = timeoutleft
		# else:
		# 	timeout = 30
		# 	userinput = raw_input("Enter something\n")
		if not readable:
			#userinput = raw_input("Timeout: %d Enter something\n" % timeout)
			#broadcastUpdates()
			print ("timeout %s" % timeout)


		for s in readable:
			#listen_socket, listen_socket_addr = s.accept();
			data = s.recv(256);
			sender = MasterDVTable[s.fileno()].name
			print("recv'd %s from %s" % (data, sender))

			if len(data) <= 0: continue

			#oldData[sender] 
			

			if data != oldData[sender]:
				if data[0] == "U":
					updateTable(data, s.fileno())
					time.sleep(2)
					broadcastUpdates()
					printMasterTable()
					oldData[sender] = data
					#broadcastUpdates()
				if data[0] == "L":
					lupdateTable(data)
					printMasterTable()
					broadcastUpdates()
					oldData = data
					time.sleep(2)



	# Sockets to which we expect to write
	# Outgoing message queues (socket:Queue)
	message_queues = {}

	for fd in rSockets:
		print ("read from %d" % rSockets[fd].fileno())

	for fd in wSockets:
		print ("write  to %d" % wSockets[fd].fileno())

	time.sleep(10)

	if myName == "A":
		
		print ("sending \"hello B\"")
		server.connect(("localhost", 20021))
		#message=raw_input("enter a message")
		server.send("hello FROM AAAAA")
		time.sleep(10)
	if myName == "B":
		print ("receiving from A")
 
		a_socket, a_socket_addr = rSockets["A"].accept();
		s = a_socket.recv(256);

		print (s)
		time.sleep(10)

	print ("done")


else:
	print 'I have no import use, please run as main\n'


