#!/usr/bin/env python3
from reducer import Reducer
import sys

def main():
    #IP = '127.0.0.1'
    ID = int(sys.argv[1])

    f = open('setup.txt', 'r')
    numProc = int(f.readline().strip())
    sites = {}
    for i in range(numProc):
        sites[i + 1] = f.readline().strip().split()
    TCP = sites.get(ID)
    TCP_IP = TCP[0]
    portnum = 5100 + ID
    REDUCER = Reducer(TCP_IP, portnum, ID)
    REDUCER.run()

if __name__ == "__main__":
    main()
