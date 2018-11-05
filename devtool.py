#!/usr/bin/python
import os
import sys
import json


def main():
    cwd = os.getcwd()
    handleArguments()
    data = readDb()
    print(data)

    # Get previous result from sonar-scanner
    # Run sonar-scanner with new code
    # Display simple comparison


def writeResult(data):
    with open('db.json', 'w') as outfile:
        json.dump(data, outfile)


def readDb():
    try:
        with open('db.json', 'r') as f:
            return json.load(f)
    except OSError:
        # Do nothing
        print(bcolors.WARNING + "If this is not the first time running the super-mega-devtool on this project something went wrong" + bcolors.ENDC)
        return {}


def handleArguments():
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
