from paxos import Paxos
from PRM import PRM
from cli import cli
import sys

def main():
    trial = cli()
    trial.setup()


if __name__ == "__main__":
    main()