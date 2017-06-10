from reducer import Reducer
import sys

def main():
    IP = '127.0.0.1'
    ID = int(sys.argv[1])
    portnum = 5100 + ID
    REDUCER = Reducer(IP, portnum, ID)
    REDUCER.run()

if __name__ == "__main__":
    main()
