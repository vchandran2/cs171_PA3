import socket
import time

class cli:
    def __init__(self,ID):
        self.mapsockets = None                # list of outgoing sockets to mappers
        self.reducer_socket = None            # outgoing socket to reducer
        self.prm_socket_out = None                # outgoing socket to prm
        self.prm_socket_in = None
        self.ID = ID                          # can be generalized with an argument. for now, this only works for one CLI

    def setup(self):
        addr = ('127.0.0.1',6000+self.ID)
        addr_out = ('127.0.0.1',5000+self.ID)
        print("setting up at: ",addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(addr)
        s.listen()
        '''
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                n.connect(addr_out)
                print("connected to PRM at addr:",addr_out)
                break
            except socket.error:
                time.sleep(1)
        self.prm_socket_out = n
        '''
        print('attempting to accept')
        conn,addr_in = s.accept()
        self.prm_socket_in = conn
        self.prm_socket_out = conn
        print("accepted from PRM")





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
