def broadcastUpdates():

	update_string = "U"

	for fd in MasterDVTable:
	    if fd != server.fileno():
	        for Dest in MasterDVTable:
		    if Dest != server.fileno():
		        neighbor = MasterDVTable[fd].name
		        if P == 1: #if poison reverse enabled
		            if MasterDVTable[server.fileno()].DVTable.has_key(neighbor)
			        cost = MasterDVTable[Dest].cost
		            elif MasterDVTable[fd].DVTable.has_key(neighbor):
				cost = 64 #inifinity!
			    else:
				cost = MasterDVTable[Dest].cost
		        else: #if no poison reverse just send Dest Cost
		            cost = MasterDVTable[Dest].cost			
		        neighbor = MasterDVTable[Dest].name
			update_string = update_string + " " + neighbor + " " + str(cost)
		MasterDVTable[fd].socket.send(update_string + "")
class Update:
