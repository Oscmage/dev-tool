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


def main():
    cwd = os.getcwd()  # Current working directory
    handleArguments()

    # Blocking, wait until done
    subprocess.run(["sonar-scanner"])
    # Retrieve project key and base url which is used for quering the api
    projectKey, baseUrl = getProjectInfo(cwd)
    url = baseUrl + MEASURES + projectKey + QUERY
    r = requests.get(url)
    json_dict = r.json()
    print(displayHistory(getHistory(json_dict, 'bugs'), 'bugs'))
    print(displayHistory(getHistory(json_dict, 'code_smells'), 'code smells'))


def displayHistory(history_list, measure):
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


def getHistory(json_dict, measure):
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


def handleArguments():
    argument = sys.argv[1]
    if argument:
        if argument == "-h":
            help()
        else:
            print("Unknown argument: %s" % argument)


def help():
    print(bcolors.WARNING + "This is how you use the dev tool herpa derp."
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
