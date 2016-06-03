#!/usr/bin/env python
import socket, sys, os
from thread import *

buffer_size = 8192
max_conn = 5
listening_port = 8080
#try:
#	listening_port  = int(raw_input("[*] Enter listening_port number: "))
#except KeyboardInterrupt:
#	print "\n[*] User Requested an Interrupt"
#	print "[*] Applicaton Exiting ..."
#	sys.exit()



def conn_string(conn, data, addr):
	print data
	raw_input("request data above. press enter to continue.")

	try:
		first_line = data.split('\n')[0]

		url = first_line.split(' ')[1]

		http_pos = url.find("://")
		if (http_pos == -1):
			temp = url
		else:

			temp = url[(http_pos + 3):]

		port_pos = temp.find(":")

		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)
		webserver = ""
		port = -1
		if (port_pos==-1 or webserver_pos < port_pos):
			port  = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]

		proxy_server(webserver, port, conn, data, addr)
	except Exception, e:
		print "this ->" + str(e)
		pass

def proxy_server(webserver, port, conn, data, addr):
#	print ("webserver: %s" % webserver)
#	print ("port: ->%d<-" % port)
#	print ("conn: ->%s<-" % conn)
#	#print ("data: ->%s<-" % str(data))
#	print ("addr: ->%s<-" % str(addr))
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print webserver
		print port
		s.connect((webserver, port))
		s.send(data)
		while 1:
			reply = s.recv(buffer_size)

			if(len(reply) > 0):

				conn.send(reply)
				print ("reply: ->%s<-" % reply)
				dar = float(len(reply))
				dar = float(dar / 1024)
				dar = "%.3s" % (str(dar))
				dar = "%s KB" % (dar)
				'Print A Custom Message For Request Complete'
				print "[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar))
			else:
				break

		s.close()
		conn.close()

	except KeyboardInterrupt:
		s.close()
		conn.close()
	except socket.error, (value, message):
		s.close()
		conn.close()
		sys.exit(1)

def start():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		s.bind(('', listening_port))
		s.listen(max_conn)

		print "[*] Initializing Sockets ... Done"
		print "[*] Sockets Binded Successfully ..."
		print("[*] Server started Successfully [ %d ]\n" % listening_port)
	except Exception, e:
		print "[*] Unable To Initialize Socket"
		print e
		sys.exit(2)

	while 1:
		try:
			conn, addr = s.accept()
			data = conn.recv(buffer_size)

			if(os.fork() == 0):
				conn_string(conn, data, addr)
		except KeyboardInterrupt:
			s.close()
			conn.close()
			print "\n[*] Proxy Server Shutting Down ..."
			print "[*] Have a Nice Day ... Homie!"
			sys.exit(1)

	s.close()

start()