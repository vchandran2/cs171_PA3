import socket

class cli:
    def __init__(self,reducer_socket,prm_socket,mapsockets):
        self.mapsockets = mapsockets                # list of outgoing sockets to mappers
        self.reducer_socket = reducer_socket        # outgoing socket to reducer
        self.prm_socket = prm_socket                # outgoing socket to prm

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

    def print(self):
        return 0

    def merge(self):
        return 0
