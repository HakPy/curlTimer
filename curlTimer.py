import subprocess
from decimal import *
import statistics

#sudo -H pip2 install statistics to get python3's statistics module

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

valid = req('validReq')
valid.executeRequests(10)
print 'Average total connection time for valid account (ms): ', int(statistics.mean(valid.returnResults()['total']))
#Uncomment for individual requests
#print (str(valid.returnResults()['total']))

invalid = req('invalidReq')
invalid.executeRequests(10)
print 'Average total connection time for inavlaid account (ms): ', int(statistics.mean(invalid.returnResults()['total']))
#Uncomment for individual requests
#print (str(invalid.returnResults()['total']))
