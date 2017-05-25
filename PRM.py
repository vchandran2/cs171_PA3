from paxos import Paxos
import socket
import time

class PRM():
    def __init__(self):
        self.index = 0
        self.log = [None] * 3

    def setup(self):
        f = open('setup.txt', 'r')
        f.readline()  # skip the first line
        TCP_PRM = f.readline().strip().split()
        TCP_PRM_IP = TCP_PRM[0]
        TCP_PRM_PORT = int(TCP_PRM[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('trying to bind to ' + str(TCP_PRM_IP) + ', ' + str(TCP_PRM_PORT))
        s.bind((TCP_PRM_IP, TCP_PRM_PORT))
        s.listen(1)
        print('listening on PRM',TCP_PRM_PORT)
        TCP_CLI = f.readline().strip().split()
        TCP_CLI_IP = TCP_CLI[0]
        TCP_CLI_PORT = int(TCP_CLI[1])
        n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_PAX = f.readline().strip().split()
        TCP_PAX_IP = TCP_PAX[0]
        TCP_PAX_PORT = int(TCP_PAX[1])
        # should then try to accept from its paxos module
        conn, addr = s.accept()
        conn.setblocking(0)
        print('accepted from paxos')
        # should then try to connect with its paxos module, for our testing purposes, the first one
        while True:
            try:
                n.connect((TCP_PAX_IP, TCP_PAX_PORT))
                print('connected to Paxos')
                break
            except socket.error:
                time.sleep(1)
        # should try to connect with the CLI
        print('trying to connect to CLI',TCP_CLI_PORT)
        while True:
            try:
                n.connect((TCP_CLI_IP, TCP_CLI_PORT))
                print('connected to CLI')
                break
            except socket.error:
                time.sleep(1)
        # accept from CLI
        conn, addr = s.accept()
        conn.setblocking(0)
        print('conn', conn)



    def replicate(self):
        pax = Paxos()

