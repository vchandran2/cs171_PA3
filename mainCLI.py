#!/usr/bin/env python3
from cli import cli
import sys

def main():
    trial = cli(int(sys.argv[1]))
    trial.setup()



if __name__ == "__main__":
    main()
