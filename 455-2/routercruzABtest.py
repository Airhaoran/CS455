#!/usr/bin/python
# Filename: router.py

import sys,socket,select,Queue, time #, readrouters
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
wSockets = {}

rSelectFrom = []
wSelectFrom = []

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

      	print 'Router init End...'
	print 'Creating Router Connection now'
	# Create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#server.setblocking(0)

	# Bind the socket to the port
	myHost = router_list[myName].host
	myBaseport = router_list[myName].baseport

	##server_address = (localhost, portNumber)
	#print >>sys.stderr, 'starting up on %s port %s' % server_address
	#server.bind((myhost, mybaseport))
	
	#server.bind((myHost, myBaseport))
	#server.connect((myHost, myBaseport))
	
	# Listen for incoming connections
	##server.listen(5)
	# Sockets from which we expect to read
	##inputs = [ server ]

	#Initialize our sockets of neighbors and pass into

	N = []

	for neighbor in router_link_list:

		rSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = myHost
		localOffset = router_link_list[neighbor].locallink
		port = myBaseport + localOffset

		#bind socket to listen on (read from)
		rSock.bind((host, port))
		rFDs.append(port)
		rSock.listen(10)
		rSockets[neighbor] = rSock
		rSelectFrom.append(rSock)

		#bind socket to send to (write to)
		#wSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		nhost = router_list[neighbor].host
		nbaseport = router_list[neighbor].baseport
		remoteOffset = router_link_list[neighbor].remotelink
		nport = nbaseport + remoteOffset

		#wSock.bind((nhost, nport))
		wAddrs[neighbor] = (nhost, nport)
		#wSockets[neighbor] = wSock

		print ("%s will read from %d to revc from router %s" % (myName, port, neighbor))
		print ("%s will write to %d to send to router %s" % (myName, nport, neighbor))

	time.sleep(10)
	if myName == "B":
		send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		send_sock.connect((wAddrs["A"]))
		send_sock.send("Hello A, message from B!!!")
		
		
	while rSelectFrom :
		readable, writable, exceptional = select.select(rSelectFrom, wSelectFrom, rSelectFrom)

		for s in readable:
			listen_socket, listen_socket_addr = s.accept();
			data = listen_socket.recv(1000);
			print ("recv'd %s from " % data)


	# Sockets to which we expect to write
	outputs = [N]
	# Outgoing message queues (socket:Queue)
	message_queues = {}

	for fd in rSockets:
		print ("read from %d" % rSockets[fd].fileno())

	for fd in wSockets:
		print ("write  to %d" % wSockets[fd].fileno())

	time.sleep(15)

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


  	'''while inputs:
		# Wait for at least one of the sockets to be ready for processing
    		print >>sys.stderr, '\nwaiting for the next event'
    		readable, writable, exceptional = select.select(inputs, outputs, inputs)
    		# Handle inputs
    		for s in readable:

        		if s is server:
            			# A "readable" server socket is ready to accept a connection
            			connection, client_address = s.accept()
            			print >>sys.stderr, 'new connection from', client_address
            			connection.setblocking(0)
            			inputs.append(connection)

            			# Give the connection a queue for data we want to send
            			message_queues[connection] = Queue.Queue()


        		else:
            			data = s.recv(1024)
            			if data:
                			# A readable client socket has data
                			print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                			message_queues[s].put(data)
                			# Add output channel for response
                			if s not in outputs:
                    				outputs.append(s)

            			else:
                		    # Interpret empty result as closed connection
                		    print >>sys.stderr, 'closing', client_address, 'after reading no data'
                		    # Stop listening for input on the connection
                		    if s in outputs:
                    			outputs.remove(s)
                	       	    inputs.remove(s)
                		    s.close()

                		    # Remove message queue
                		    del message_queues[s]
    			# Handle outputs
    			for s in writable:
        			try:
            			    next_msg = message_queues[s].get_nowait()
        			except Queue.Empty:
            		 	# No messages waiting so stop checking for writability.
            			    print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
            			    outputs.remove(s)
        			else:
            			    print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
            			    s.send(next_msg)
    			# Handle "exceptional conditions"
    			for s in exceptional:
        		    print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
        		    # Stop listening for input on the connection
        		    inputs.remove(s)
        		    if s in outputs:
            		        outputs.remove(s)
        		    s.close()

        		    # Remove message queue
        		    del message_queues[s]'''




else:
	print 'I have no import use, please run as main\n'


