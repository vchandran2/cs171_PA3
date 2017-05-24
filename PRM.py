from paxos import Paxos
import socket

class PRM():
    def __init__(self):
        self.index = 0
        self.log = [None] * 3

    def setup(self):
        f = open('setup.txt', 'r')
        f.readline()  # skip the first line
        TCP_PRM = f.readline()
        TCP_PRM_IP = TCP_PRM[0]
        TCP_PRM_PORT = TCP_PRM[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('trying to bind to ' + str(TCP_PRM_IP) + ', ' + str(TCP_PRM_PORT))
        s.bind((TCP_PRM_IP, TCP_PRM_PORT))
        s.listen(1)
        # should first try to connect with its paxos module, for our testing purposes, the first one




    def replicate(self):
        pax = Paxos()

