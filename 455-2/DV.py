#!/usr/bin/python
# Filename: DV.py
# Implementation for Distance Vector Table structures and algorithm


class VectorTableEntry:
    def __init__(self, name, neighbor, cost, socket, nexthop):
		self.name = name
		self.DVTable = {neighbor : cost}; #dictionary
		self.socket = socket
		self.cost = cost
		self.nexthop = nexthop
		
    def updateNeighbor(self, neighbor, cost):

		self.DVTable[neighbor] = cost;
		self.keylist = self.DVTable.keys() 

    def getNeighborCost(neighbor):
		return self.DVTable[neighbor]
