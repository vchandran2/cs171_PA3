from paxos import Paxos
from PRM import PRM
from cli import cli
import sys

def main():
    print(sys.argv)
    trial = Paxos(index=0, ID=int(sys.argv[1]))
    trial.setup()


if __name__ == "__main__":
    main()

