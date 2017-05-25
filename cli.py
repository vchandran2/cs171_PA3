import socket
import time

class cli:
    def __init__(self):
        self.mapsockets = None                # list of outgoing sockets to mappers
        self.reducer_socket = None            # outgoing socket to reducer
        self.prm_socket_out = None                # outgoing socket to prm
        self.prm_socket_in = None
        self.ID = 5005                     # can be generalized with an argument. for now, this only works for one CLI

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
                        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        n.connect((TCP_IP, TCP_PORT))
                        self.prm_socket_out = n
                        print('connected to ' + str(recvr))
                        break
                    except socket.error:
                        time.sleep(1)
            elif (self.ID == recvr):
                print('trying to accept')
                conn, addr = s.accept()
                self.prm_socket_in = conn
                conn.setblocking(0)
            line = f.readline()




    def execute_commands(self):
        while True:
            inputstr = input("Enter command: ")
            inputstr = inputstr.split()
            if inputstr[0] == 'replicate':
                filename = inputstr[1]
                msg = 'replicate|'+ filename + '&'
                self.prm_socket_out.sendall(msg.encode())
                return 0
            elif inputstr[0] == 'stop':
                msg = 'stop&'
                self.prm_socket_out.sendall(msg.encode())
                return 0
            elif inputstr[0] == 'resume':
                msg = 'resume&'
                self.prm_socket_out.sendall(msg.encode())
                return 0
            elif inputstr[0] == 'total':
                return 0
            elif inputstr[0] == 'print':
                return 0
            elif inputstr[0] == 'merge':
                return 0
            else:
                print("invalid commmand")



    def replicate(self):
        return 0

    def stop(self):
        return 0

    def resume(self):
        return 0

    def total(self):
        return 0

    def printCmd(self):
        return 0

    def merge(self):
        return 0
