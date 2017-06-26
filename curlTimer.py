#!/usr/bin/python
import subprocess
from decimal import *
import statistics
import argparse
from argparse import RawTextHelpFormatter
import sys

#sudo -H pip2 install statistics to get python3's statistics module

#Header on the help page
parser = argparse.ArgumentParser(description="----------Program-Help-Page----------", formatter_class=RawTextHelpFormatter)

#Inline Arguments
parser.add_argument("-v", help="The file containing the valid curl request \n")
parser.add_argument("-i", help="The file containing the invalid curl request \n")
parser.add_argument("-r", help="The amount of requests you would like to run (default=10) \n", type=int)

args = parser.parse_args()

#Ensures that the arguments are correctly provided
if args.v == None:
	print 'You forgot to select a file containing a valid curl request. \n Use -h to display the arguments.\n'
	exit()
if args.i == None:
	print 'You forgot to select a file containing an invalid curl request. \n Use -h to display the arguments.\n'
	exit()

#If -r isn't used, have a default of 10 requests
if args.r == None:
	default = int(10)
else:
	default = int(args.r) 

class req(object):
    def __init__(self, inputFile):
        originalRequest = self.openRequest(inputFile)
        injectedRequest = self.injectStatsScript(originalRequest)
        self.request = self.saveRequest('./requests/'+'mod'+inputFile,injectedRequest)
        self.results = {'lookup':[],'connect':[],'appCon':[],'redirect':[],'preXfer':[],'startXfer':[],'total':[]}

    def openRequest(self, inputFile):
        with open(inputFile, 'r') as request:
            return request.read()

    def injectStatsScript(self, request):
        statsString = "-w 'lookup\t%{time_namelookup}\nconnect\t%{time_connect}\nappCon\t%{time_appconnect}\nredirect\t%{time_redirect}\npreXfer\t%{time_pretransfer}\nstartXfer\t%{time_starttransfer}\ntotal\t%{time_total}' -o /dev/null "
        return request[:5] + statsString + request[5:]

    def saveRequest(self, filename, request):
        open(filename, 'w').write(request)
        return filename

    def convertTime(self, time): # convert time from string to int as its easier to do statistics
        return int(Decimal(time)*1000)

    def executeRequest(self):    # find a better way to execute curl requests?
        p = subprocess.Popen(['./caller.sh',self.request],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        data = p.communicate()[0]
        data = data.split('\n')
        data = [x.split('\t') for x in data]
        retval = {}                             #create dict of timings
        for x in data:
            retval[x[0]] = self.convertTime(x[1])
        self.updateResults(retval)

    def executeRequests(self, noOfCalls):
        for x in range(0, noOfCalls):
            self.executeRequest()

    def updateResults(self,resultsDict):
        self.results['lookup'].append(resultsDict['lookup'])
        self.results['connect'].append(resultsDict['connect'])
        self.results['appCon'].append(resultsDict['appCon'])
        self.results['redirect'].append(resultsDict['redirect'])
        self.results['preXfer'].append(resultsDict['preXfer'])
        self.results['startXfer'].append(resultsDict['startXfer'])
        self.results['total'].append(resultsDict['total'])

    def returnResults(self):
        return self.results

    '''
    def modifyRequest(request,key,replacement):
        return request[:request.index(key)] + replacement + request[request.index(key)+len(key):]
    '''

#--------------------------------------------------------------------------------------------------------#

valid = req(args.v)
valid.executeRequests(default)
print 'Average total connection time for valid account (ms): ', int(statistics.mean(valid.returnResults()['total']))
#Uncomment for individual requests
#print 'Individual Requests (ms): ', (str(valid.returnResults()['total']))

invalid = req(args.i)
invalid.executeRequests(default)
print 'Average total connection time for invalid account (ms): ', int(statistics.mean(invalid.returnResults()['total']))
#Uncomment for individual requests
#print 'Individual Requests (ms): ', (str(invalid.returnResults()['total']))
