#!/usr/bin/python
import os
import sys


def main():
    cwd = os.getcwd()
    argument = sys.argv[1]

    if argument:
        if argument == "-h":
            help()
        else:
            print("Unknown argument: %s" % argument)


def help():
    print(bcolors.WARNING + "Testest test test test"
          + bcolors.ENDC)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == "__main__":
    main()
