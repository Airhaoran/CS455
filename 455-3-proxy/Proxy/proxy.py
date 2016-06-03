#!/usr/bin/python
#proxy.py
# Global Variables
import socket, thread, select, os, sys
# https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol  -List of methods and ways to handle them
method_list = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH' ]
DEFAULT_TIMEOUT = 60
MAX_TIMEOUT = 100
DEFAULT_PORT = 80
BUFFERSIZE = 1024
VERHTTP = 'HTTP/1.1' #Crt-shft-i , click network, reload page to view standard HTTP headers
proxyVER = 'V. 1.002' #Increment this for each new revision of proxy.py

class childhandler:
    def __init__(self, connection, address):
	self.path = '' #declare path variable global
	self.protocol = '' #declare variable global
	self.childconnection = connection
	self.timout = DEFAULT_TIMEOUT
	self.buffer = '' #[BUFFERSIZE] = 0 #may replace with dynamica allocation
	self.method, self.path, self.protocol = self.read_header()
	self.connect_welcome()
	print 'target connection has now ended, now closing child connection\n'
	#targetconnection should already be closed from connect_welcome() return call
	self.childconnection.close()
        sys.exit(0) #kill child process

    def create_path_connection(self,target):
        i = target.find(':')
	if -1 != i:
	    targetport = int(target[i + 1:])
	    target = target[:i]
	else:
	    targetport = DEFAULT_PORT
	
        print 'Host = %s\nPath = %s\nTargetPort = %d\n\n' %(target,self.path, targetport)
	# socket.getaddrinfo(host, port[, family[, socktype[, proto[, flags]]]])
	(family, _, _, _, address) = socket.getaddrinfo(target, targetport)[0] 
        #use family and  Client address(could modify to proxy server address?) of target we want to connect to
        self.targetconnection = socket.socket(family)
        self.targetconnection.connect(address)

    def connect_welcome(self):
	mySocs = [] #create list for sockets
	mySocs.append(self.childconnection)
	#modify Optional Header Modifications see Proxy.pdf for ways to handle this part
	#Fill in header with our Proxy server information possibly
        if self.method == 'CONNECT': #send proxy-server welcome message to connected child (all other data is mundane)
	    self.create_path_connection(self.path)
	    self.childconnection.send(VERHTTP+ 'Connection  established\n' + 'Connected through Cpts455 ProxyServer V.%s\n\n' % proxyVER )
	else : #any other messages go to the dest path connection
	    self.path = self.path[7:]
            x = self.path.find('/')
            host = self.path[:x]        
            path = self.path[x:]
	    self.create_path_connection(host)
	    self.targetconnection.send('%s %s %s\n'%(self.method, path, self.protocol) #recompile header
                             + self.buffer) #append rest of buffer data to packet
	
	
	mySocs.append(self.targetconnection)        
	self.buffer = '' #reset buffer
	timeout_count = 0
	timeout = MAX_TIMEOUT
	while 1:
	    readable, writable, exceptional = select.select(mySocs, [], mySocs, timeout)
	    timeout_count += 1
	    if exceptional:
		self.targetconnection.close()
		break
	    if readable:
		for j in readable:
		    data_in = j.recv(BUFFERSIZE) #recv our data
		    if j is self.childconnection: 
			socket_out = self.targetconnection #if message is from self, send to target
		    else:
			socket_out = self.childconnection
		    if data_in:
			timeout_count = 0
			socket_out.send(data_in)
	    if timeout_count == timeout:
		self.targetconnection.close()
		break




    def read_header(self):
	while 1:
	    self.buffer += self.childconnection.recv(BUFFERSIZE)

	    CR_found = self.buffer.find('\n') # returns -1 if not found, else returns first instance of \n

	    if CR_found != -1:
		break

	print'Header read: %s\n\n' %self.buffer[:CR_found] #print out buffer
	DataIn = (self.buffer[:CR_found+1]).split() # make a list of header recv
	self.buffer = self.buffer[CR_found+1:] #point buffer to rest of packets data
		
	return DataIn #return list of header data parced


if __name__ == '__main__':
    childcount = 0
    pid = 0
    status = 0
    print ('initialization Proxy Server...')
	# Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #_DGRAM
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow reconnection
	#server.setblocking(0)

	# Bind the socket to the port
    myHost = 'localhost'
    myBaseport = 8080

    server.bind((myHost, myBaseport))
    print 'Server created on %s, port:%d' % (myHost, myBaseport)
    server.listen(0) #0 ensures only children accept connections?

    while 1:
	
	source, address = server.accept()
	newchild = os.fork()
	if newchild == 0:
	    childhandler(source,address)
	
	del source #need to delete source socket from accept return call
        childcount += 1
	print 'Newchild created #%d\n\n' % childcount
	
	#newchild, status = os.waitpid(newchild, 0)
	while childcount :
	    #Wait for child to die #find os.function for this
	    newchild, status = os.waitpid(-1, os.WNOHANG)
	    if newchild == 0 : #if this is a child break back into while loop to call accept and fork another child connection
		break
	    else :
		print 'server: Client %d closed connect with vaule %d' % (pid, os.WIFEXITED(status))
		childcount -= 1


    server.close()




