#!/usr/bin/python
# Filename: TDV.py
# Implementation for Distance Vector Table structures and algorithm


class VectorTableEntry:
    def __init__(self, neighbor, cost, nexthop, socket):
		self.neighbor = neighbor
		self.cost = cost
		self.nexthop = nexthop
		self.socket = socket
