import sys
import socket
import time


class Paxos():
    def __init__(self, index, ID):
        self.numVotes = 0
        self.numAccepts = 0
        self.index = index
        self.ballotNum = [0, 0]
        self.acceptNum = [0, 0]
        self.val = None
        self.ID = ID

    def rcvPrepare(self, data, channel):
        ballotRcvd = data[1]
        if ((ballotRcvd[0] > self.ballotNum[0])
            | (ballotRcvd[0] == self.ballotNum[0])
            & (ballotRcvd[1] > self.ballotNum[1])):
            self.ballotNum = ballotRcvd
            print(channel)

    def receiveMsgs(self, incomingTCP):
        while True:
            for channel in incomingTCP:
                try:
                    data = incomingTCP.get(channel).recv(1024)
                    data = data.decode().strip().split('|')
                    if (data[0] == 'prepare'):
                        self.rcvPrepare(data, channel)
                except socket.error:
                    break

    def setup(self):
        f = open('setup.txt', 'r')
        numProc = int(f.readline().strip())
        sites = {}
        for i in range(numProc):
            sites[i + 1] = f.readline().strip().split()
        print(sites)
        TCP = sites.get(self.ID)
        print(TCP)
        TCP_IP = TCP[0]
        TCP_PORT = int(TCP[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('trying to bind to ' + str(TCP_IP) + ', ' + str(TCP_PORT))
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        incomingTCP = {}
        outgoingTCP = {}
        line = f.readline()
        while (line != ""):
            line = line.strip().split()
            sender = int(line[0])
            recvr = int(line[1])
            if (self.ID == sender):
                while True:
                    try:
                        TCP = sites.get(int(recvr))
                        TCP_IP = TCP[0]
                        TCP_PORT = int(TCP[1])
                        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        n.connect((TCP_IP, TCP_PORT))
                        outgoingTCP[recvr] = n
                        print('connected to ' + str(recvr))
                        break
                    except socket.error:
                        time.sleep(1)
            elif (self.ID == recvr):
                conn, addr = s.accept()
                conn.setblocking(0)
                incomingTCP[sender] = conn
            line = f.readline()
        # practicing just sending message from ID 1 to all others
        if (self.ID == 1):
            self.ballotNum[0] = 1
            self.ballotNum[1] = self.ID
            for out in outgoingTCP:
                outgoingTCP.get(out).sendall(str('MARKER'
                                                                 + '-'
                                                                 + str(out)
                                                                 + '-2|').encode())
                print('sent to ' + str(out))
        else:
            self.receiveMsgs(incomingTCP)










    '''
    def accept():

    def acknowledge():



    def propose():

    def decide():
    '''


