# coding: utf-8
import os
import sys
import time
import pandas as pd
import argparse

from  trthRest import trthRestFeed as trf
from timestampCtl import timestampCtl as tmc

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
    uFrom=str(confDF['from'][0])
    uTo=str(confDF['to'][0])
    uInterval=str(confDF['interval'][0])
    uOutput=str(confDF['output'][0])
    uFields=str(confDF['fields'][0]).replace('[','').replace(']','')
    uGmtOffset=int(confDF['gmtOffset'][0])
else:
    print ('Configuration : ' + argvs[1] + ' not exist.')
    quit()

# uFields='"Open","High","Low","Last"'
tf=trf()
##### 9 HOURS TIME SHIFT
tm=tmc()
uFrom2=tm.timeShift(uFrom,0) #uGmtOffset+1)
uTo2=tm.timeShift(uTo,0) #uGmtOffset+2)
if uFrom2 != '' and uTo2 != '':
    uFrom = uFrom2
    uTo = uTo2

print ('***Time Period From ' + uFrom + ' To ' + uTo)
print ('***Expected Fields ==> ' + uFields)

##### CREATE AUTHENTIFICATION TOKENprint (uName)
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




