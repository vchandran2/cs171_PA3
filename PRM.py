import socket
import time
import paxos1

class PRM():
    def __init__(self,ID):
        self.rcvdVotes = {}     # upon receiving ack, add (channel:acknowledge msg) to this dict. not including mine
        self.accepts_dict = {}  # ballotnum:number of accepts
        self.index = 0          # index in the log of paxos objects that we are operating on
        self.outgoingTCP = {}   #id: socket
        self.incomingTCP = {}   #id: socket
        self.ID = ID
        self.sites = {} # all the sites and their TCPs
        self.proposedVal = None # when a process wants to propose a value, it'll be stored here
        self.majority = None
        self.firstTimeAccept = True
        self.rcvdDacks = {} # receive dack (channel:ack)
        self.log = [None]*20 # log of paxos objects
        self.cli_out_s = None
        self.cli_in_s =None

    def rcvPrepare(self, data, channel):
        ballotRcvd = list(map(int, data[1].strip('[]').split(',')))
        index = int(data[2])
        if self.log[index] == None:
            self.log[index] = paxos1.Paxos(index)
        if self.log[index].decided: # if the object is already decided NO ACK
            return
        print("ballot received: ",ballotRcvd,"index recv: ",index)
        if ((ballotRcvd[0] > self.log[index].ballotNum[0])
            | (ballotRcvd[0] == self.log[index].ballotNum[0])
            & (ballotRcvd[1] > self.log[index].ballotNum[1])):
            self.index = index
            self.log[index].ballotNum = ballotRcvd
            self.outgoingTCP.get(channel).sendall(str('ack|'
                                                  + str(self.log[index].ballotNum) + '|'
                                                  + str(self.log[index].acceptNum) + '|'
                                                  + str(self.log[index].val)       + '|'
                                                  + str(index)
                                                  +'&').encode())
            print('sent ack ' + str(self.log[index].ballotNum) + ' to ' + str(channel))

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
                self.log[self.index].val = self.log[self.index].proposedVal
            else:
                self.log[self.index].val = maxVote[3]
        for out in self.outgoingTCP:
            self.outgoingTCP.get(out).sendall(str('accept|'
                                                  + str(self.log[self.index].ballotNum) +'|'
                                                  + str(self.log[self.index].val)
                                                  +'&').encode())
            print('sent accept ' + str(self.log[self.index].val) + ' to ' + str(out))

    def receiveMsgs(self, incomingTCP):
        #print("RECEIVING MESSAGES")
        for channel in incomingTCP:
            try:
            #print("Starting for loop in receiveMSGS. Channel = ",channel)
                data = incomingTCP.get(channel).recv(1024).decode()
                data_split = data.strip().split('&')
                data_split = list(filter(None, data_split))
                for data in data_split:
                    data = data.strip().split('|')
                    if self.log[self.index].decided == True:
                        if(data[0] == 'dack'):
                            if channel not in self.rcvdDacks:
                                self.rcvdDacks[channel] = data
                        if(data[0] == 'decide'):
                            self.send_dack(channel)
                    else:
                        if (data[0] == 'decide'):
                            print('deciding on ' + data[1])
                            self.val = int(data[1])
                            self.send_dack(channel)
                            self.decide()
                        # prepare msg looks like this: prepare|ballotNum
                        if (data[0] == 'prepare'):
                            self.rcvPrepare(data, channel)
                        # ack msg looks like this: ack|ballotNum|acceptNum|val
                        if (data[0] == 'ack'):
                            self.rcvAck(data, channel)
                        if (data[0] == 'accept'):
                            print(str(data) + ' from ' + str(channel))
                            ballotRcvd = list(map(int, data[1].strip('[]').split(',')))
                            val = int(data[2])
                            self.recvAccept(ballotRcvd,val)
            except socket.error:
                continue

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
        s.listen(2)
        print('listening on paxos')
        line = f.readline()
        while (line != ''):
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
                        n.setblocking(0)
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
        # practicing just sending message from ID 1 to all others
        self.setupCLI(s)
        self.majority = (len(self.sites) // 2) + 1
        if (self.ID == 1):
            self.propose(5)
        if (self.ID == 2):
            self.propose(3)
        if (self.ID == 3):
            self.propose(1)
        while True:
            self.receiveMsgs(self.incomingTCP)

    def setupCLI(self,serversock):
        cli_addr = ('127.0.0.1',6000+self.ID)
        print("setting up cli on addr: ", cli_addr)
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                n.connect(cli_addr)
                n.setblocking(0)
                print("connected to CLI at addr",cli_addr)
                break
            except socket.error:
                time.sleep(1)
        self.cli_out_s = n
        print("attempting to accept")
        self.cli_in_s,addr = serversock.accept()
        self.cli_in_s.setblocking(0)
        print("accepted from cli")


    def compareBallots(self,ballot1,ballot2): # returns true if ballot1 is greater or equal to ballot2
        b1 = str(ballot1[0]) + str(ballot1[1])
        b2 = str(ballot2[0]) + str(ballot2[1])
        b1 = int(b1)
        b2 = int(b2)
        if b1 >= b2:
            return True
        return False

    def propose(self, value):               # Done, Not tested
        paxos_obj = paxos1.Paxos(self.index)
        self.log.insert(self.index,paxos_obj)
        self.log[self.index].ballotNum[0] += 1
        self.log[self.index].ballotNum[1] = self.ID
        self.log[self.index].proposedVal = value
        for out in self.outgoingTCP:
            self.outgoingTCP.get(out).sendall(str('prepare|'
                                                  + str(self.log[self.index].ballotNum) + '|'
                                                  + str(self.index)
                                                  + '&'
                                                  ).encode())
            print('sent to ' + str(out))
        self.receiveMsgs(self.incomingTCP)

    def recvAccept(self,ballot,value): # takes in accept msg
        b_key = str(ballot)
        if b_key not in self.accepts_dict:
            self.accepts_dict[b_key] = 1
        else:
            self.accepts_dict[b_key] += 1
        print("received accept: (ballot,value) = ",ballot,",",value)
        if self.compareBallots(ballot,self.log[self.index].ballotNum):
            print("ballot: ",ballot," is greater than: ", self.log[self.index].ballotNum)
            self.log[self.index].acceptNum = ballot
            self.log[self.index].val = value
            if self.firstTimeAccept == True:
                msg = "accept|"+b_key+"|"+ str(value) + "&"
                print("from recvAcc, sending accept msg: ",msg)
                for id in self.outgoingTCP:
                    self.outgoingTCP[id].sendall(msg.encode())
                self.firstTimeAccept = False
        print('num for ballot ' + str(b_key) + ':' + str(self.accepts_dict[b_key]) + ' majority: ' + str(self.majority))
        if self.accepts_dict[b_key] == self.majority:
            self.decide()
        print("DONE WITH RECVACCEPT")

    def decide(self):
        print("deciding on value: ",self.log[self.index].val)
        msg = "decide|" + str(self.log[self.index].val) + '&'
        num_othersites = len(self.sites) - 1
        self.log[self.index].decided = True
        while len(self.rcvdDacks) != num_othersites:
            for id in self.outgoingTCP:
                self.outgoingTCP[id].sendall(msg.encode())
            time.sleep(1)
            self.receiveMsgs(self.incomingTCP)
        self.reset()
        print("RESETED")
        quit()

    def send_dack(self,channel):
        msg = 'dack|'+ str(self.ID) + '&'
        self.outgoingTCP[channel].sendall(msg.encode())

    def reset(self):
        self.index += 1
        self.rcvdVotes = {}  # upon receiving ack, add (channel:acknowledge msg) to this dict. not including mine
        self.accepts_dict = {}  # ballotnum:number of accepts
        self.firstTimeAccept = True
        self.rcvdDacks = {}

    def replicate(self):
        return 0
    def merge(self):
        return 0
    def total(self):
        return 0
    def stop(self):
        return 0
    def resume(self):
        return 0
    def printdata(self):
        return 0

    def recvFromCli(self):
        try:
            data = self.cli_in_s.recv(1024).decode()
        except socket.error:
            return
        data = data.strip().split('&')
        if data[0] == 'replicate':
            self.replicate()
        elif data[0] == 'stop':
            self.stop()
        elif data[0] == 'resume':
            self.resume()
        elif data[0] == 'merge':
            self.merge()
        elif data[0] == 'total':
            self.total()
        elif data[0] == 'print':
            self.printdata()






