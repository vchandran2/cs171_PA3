import sys
import socket
import time

class Paxos():
    def __init__(self, index):
        self.index = index # for when we expand to PRM
        self.ballotNum = [0, 0]
        self.acceptNum = [0, 0]
        self.val = None # null until a value has been accepted by majority
        self.proposedVal = None # when a process wants to propose a value, it'll be stored here
        self.decided = False
        self.filename = None