import sys
import socket
import time


class Paxos():
    def __init__(self, index, ID):
        self.rcvdVotes = {} # upon receiving ack, add (channel:acknowledge msg) to this dict. not including mine
        self.numAccepts = 0
        self.index = index # for when we expand to PRM
        self.ballotNum = [0, 0]
        self.acceptNum = [0, 0]
        self.outgoingTCP = {}
        self.incomingTCP = {}
        self.val = None # null until a value has been accepted by majority
        self.ID = ID
        self.sites = {} # all the sites and their TCPs
        self.proposedVal = None # when a process wants to propose a value, it'll be stored here

    def rcvPrepare(self, data, channel):
        ballotRcvd = list(map(int, data[1].strip('[]').split(',')))
        print(ballotRcvd)
        if ((ballotRcvd[0] > self.ballotNum[0])
            | (ballotRcvd[0] == self.ballotNum[0])
            & (ballotRcvd[1] > self.ballotNum[1])):
            self.ballotNum = ballotRcvd
            self.outgoingTCP.get(channel).sendall(str('ack|'
                                                  + str(self.ballotNum) + '|'
                                                  + str(self.acceptNum) + '|'
                                                  + str(self.val)
                                                  ).encode())
            print('sent ack ' + str(self.ballotNum) + ' to ' + str(channel))

    def rcvAck(self, data, channel):
        majority = (len(self.sites) // 2) + 1
        self.rcvdVotes[channel] = data
        # if the number of rcvdVotes plus mine is a majority
        if (len(self.rcvdVotes) + 1 >= majority):
            # if all received values are None, then we set my val to my proposedVal
            # if not, then we set my val to the val that we received with the highest ballot
            maxVote = None
            for vote in self.rcvdVotes:
                if (self.rcvdVotes[vote][3] != 'None'):
                    ballotRcvd = list(map(int, self.rcvdVotes[vote][1].strip('[]').split(',')))
                    if (maxVote == None):
                        maxVote = self.rcvdVotes[vote]
                    elif ((ballotRcvd[0] > list(map(int, maxVote[1].strip('[]').split(',')))[0])
                            | (ballotRcvd[0] == list(map(int, maxVote[1].strip('[]').split(',')))[0])
                            & (ballotRcvd[1] > list(map(int, maxVote[1].strip('[]').split(',')))[1])):
                        maxVote = self.rcvdVotes[vote]
            print('maxVote = ' + str(maxVote))
            if (maxVote == None):
                self.val = self.proposedVal
            else:
                self.val = maxVote[3]
        for out in self.outgoingTCP:
            self.outgoingTCP.get(out).sendall(str('accept|'
                                                  + str(self.ballotNum) +'|'
                                                  + str(self.val)
                                                  ).encode())
            print('sent accept ' + str(self.val) + ' to ' + str(out))

    def receiveMsgs(self, incomingTCP):
        while True:
            for channel in incomingTCP:
                try:
                    data = incomingTCP.get(channel).recv(1024)
                    data = data.decode().strip().split('|')
                    # prepare msg looks like this: prepare|ballotNum
                    if (data[0] == 'prepare'):
                        self.rcvPrepare(data, channel)
                    # ack msg looks like this: ack|ballotNum|acceptNum|val
                    if (data[0] == 'ack'):
                        self.rcvAck(data, channel)
                except socket.error:
                    break

    def setup(self):
        f = open('setup.txt', 'r')
        numProc = int(f.readline().strip())
        for i in range(numProc):
            self.sites[i + 1] = f.readline().strip().split()
        print(self.sites)
        TCP = self.sites.get(self.ID)
        print(TCP)
        TCP_IP = TCP[0]
        TCP_PORT = int(TCP[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('trying to bind to ' + str(TCP_IP) + ', ' + str(TCP_PORT))
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        line = f.readline()
        while (line != ""):
            line = line.strip().split()
            sender = int(line[0])
            recvr = int(line[1])
            if (self.ID == sender):
                while True:
                    try:
                        TCP = self.sites.get(int(recvr))
                        TCP_IP = TCP[0]
                        TCP_PORT = int(TCP[1])
                        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        n.connect((TCP_IP, TCP_PORT))
                        self.outgoingTCP[recvr] = n
                        print('connected to ' + str(recvr))
                        break
                    except socket.error:
                        time.sleep(1)
            elif (self.ID == recvr):
                conn, addr = s.accept()
                conn.setblocking(0)
                self.incomingTCP[sender] = conn
            line = f.readline()
        self.receiveMsgs(self.incomingTCP)


    def propose(self, value):
        self.ballotNum[0] += 1
        self.ballotNum[1] = self.ID
        self.proposedVal = value
        for out in self.outgoingTCP:
            self.outgoingTCP.get(out).sendall(str('prepare|'
                                                        + str(self.ballotNum)
                                                        ).encode())
            print('sent to ' + str(out))
        self.receiveMsgs(self.incomingTCP)

    '''
    def accept():

    def acknowledge():

    def sendmsg(string):


    def propose():

    def decide():
    '''


