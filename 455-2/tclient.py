import socket
import sys

localhost = sys.argv[1]
portNumber = int(sys.argv[2])
server_address = (localhost, portNumber)
my_address=(localhost,20010)
# Create a TCP/IP socket
socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socks.bind(my_address)
         
# Connect the socket to the port where the server is listening
print >>sys.stderr, 'connecting to %s port %s' % server_address
message = raw_input("Enter your masage\n")

socks.connect(server_address)
while message != "exit":
    
    print >>sys.stderr, '%s: sending "%s"' % (socks.getsockname(), message)
    socks.send(message)

            # Read responses on both sockets
        
    data = socks.recv(1024)
    print >>sys.stderr, '%s: received "%s"' % (socks.getsockname(), data)
    if not data:
        print >>sys.stderr, 'closing socket', socks.getsockname()
        socks.close()
    message = raw_input("Enter your masage\n")