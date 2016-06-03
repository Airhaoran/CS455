#!/usr/bin/python
# Filename: router.py
import itertools, time
import DV
import sys,socket,select,Queue #, readrouters
# How to use get sys arguments
#for i in sys.argv:
#	print i
# or use  sys.argv[1],2,3,4 for arguments
#from sys import argv #gets ARGV Variable
#from neighbor import neighborName

a = ""
neighbor_name= [ ]
inputs = [ ]
MasterDVtable = {}


def neighborAdress(neighborName):
    router_list = readrouters(sys.argv[1])
    address = 0
    for j in router_list:
        if neighborName == j:
            address = router_list[j].baseport   
    
    return address

from readrouters import readrouters, readlinks, RouterInfo, LinkInfo
#We can now use these imported functions and class structures

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Not enough arguments'
        close(0)
    elif len(sys.argv) == 4:
        P = sys.argv[1]
        testDir = sys.argv[2]
        myName = sys.argv[3]
    else:
        P = 0
        testDir = sys.argv[1]
        myName = sys.argv[2]
    
    print 'Router initialization started...\n'
	
    router_list = readrouters(testDir)
    router_link_list = readlinks(testDir,myName)
    for i in router_list:
    	print "RouterName: %s, port# %d" % (i,router_list[i].baseport)
    for j in router_link_list:
        neighbor = j
    	print "Neighbor: %s, Link Cost: %d" % (j, router_link_list[j].remotelink)
        print 'Router init End...'
    print 'Creating Router Connection now'

        
localhost = router_list[myName].host
portNumber = router_list[myName].baseport
my_address = (localhost, portNumber)
rSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rSock.bind(my_address)





        
print >>sys.stderr, 'My localhost: %s My portnumber %s' % my_address
#print rSock.fileno()
newDV = DV.VectorTableEntry(myName, myName, 0, rSock)
#print rSock.fileno()
MasterDVtable[rSock.fileno()] = newDV #MasterDVtable[2].name A
        # Initializing 
for j in router_link_list:
    print 'j = %s' % j
    neighbor_name.append(j)
    a = j
    portmy = portNumber+router_link_list[j].locallink
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (localhost, portmy)
    a.bind(address)
    neighborPort =neighborAdress(j)+router_link_list[j].remotelink
    neighborAdd = (localhost,neighborPort)
    a.connect(neighborAdd)   
    inputs.append(a)
    print "Binding portNumber: %s" % portmy
    message = "I am " + sys.argv[2]
    print a.fileno()

    newDV = DV.VectorTableEntry(j, myName, router_link_list[j].cost, a)
    #print rSock.fileno()
    MasterDVtable[a.fileno()] = newDV #MasterDVtable[2].name A

    




time.sleep(5)# sleep for 20 seconds to let other router set up
while 1:
    for x,y in zip(inputs,neighbor_name):
        #neighborPort =neighborAdress(y)+router_link_list[y].remotelink
        #neighborAdd = (localhost,neighborPort)
        #x.connect(neighborAdd)
        x.send(message)
        print "sent %s to neighbor_name = %s at = %s\n" % (message, y, neighborPort)    	
        outputs = []
        print >>sys.stderr, '\nwaiting for the next event\n'
        readable, writable, exceptional = select.select(inputs, outputs, inputs,10)
        for s in readable:
            data= s.recv(1024)

            if data:
                #print >>sys.stderr, 'received %s \n' % data
                print >>sys.stderr, 'received %s from %s' % (data,s.getpeername())



                    


                        
        		



else:
	print 'I have no import use, please run as main\n'


