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
        s.listen(1)
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
        print("done with setup")
        self.execute_commands()

    def execute_commands(self):
        while True:
            inputstr = input("Enter command: ")
            inputstr = inputstr.strip().split()
            msg = ''
            if inputstr[0] == 'replicate':
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
            else:
                print("invalid command")
            self.prm_socket_out.sendall(msg.encode())
            if msg != '':
                self.wait()

    def wait(self):
        while True:
            try:
                data = self.prm_socket_in.recv(1024).decode()
                print('received this dank data', data)
                data_split = data.strip().split('&')
                print(len(data))
                if len(data) >= 1:
                    if data_split[0] == 'success':
                        print('success!')
                        return
                    if data_split[0] == 'failure':
                        print('fail!')
                        return
            except socket.error:
                continue
            time.sleep(0.5)
