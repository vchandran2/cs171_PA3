from paxos import Paxos
import socket
import time

class PRM():
    def __init__(self):
        self.index = 0
        self.log = [None] * 3
        self.ID = 5004          # can be generalized with an argument. for now, this only works for one PRM

    def setup(self):
        f = open('setupEx', 'r')
        sitesEx = {}
        for i in range(5):
            TCP = f.readline().strip().split()
            sitesEx[int(TCP[1])] = TCP
        TCP = sitesEx.get(self.ID)
        print(TCP)
        TCP_IP = TCP[0]
        TCP_PORT = int(TCP[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('trying to bind to ' + str(TCP_IP) + ', ' + str(TCP_PORT))
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        line = f.readline()
        while (line != ''):
            line = line.strip().split()
            sender = int(line[0])
            recvr = int(line[1])
            if (self.ID == sender):
                while True:
                    try:
                        TCP = sitesEx.get(recvr)
                        TCP_IP = TCP[0]
                        TCP_PORT = int(TCP[1])
                        print(TCP)
                        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        n.connect((TCP_IP, TCP_PORT))
                        print('connected to ' + str(recvr))
                        break
                    except socket.error:
                        time.sleep(1)
            elif (self.ID == recvr):
                conn, addr = s.accept()
                conn.setblocking(0)
            line = f.readline()



    def replicate(self):
        pax = Paxos()

