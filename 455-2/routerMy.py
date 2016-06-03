#!/usr/bin/python
# Filename: router.py

import sys #, readrouters
# How to use get sys arguments
#for i in sys.argv:
#	print i
# or use  sys.argv[1],2,3,4 for arguments
#from sys import argv #gets ARGV Variable

from readrouters import readrouters, readlinks, RouterInfo, LinkInfo
#We can now use these imported functions and class structures

if __name__ == '__main__':
        print 'Router initialization started...\n'
	#Dictionary data struct is like hash table, d = {key1 : value1, key2 : value2 }
	router_list = readrouters(sys.argv[1])
	router_link_list = readlinks(sys.argv[1],sys.argv[2])
	for i in router_list:
		print "RouterName: %s, port# %d" % (i,router_list[i].baseport)
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)
	localhost = router_list[sys.argv[2]].host
	portNumber = router_list[sys.argv[2]].baseport
	server_address = (localhost, portNumber)
	server.bind(server_address)
	server.listen(5)
	inputs = [ server ]
	outputs = [ ]
	message_queues = {}
	for j in router_link_list:
		message_queues.put(j)
		message_queues.put(j)
	for j in router_link_list:
		neighbor_add = (localhost,router_list[j].baseport)
		connect.(server_address)
		server.send()
	
		#Select Send info:
		#Neighor j's Port# = router_list[j].baseport
		#D1 = j  , cost = router_link_list[j].remotelink
		#Select Recv info:
		#Select FD = Neighbor J's baseport
		#Neighbor J's DV Table  Updated cost = Select Data read
		print "Neighbor: %s, Link Cost: %d" % (j, router_link_list[j].remotelink)


      	print 'Router End...'
else:
	print 'I have no import use, please run as main\n'
