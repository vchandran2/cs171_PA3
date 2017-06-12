import socket
import time
from paxos1 import Paxos
from log import log
import ast

#TODO:
    # Reduce needs to receive messages
    # Test locally, Then set it up on Eucalyptus

IP_local = '127.0.0.1'
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
        self.rcvdDacks = {} # receive dack (channel:ack)
        self.log = [None]*100 # log of paxos objects
        self.cli_out_s = None
        self.cli_in_s = None
        self.stopped = False
        self.waitingCounter = 0
        self.waiting = False

    def sendMessage(self,sock,msg):
        msg = msg.encode()
        sock.send(msg)
        #filesize = len(msg)
        #sent = 0
        #while sent < filesize:
            #sent += sock.send(msg,1024)
            #msg = msg[sent:]

    def rcvPrepare(self, data, channel):
        ballotRcvd = list(map(int, data[1].strip('[]').split(',')))
        index = int(data[2])
        if self.log[index] is None:
            self.log[index] = Paxos(index)
        if self.log[index].decided: # if the object is already decided NO ACK
            return
        print("(received prepare) ballot received: ",ballotRcvd,"index recv: ",index,"from: ",channel)
        if ((ballotRcvd[0] > self.log[index].ballotNum[0])
            | (ballotRcvd[0] == self.log[index].ballotNum[0])
            & (ballotRcvd[1] > self.log[index].ballotNum[1])):
            self.index = index
            self.log[index].ballotNum = ballotRcvd
            if(self.log[index].val is None):
                self.sendMessage(self.outgoingTCP.get(channel),str('ack|'
                                                      + str(self.log[index].ballotNum) + '|'
                                                      + str(self.log[index].acceptNum) + '|'
                                                      + str(self.log[index].val)       + '|' #bug will probably happen
                                                      + str(index)
                                                      +'&'))
            else:
                self.sendMessage(self.outgoingTCP.get(channel), str('ack|'
                                                          + str(self.log[index].ballotNum) + '|'
                                                          + str(self.log[index].acceptNum) + '|'
                                                          + str(self.log[index].val) + '|'  # bug will probably happen
                                                          + str(index) + '|'
                                                          + str(self.log[index].val.filename) + '|'
                                                          + str(self.log[index].val.file)
                                                          + '&'))
            self.waiting = True
            print('sent ack (bal, val) ' + str(self.log[index].ballotNum) +', '+ str(self.log[index].val) + ' to ' + str(channel))

    def rcvAck(self, data, channel):
        ballot = data[1]
        ballot = list(map(int, ballot.strip('[]').split(',')))
        if self.compareBallots(ballot, self.log[self.index].ballotNum):
            majority = (len(self.sites) // 2) + 1
            self.rcvdVotes[channel] = data
            print('received Ack from: ', channel)
            # if the number of rcvdVotes plus mine is a majority
            if (len(self.rcvdVotes) + 1 == majority):
                print('received majority of ACKS')
                # if all received values are None, then we set my val to my proposedVal
                # if not, then we set my val to the val that we received with the highest ballot
                maxVote = None
                for vote in self.rcvdVotes:
                    if (self.rcvdVotes[vote][3] != 'None'):
                        ballotRcvd = list(map(int, self.rcvdVotes[vote][1].strip('[]').split(',')))
                        if (maxVote is None):
                            maxVote = self.rcvdVotes[vote]
                        elif ((ballotRcvd[0] > list(map(int, maxVote[1].strip('[]').split(',')))[0])
                                | (ballotRcvd[0] == list(map(int, maxVote[1].strip('[]').split(',')))[0])
                                & (ballotRcvd[1] > list(map(int, maxVote[1].strip('[]').split(',')))[1])):
                            maxVote = self.rcvdVotes[vote]
                print('maxVote = ' + str(maxVote))
                if (maxVote is None):
                    self.log[self.index].val = self.log[self.index].proposedVal
                else:
                    self.log[self.index].val.filename = maxVote[5]
                    self.log[self.index].val.file = self.strToDict(maxVote[6])
                msg = 'accept|'+str(self.log[self.index].ballotNum)+'|'
                msg += str(self.log[self.index].val.file)+'|'+self.log[self.index].val.filename #send dict|filename
                msg += '&'
                b_key = str(self.log[self.index].ballotNum)
                self.accepts_dict[b_key] = 1
                for out in self.outgoingTCP:
                    self.sendMessage(self.outgoingTCP.get(out),msg)
                    print('sent '+ msg + ' to ' + str(out))
                self.waiting = True

    def receiveAll(self):
        if self.waiting:
            print('waiting: ',self.waitingCounter)
            self.waitingCounter += 1
        if self.waitingCounter == 20:
            self.fail()
        self.receiveCLI()
        self.receiveMsgs(self.incomingTCP)
        time.sleep(0.1)

    def fail(self):
        print('failure')
        self.log[self.index] = None
        self.waiting = False
        self.waitingCounter = 0
        msg = 'failure&'
        self.sendMessage(self.cli_out_s,msg)

    def receiveCLI(self):
        #print("receiving from cli")
        try:
            datum = self.cli_in_s.recv(1024).decode()
            print("received from cli")
            data_split = datum.strip().split('&')
            for data in data_split:
                if data != '':
                    data = data.split('|')
                    print(data)
                    if self.stopped:
                        if data[0] == 'resume':
                            self.resume()
                            self.sendSuccessToCLI()
                    else:
                        if data[0] == 'replicate':
                            print("replicate received")
                            self.replicate(data[1])
                        elif data[0] == 'stop':
                            self.stop()
                            self.sendSuccessToCLI()
                        elif data[0] == 'resume':
                            self.resume()
                            self.sendSuccessToCLI()
                        elif data[0] == 'merge':
                            pos1 = int(data[1])
                            pos2 = int(data[2])
                            self.merge(pos1,pos2)
                            self.sendSuccessToCLI()
                        elif data[0] == 'total':
                            pos1 = int(data[1])
                            pos2 = int(data[2])
                            self.total(pos1,pos2)
                            self.sendSuccessToCLI()
                        elif data[0] == 'print':
                            self.printdata()
                            self.sendSuccessToCLI()
                    #self.sendSuccessToCLI()
        except socket.error:
            return
        return

    def sendSuccessToCLI(self):
        msg = 'success&'
        print('sending success to CLI')
        self.sendMessage(self.cli_out_s,msg)


    def receiveMsgs(self, incomingTCP):
        for channel in incomingTCP:
            try:
                data = incomingTCP.get(channel).recv(1000000)
                data = data.decode()
                '''
                data = incomingTCP.get(channel).recv(1024).decode()
                data = data.strip()
                while data[-1] != '&': # if last char in string does not equal & recv again
                    try:
                        print('received 1KB')
                        data += incomingTCP.get(channel).recv(1024).decode().strip()
                    except socket.error:
                        continue'''
                if (self.stopped):
                    break
                if data != '':
                    print('waiting == false, waiting counter == 0')
                    self.waiting = False
                    self.waitingCounter = 0
                data_split = data.strip().split('&')
                data_split = list(filter(None, data_split))
                for data in data_split:
                    data = data.strip().split('|')
                    if self.log[self.index] is not None and self.log[self.index].decided == True:
                        if(data[0] == 'dack'):
                            print('received dack from', channel)
                            if channel not in self.rcvdDacks:
                                self.rcvdDacks[channel] = data
                        if(data[0] == 'decide'):
                            print('received decide from', channel)
                            self.send_dack(channel)
                    else:
                        if (data[0] == 'decide'):
                            if data[3] == str(self.index):
                                print('received first decide from', channel, 'data:', data[1])
                                if self.log[self.index] is None:
                                    self.log.insert(self.index,Paxos(self.index))
                                self.log[self.index].val = log(data[2],data[1])
                                self.send_dack(channel)
                                self.decide()
                        # prepare msg looks like this: prepare|ballotNum
                        if (data[0] == 'prepare'):
                            print('received prepare from', channel)
                            self.rcvPrepare(data, channel)
                        # ack msg looks like this: ack|ballotNum|acceptNum|val
                        if (data[0] == 'ack'):
                            print('received ack from', channel)
                            self.rcvAck(data, channel)
                        if (data[0] == 'accept'):
                            print('received '+ str(data) + ' from ' + str(channel))
                            ballotRcvd = list(map(int, data[1].strip('[]').split(',')))
                            val = self.strToDict(data[2])
                            filename = data[3]
                            self.recvAccept(ballotRcvd,val,filename)
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
        print("receiving all")
        self.majority = (len(self.sites) // 2) + 1
        while True:
            self.receiveAll()
            time.sleep(0.5)

    def setupCLI(self,serversock):
        cli_addr = (IP_local,6000+self.ID)
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
        paxos_obj = Paxos(self.index)
        self.log.insert(self.index,paxos_obj)
        self.log[self.index].ballotNum[0] += 1
        self.log[self.index].ballotNum[1] = self.ID
        self.log[self.index].proposedVal = value
        msg = str('prepare|'
                                                  + str(self.log[self.index].ballotNum) + '|'
                                                  + str(self.index)
                                                  + '&'
                                                  )
        for out in self.outgoingTCP:
            self.sendMessage(self.outgoingTCP.get(out),msg)
            print('sent ',msg, 'to ', str(out))
        self.waiting = True
        #self.receiveMsgs(self.incomingTCP)

    def recvAccept(self,ballot,value,filename): # takes in accept msg
        b_key = str(ballot)
        if b_key not in self.accepts_dict:
            self.accepts_dict[b_key] = 1
        else:
            self.accepts_dict[b_key] += 1
        print("received accept: (ballot,value) = ",ballot,",",value)
        if self.log[self.index] is None:
            self.log.insert(self.index,Paxos(self.index))
        if self.compareBallots(ballot,self.log[self.index].ballotNum):
            print("ballot: ",ballot," is greater than: ", self.log[self.index].ballotNum)
            self.log[self.index].acceptNum = ballot
            self.log[self.index].val = log(filename,value)
            if self.accepts_dict[b_key] == 1:
                msg = 'accept|'+b_key+'|'+ str(value) + '|' + filename+ '&'
                print("from recvAcc, sending accept msg: ",msg)
                for id in self.outgoingTCP:
                    self.sendMessage(self.outgoingTCP[id],msg)
                self.waiting = True
        print('num for ballot ' + str(b_key) + ':' + str(self.accepts_dict[b_key]) + ' majority: ' + str(self.majority))
        if self.accepts_dict[b_key] == self.majority:
            self.decide()
        print("DONE WITH RECVACCEPT")

    def decide(self):
        print("deciding on value: ",self.log[self.index].val)
        msg = "decide|" + str(self.log[self.index].val.file)+'|'\
              +self.log[self.index].val.filename + '|'+ str(self.index)+ '&'
        num_othersites = len(self.sites) - 1
        self.log[self.index].decided = True
        while len(self.rcvdDacks) != num_othersites:
            for id in self.outgoingTCP:
                self.sendMessage(self.outgoingTCP[id],msg)
         #  self.waiting = True
            time.sleep(1)
            self.receiveMsgs(self.incomingTCP)
        self.reset()
        print("RESETED")
        self.sendSuccessToCLI()

    def send_dack(self,channel):

        msg = 'dack|'+ str(self.ID) + '&'
        self.sendMessage(self.outgoingTCP[channel],msg)
        # self.waiting = True

    def reset(self):
        self.index += 1
        self.rcvdVotes = {}  # upon receiving ack, add (channel:acknowledge msg) to this dict. not including mine
        self.accepts_dict = {}  # ballotnum:number of accepts
        self.rcvdDacks = {}



    def replicate(self,filename):
        print("replicating")
        logobj = log(filename)
        self.propose(logobj)
        print('done with replicate method')

    def merge(self,pos1,pos2):
        combined_dict = {}
        dict1 = self.log[pos1].val.file
        dict2 = self.log[pos2].val.file
        for key in dict1:
            if key not in combined_dict:
                combined_dict[key] = dict1[key]
            else:
                combined_dict[key] += dict1[key]
        for key in dict2:
            if key not in combined_dict:
                combined_dict[key] = dict2[key]
            else:
                combined_dict[key] += dict2[key]
        for key in combined_dict:
            print(key,combined_dict[key])
        print('end of merge method')

    def total(self,pos1,pos2):
        total = 0
        dict1 = self.log[pos1].val.file
        dict2 = self.log[pos2].val.file
        for key in dict1:
            total += dict1[key]
        for key in dict2:
            total += dict2[key]
        print("total: ",total)
        print('end of total method')

    def stop(self):
        self.stopped = True
        print('stopped')
        return


    def resume(self):
        print('resumed')
        self.stopped = False
        return

    def printdata(self):
        for i in self.log:
            if i is not None:
                filename = i.val.filename
                print(filename)


    def strToDict(self,strang):
        return ast.literal_eval(strang)





