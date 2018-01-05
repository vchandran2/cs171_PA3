#!/usr/bin/env python3
from mapper import Mapper
import sys

def main():
#    IP = '127.0.0.1'
    ID = sys.argv[1]
    num = ID[-1]
    ID = int(ID)
    f = open('setup.txt', 'r')
    numProc = int(f.readline().strip())
    sites = {}
    for i in range(numProc):
        sites[i + 1] = f.readline().strip().split()
    TCP = sites.get(int(num))
    TCP_IP = TCP[0]
    portnum = 5000 + ID # id is a two digit number
    MAPPER = Mapper(TCP_IP,portnum,ID)
    MAPPER.run()

main()
