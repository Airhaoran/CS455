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

rFDs = []
wAddrs = {}
wFDs = []

rSockets = {}

rSelectFrom = []
wSelectFrom = []

MasterDVTable = {}

def broadcastUpdates():

	update_string = "U"

	for fd in MasterDVTable:
		neighbor = MasterDVTable[fd].name
		cost = MasterDVTable[fd].cost
		update_string = update_string + " " + neighbor + " " + str(cost)

	for fd in MasterDVTable:
		if fd != server.fileno():
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

	print ("MasterDVTable of %s" % myName)
	for fd in MasterDVTable:
		neighbor = MasterDVTable[fd].name 
		cost = MasterDVTable[fd].cost

		print ("%s : %d" % (neighbor, cost))


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

	printMasterTable()


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

	MasterDVTable[server.fileno()] = DV.VectorTableEntry(myName, myName, 0, server)

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

		rSockets[neighbor] = rSock
		rSelectFrom.append(rSock)

		cost = int(router_link_list[neighbor].cost)

		MasterDVTable[rSock.fileno()] = DV.VectorTableEntry(neighbor, myName, cost, rSock)
		MasterDVTable[server.fileno()].updateNeighbor(neighbor, cost)

		print("")
		print ("%s will read from %d to revc from router %s" % (myName, port, neighbor))
		print ("%s will write to %d to send to router %s" % (myName, nport, neighbor))
		print ("%s will read from fd(%d) to recv from %s" %(myName, rSock.fileno(), neighbor))
		print ("")

	time.sleep(5)
	#if myName == "B":
	#	while 1:
			#send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#send_sock.connect(wAddrs["A"])
			#send_sock.send("Hello A, message from B!!!")
	#		print ("send to E")
	#		rSockets["E"].send("U C 10 A 10 E 6")
	#		time.sleep(200);

	broadcastUpdates()
	
	while rSelectFrom :
		readable, writable, exceptional = select.select(rSelectFrom, wSelectFrom, rSelectFrom)

		#if leftovertimeout > 0:
		#	timeout = leftovertimeout
		#else:
		#	timeout = 30
			#LET neighbors know callUsend()

		for s in readable:
			#listen_socket, listen_socket_addr = s.accept();
			data = s.recv(256);
			sender = MasterDVTable[s.fileno()].name
			print("recv'd %s from %s" % (data, sender))

			if len(data) <= 0: continue

			if data[0] == "U":
				updateTable(data, s.fileno())
				#broadcastUpdates()


	# Sockets to which we expect to write
	# Outgoing message queues (socket:Queue)
	message_queues = {}

	for fd in rSockets:
		print ("read from %d" % rSockets[fd].fileno())

	for fd in wSockets:
		print ("write  to %d" % wSockets[fd].fileno())

	time.sleep(5)

	if myName == "A":
		
		print ("sending \"hello B\"")
		server.connect(("localhost", 20021))
		#message=raw_input("enter a message")
		server.send("hello FROM AAAAA")
		time.sleep(10)
	if myName == "B":
		print ("receiving from A")
		#server.connect(("localhost", 20040))
		#rSockets["A"].connect(("localhost", 20040))
		a_socket, a_socket_addr = rSockets["A"].accept();
		s = a_socket.recv(256);
		#s = server.recv(256)
		print (s)
		time.sleep(10)

	print ("done")


else:
	print 'I have no import use, please run as main\n'


