import socket
import time

class cli:
    def __init__(self):
        self.mapsockets = 0                # list of outgoing sockets to mappers
        self.reducer_socket = 0            # outgoing socket to reducer
        self.prm_socket = 0                # outgoing socket to prm

    def setup(self):
        f = open('setup.txt', 'r')
        f.readline() #skip first line
        TCP_PRM = f.readline().strip().split()
        TCP_PRM_IP = TCP_PRM[0]
        TCP_PRM_PORT = int(TCP_PRM[1])
        # try to connect with PRM
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                n.connect((TCP_PRM_IP, TCP_PRM_PORT))
                self.prm_socket = n
                print('connected to PRM')
                break
            except socket.error:
                time.sleep(1)
        TCP_CLI = f.readline().strip().split()
        TCP_CLI_IP = TCP_CLI[0]
        TCP_CLI_PORT = int(TCP_CLI[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_CLI_IP, TCP_CLI_PORT))
        s.listen(1)
        print('listening on CLI',TCP_CLI_PORT)
        #accept from PRM
        conn, addr = s.accept()
        conn.setblocking(0)




    def execute_commands(self):
        inputstr = input("Enter command: ")


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
