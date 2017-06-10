from mapper import Mapper
import sys

def main():
    IP = '127.0.0.1'
    ID = int(sys.argv[1])
    portnum = 5010 + ID
    MAPPER = Mapper(IP,portnum,ID)
    MAPPER.run()

main()