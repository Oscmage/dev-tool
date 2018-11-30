#!/usr/bin/python
import os
import sys
import json
from urllib.parse import quote
import requests
import subprocess


SCANNER_REPORT_PATH = "/.scannerwork/report-task.txt"
PROJECT_KEY = "projectKey="
SERVER_URL = "serverUrl="
QUERY = "&metrics=sqale_index%2Cduplicated_lines_density%2Cncloc%2Ccoverage%2Cbugs%2Ccode_smells%2Cvulnerabilities&ps=1000"
MEASURES = "/api/measures/search_history?component="

NORMAL_MODE = "NORMAL MODE"
STASH_MODE = "STASH MODE"
HELP = "HELP"


def main():
    cwd = os.getcwd()  # Current working directory
    mode = parseArguments()
    if mode:
        if mode == NORMAL_MODE:
            normal_mode(cwd)
        if mode == STASH_MODE:
            stash_mode(cwd)
        if mode == HELP:
            help()


def normal_mode(cwd):
    # Display difference from last run of sonar-scanner
    sonar_scanner_print_out(cwd)


def stash_mode(cwd):
    # Stash everything from new changes
    # Run sonar scanner to get previous result
    # Pop the new code
    cool_print("Stashing changes")
    subprocess.run(["git", "stash", "--all", "--include-untracked"])
    cool_print("Running sonar-scanner without new changes")
    subprocess.run(["sonar-scanner"])
    cool_print("Poping changes")
    subprocess.run(["git", "stash", "pop"])
    # Display difference for changes
    cool_print(
        "Run sonar scanner for second time to display difference with your changes")
    sonar_scanner_print_out(cwd)


def cool_print(to_print):
    print(bcolors.OKGREEN +
          "###########################################################" + bcolors.ENDC)
    print(bcolors.OKGREEN + to_print + bcolors.ENDC)
    print(bcolors.OKGREEN +
          "###########################################################" + bcolors.ENDC)


def sonar_scanner_print_out(cwd):
    # Blocking, wait until done
    subprocess.run(["sonar-scanner"])
    # Retrieve project key and base url which is used for quering the api
    projectKey, baseUrl = getProjectInfo(cwd)
    url = baseUrl + MEASURES + projectKey + QUERY
    r = requests.get(url)
    json_dict = r.json()
    print(display_history(get_history(json_dict, 'bugs'), 'bugs'))
    print(display_history(get_history(json_dict, 'code_smells'), 'code smells'))
    print(display_history(get_history(json_dict, 'vulnerabilities'), 'vulnerabilities'))


def display_history(history_list, measure):
    '''
    Expects a list of minimum len 2 and which is sorted with the most recent entry first.
    '''
    if len(history_list) < 2:
        return "There is no history for %s" % measure
    currentVal = int(history_list[0]['value'])
    previousVal = int(history_list[1]['value'])
    change = currentVal - previousVal
    changeText = "Changes with regards to %s since last time: " % measure
    if change > 0:
        return bcolors.FAIL + changeText + "+" + str(change) + bcolors.ENDC
    if change < 0:
        return bcolors.OKGREEN + changeText + "-" + str(change) + bcolors.ENDC
    return bcolors.OKGREEN + changeText + str(change) + bcolors.ENDC


def get_history(json_dict, measure):
    '''
    Retrieves the history for a specific measure eg: 'bugs' sorted by most recent date first.
    '''
    measures = json_dict['measures']
    for m in measures:
        if m['metric'] == measure:
            return sorted(m['history'], key=lambda elem: elem['date'], reverse=True)
    raise ValueError("Could not retrieve the measure: %s" % measure)


def getProjectInfo(cwd):
    # Retrieves the project key and the base url in encoded uri format
    scanner_report_path = cwd + SCANNER_REPORT_PATH
    projectKey = ""
    baseUrl = ""
    with open(scanner_report_path) as f:
        for line in f:
            if PROJECT_KEY in line:
                projectKey = line[len(PROJECT_KEY):].strip()
            elif SERVER_URL in line:
                baseUrl = line[len(SERVER_URL):].strip()
    if projectKey and baseUrl:
        return quote(projectKey), baseUrl
    raise ValueError("Could not retrieve projectKey or baseUrl from %s" %
                     scanner_report_path)


def writeResult(data):
    with open('db.json', 'w') as outfile:
        json.dump(data, outfile)


def parseArguments():
    argument = sys.argv[1]
    if argument:
        if argument == "-h":
            return HELP
        elif argument == "-gs":
            return STASH_MODE
        else:
            print("Unknown argument: %s" % argument)
            return ""
    else:
        return NORMAL_MODE


def help():
    print(bcolors.WARNING + "Running without any argument will compare to previous run. Another alternative is to run with the argument -gs which will stash your current changes and compare to the last commit. This assumes it's a git repository"
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
