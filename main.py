from paxos import Paxos
import sys

def main():
    print(sys.argv)
    trial = Paxos(index=0, ID=int(sys.argv[1]))
    trial.setup()


if __name__ == "__main__":
    main()

