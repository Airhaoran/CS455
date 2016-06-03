#!/usr/bin/python
# Filename: router.py

import sys,socket,select,Queue #, readrouters
# How to use get sys arguments
#for i in sys.argv:
#	print i
# or use  sys.argv[1],2,3,4 for arguments
#from sys import argv #gets ARGV Variable

from readrouters import readrouters, readlinks, RouterInfo, LinkInfo
#We can now use these imported functions and class structures
def NeighborConnectionCheck(Link,router_list,router_link_list, socket):
    retval = 0
    
    localhost  = router_list[router_link_list[Link]].host
    portNumber = router_list[router_link_list[Link]].baseport
    NeighborAddr = (localhost, portNumber)
    if socket.connect_ex(NeighborAddr) > 0 :
	retval = 1


    return retval
if __name__ == '__main__':
    if len(sys.argv) < 3:
	print 'Not enough arguments'
	close(0)
    elif len(sys.argv) == 4:
	P = sys.argv[1]
        testdir = sys.argv[2]
        name = sys.argv[3]
    else:
	P = 0
        testdir = sys.argv[1]
        name = sys.argv[2]
    print 'Router initialization started...\n'
    router_list = readrouters(testdir)
    router_link_list = readlinks(testdir,name)
    for i in router_list:
        print "RouterName: %s, port# %d" % (i,router_list[i].baseport)
    for j in router_link_list:
	#Select Send info:
	#Neighor j's Port# = router_list[j].baseport
	#D1 = j  , cost = router_link_list[j].remotelink
	#Select Recv info:
	#Select  gives us = Neighbor J's baseport
	#Neighbor J's DV Table  Updated cost = Select Data read
	print "Neighbor: %s, Link Cost: %d" % (j, router_link_list[j].remotelink)

    print 'Router init End...'
    print 'Creating Router Connection now'
    # Create a TCP/IP socket
    SocketList = []
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    # Bind the socket to the port
    localhost = router_list[name].host
    portNumber = router_list[name].baseport

    server_address = (localhost, portNumber)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    server.bind(server_address)
    # Listen for incoming connections
    server.listen(5)
    # Sockets from which we expect to read
    print 'Server socket fd()= %d\n' % server.fileno()
    SocketList.append(server.fileno())
    # Sockets to which we expect to write, empty until we get some connections made
    for i in router_link_list: #reading FD
	nlocalhost  = router_list[i].host
    	nportNumber = router_list[name].baseport + router_link_list[i].locallink
	NeighborAddr = (nlocalhost, nportNumber)
	tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        print 'Created socket addr %s, %d \n' % (nlocalhost, nportNumber)
        tempSock.setblocking(0)
	tempSock.bind(NeighborAddr)
        SocketList.append(tempSock.fileno())
        print 'Server added socket fd()= %d\n' % tempSock.fileno()
        localhost  = router_list[i].host
    	portNumber = router_list[i].baseport + router_link_list[i].remotelink
	NeighborAddr = (localhost, portNumber)
        tempSock.listen(5)
        print 'Socket connected to socket addr %s, %d \n' % (localhost, portNumber)
        tempSock.connect(NeighborAddr)
    while 1:
	s = 1
    inputs = [ SocketList ]
        
    # Outgoing message queues (socket:Queue)
    message_queues = {}
    connectedLinks = 0
    timeout = 30.00
    '''while inputs:
        if connectedLinks < router_link_list.items(): #until all Links established, keep trying
	    connectedLinks += NeighborConnectionCheck(connectedLinks,router_list,router_link_list,server)

	readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)

	# Handle inputs
	for s in readable:

            if s is server.fileno():
            	# A "readable" server socket is ready to accept a connection
            	connection, client_address = s.accept()
            	print >>sys.stderr, 'new connection from', client_address
            	connection.setblocking(0)
            	inputs.append(connection) #add neighbors connection to inputs
		outputs.append(connection) #add neighbors connection to outputs

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


