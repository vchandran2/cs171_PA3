from mapper import Mapper
import sys

def main():
    IP = '127.0.0.1'
    ID = int(sys.argv[1])
    portnum = 5000 + ID # id is a two digit number
    MAPPER = Mapper(IP,portnum,ID)
    MAPPER.run()

main()