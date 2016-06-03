
def neighborName(portNumber, router_list):
	name = None
    for j in router_list:
        if portNumber == router_list[j].baseport:
            	name = j   
    return name