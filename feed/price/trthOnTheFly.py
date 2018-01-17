# coding: utf-8
import os
import sys
import time
import pandas as pd
import argparse
import datetime

from  trthRest import trthRestFeed as trf
from timestampCtl import timestampCtl as tmc

##### RANGE SPECIFY
dnow=datetime.datetime.now()
dnow+=datetime.timedelta(hours=-1)
dpast=dnow+datetime.timedelta(hours=-119)

print (dpast.strftime('%Y-%m-%dT%H:00:00.000Z'))
print (dnow.strftime('%Y-%m-%dT%H:59:59.000Z'))

fromDateTime=dpast.strftime('%Y-%m-%dT%H:00:00.000Z')
toDateTime=dnow.strftime('%Y-%m-%dT%H:59:59.000Z')

##### MAIN ARGUMENTS IN CONFIGURATION
uName=''
uPassword=''
uUrl=''
uRic=''
uFrom=''
uTo=''
uInterval=''
uOutput=''
##### COMMAND ARGUMANE MANAGEMENT
argvs=sys.argv
argc=len(argvs)
if argc != 2:
    print ('Usage: python %s config_file_path' % argvs[0])
    quit()
##### VERIFY CONFIGURATION PATH EXISTENCE
if os.path.exists(argvs[1]):
    confDF = pd.read_csv(argvs[1],'|')
    uName=str(confDF['userName'][0])
    uPassword=str(confDF['userPassword'][0])
    uUrl=str(confDF['rootUrl'][0])
    uRic=str(confDF['ric'][0])
    uInterval=str(confDF['interval'][0])
    uOutput=str(confDF['output'][0])
    uFields=str(confDF['fields'][0]).replace('[','').replace(']','')
    uGmtOffset=int(confDF['gmtOffset'][0])
else:
    print ('Configuration : ' + argvs[1] + ' not exist.')
    quit()

uFrom = fromDateTime
uTo = toDateTime

print ('***Time Period From ' + uFrom + ' To ' + uTo)
print ('***Expected Fields ==> ' + uFields)

##### CREATE AUTHENTIFICATION TOKENprint (uName)
tf=trf()
authKey=tf.init(uName,uPassword,uUrl)
if authKey == '':
    sys.exit(-1)
print (authKey)
##### REQUEST TRTH
statUrl=tf.reqIntradayBars(uRic,uFrom,uTo,uInterval, uFields)
if statUrl == '':
    sys.exit(-1)
print (statUrl)
##### WAITING FOR DATA READY
jobID=tf.getStateOfIntradayBars()
if jobID == '':
    sys.exit(-1)
print (jobID)
##### GET DATA
tf.getIntradayBarsData2(uOutput)




