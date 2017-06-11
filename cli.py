import socket
import time
import os

IP = '127.0.0.1' # IP of the SITE
class cli:
    def __init__(self,ID):
        self.mapsockets = []                # list of outgoing sockets to mappers
        self.reducer_socket = None            # outgoing socket to reducer
        self.prm_socket_out = None                # outgoing socket to prm
        self.prm_socket_in = None
        self.ID = ID                          # can be generalized with an argument. for now, this only works for one CLI

    def setup(self):
        addr = (IP,6000+self.ID)
        addr_out = (IP,5000+self.ID)
        print("setting up at: ",addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(addr)
        s.listen(2)
        print('attempting to accept')
        conn, addr_in = s.accept()
        conn.setblocking(0)
        self.prm_socket_in = conn
        print("accepted from PRM")
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                n.connect(addr_out)
                n.setblocking(0)
                print("connected to PRM at addr:",addr_out)
                break
            except socket.error:
                time.sleep(1)
        self.prm_socket_out = n
        self.connectToMappers()
        self.connectToReducer()
        print("done with setup")
        self.execute_commands()

    def connectToMappers(self):
        addrs = []
        addrs.append((IP,5010 +self.ID))
        addrs.append((IP,5020+self.ID))
        for addr_out in addrs:
            n = self.connectTo(addr_out)
            self.mapsockets.append(n)

    def connectToReducer(self):
        addr = ((IP,5100 + self.ID))
        self.reducer_socket = self.connectTo(addr)

    def connectTo(self,addr_out):
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to', addr_out)
        while True:
            try:
                n.connect(addr_out)
                n.setblocking(0)
                print("connected at addr:", addr_out)
                break
            except socket.error:
                time.sleep(0.25)
        return n

    def execute_commands(self):
        while True:
            try:
                data = self.prm_socket_in.recv(1024).decode()
            except socket.error:
                pass
            inputstr = input("Enter command: ")
            inputstr = inputstr.strip().split()
            msg = ''
            if inputstr[0] == 'replicate':
                if len(inputstr) == 2:
                    filename = inputstr[1]
                    msg = 'replicate|'+ filename + '&'
            elif inputstr[0] == 'stop':
                msg = 'stop&'
            elif inputstr[0] == 'resume':
                msg = 'resume&'
            elif inputstr[0] == 'total':
                if len(inputstr) == 3:
                    msg = 'total|'+inputstr[1]+'|'+inputstr[2]+'&'
            elif inputstr[0] == 'print':
                msg = 'print&'
            elif inputstr[0] == 'merge':
                if len(inputstr) == 3:
                    msg = 'merge|'+inputstr[1]+'|'+inputstr[2]+'&'
            elif inputstr[0] == 'map':
                if len(inputstr) == 2:
                    self.mapFile(inputstr[1])
            elif inputstr[0] == 'reduce':
                if len(inputstr) == 3:
                    print(inputstr)
                    reduceMsg = 'reduce|'+inputstr[1]+'|'+inputstr[2]+'&'
                    self.reducer_socket.sendall(reduceMsg.encode())
            else:
                print("invalid command")
            self.prm_socket_out.sendall(msg.encode())
            if msg != '':
                self.wait()

    def mapFile(self,filename):
        file_size = self.getSize(filename)
        offset = file_size//2
        file = open(filename)
        while(True):
            c = file.read(1)
            if c == ' ':
                break
            offset+=1
        msg1 = filename + '|' + '0' + '|' + str(offset) + '&'
        msg2 = filename + '|' + str(offset) + '|' + str(file_size//2) + '&'
        self.mapsockets[0].sendall(msg1.encode())
        self.mapsockets[1].sendall(msg2.encode())


    def getSize(self,filename):
        st = os.stat(filename)
        return st.st_size

    def wait(self):
        while True:
            try:
                data = self.prm_socket_in.recv(1024).decode()
                print('received this dank data', data)
                data_split = data.strip().split('&')
                print('length of data:',len(data))
                if len(data) >= 1:
                    if data_split[0] == 'success':
                        print('success!')
                        return
                    if data_split[0] == 'failure':
                        print('fail!')
                        return
            except socket.error:
                continue
