#!/usr/bin/env python3
from PRM import PRM
import sys

def main():
    print(sys.argv)
    trial = PRM(ID=int(sys.argv[1]))
    trial.setup()


if __name__ == "__main__":
    main()
