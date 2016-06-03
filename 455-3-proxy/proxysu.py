#!/usr/bin/python
#proxy.py
# Global Variables
import socket, thread, select, os

method_list = ['GET', 'PUT', 'POST', 'HEAD', 'OPTIONS', 'DELETE', 'TRACE']
DEFAULT_TIMEOUT = 60
SELECT_TIMEOUT = 3
DEFAULT_PORT = 60
MAX_TIMEOUT = 20
BUFFERSIZE = 1024
VERHTTP = 'HTTP/1.1'
proxyVER = 'V. 1.00' #Increment this for each new revision of proxy.py

class childhandler:
    def __init__(self, connection, address):
	self.child = connection
	self.timout = DEFAULT_TIMEOUT
	self.buffer = '' #[BUFFERSIZE] = 0 #may replace with dynamica allocation
	self.method, self.path, self.protocol = self.read_header()
        if self.method == 'CONNECT': #rewrite this
	    self.connect()
	elif self.method in method_list:
	    self.process_method()
	print 'Child has connect, now closing\n'
	self.child.close()

    

    def connect(self):
    	
		i = self.path.find(':')
		if -1 != i:
		    targetport = int(self.path[i + 1:])
		    targethost = path[:i]
		else:
		    port = DEFAULT_PORT
		# socket.getaddrinfo(host, port[, family[, socktype[, proto[, flags]]]])
		(family, _, _, _, address) = socket.getaddrinfo(host, port)[0] 
	        #use family and address of target we want to connect to
	        self.target = socket.socket(family)
	        self.target.connect(address)
		#modify Optional Header Modifications see Proxy.pdf for ways to handle this part
		#Fill in header with our Proxy server information
		self.child.send(VERHTTP+ ' 200 Connection  established\n' + 'ProxyServer-agent: %s\n\n' % proxyVER)
		timeout_count = 0
		timeout = MAX_TIMEOUT	
		mySoc = [self.child, self.target] 
		while 1:
			(readable, _, exceptional) = select.select(socs, [], socs, SELECT_TIMEOUT)
			timeout_count+=1
			if exceptional:
				break
			if readable:
				for s in readable:
					data = s.readable(BUFFERSIZE)
					if s is self.child:
						target = self.target
					else:
						target = self.child
					if data:
						target.send(data)
						timeout_count = 0
			if timeout_count == timeout:
				break




	
    def read_header(self):
	while 1:
	    self.buffer += self.child.recv(BUFFERSIZE)

	    CR_found = self.buffer.find('\n') # returns -1 if not found, else returns first instance of \n

	    if CR_found != -1:
		break

	print'Header read: %s' %self.buffer[:CR_found] #print out buffer
	DataIn = (self.buffer[:CR_found+1]).split() # make a list of header recv
	self.buffer = self.buffer[CR_found+1:] #point buffer to rest of packets data
		
	return DataIn


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
    myBaseport = 6060

    server.bind((myHost, myBaseport))
    print 'Server created on %s, port:%d' % (myHost, myBaseport)
    server.listen(0) #0 ensures only children accept connections?

    while 1:
	newchild = os.fork()
	if newchild == 0:
	    source, address = server.accept()
	    childhandler(source,address)
        childcount += 1
	while childcount :
	    #Wait for child to die #find os.function for this
	    newchild, status = os.waitpid(newchild, 0)
	    if newchild == 0 :
		break
	    else :
		print 'server: Client %d closed connect with vaule %d' % (pid, os.WIFEXITED(status))
		childcount -= 1


