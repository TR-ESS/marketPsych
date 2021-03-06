# coding: utf-8 -*-
import http.client
import json
import os
import sys
import time
import codecs
import shutil
import gzip
import pandas as pd
from io import StringIO

##########
# Tick History Version 2 User Authentification
# Purpose: get Authentification "Value" for further request
# Author: Noriyuki Suzuki / Market Development Manager / Thomson Reuters
##########

conn = http.client.HTTPSConnection("hosted.datascopeapi.reuters.com")
username="9010288"
password="Anglers01"
payload2='{"Credentials":{"Username":"%s","Password":"%s"}}' % (username, password)
headers2 = {
    'prefer': "respond-async",
    'content-type': "application/json",
    'cache-control': "no-cache"
    }
print (headers2)
conn.request("POST", "/RestApi/v1/Authentication/RequestToken", payload2, headers2)

res = conn.getresponse()
print ("User Authentification Status:" + str(res.status))
data = res.read()
json_dict=json.loads(data.decode("utf-8"))
try:
    uAuthValue=json_dict['value']
except KeyError:
    print(str(json_dict['error']))
    sys.exit()
print ("User Authentification Value ==> : " + str(uAuthValue))

##########
# Tick History v2 Request Intraday History
# Author: Noriyuki Suzuki / Market Development Manager / Thomson Reuters

ric="JNIc1"
start="1998-01-01T00:00:00.000Z"
end="2007-12-31T23:59:59.000Z"

payload2='{"ExtractionRequest":{"@odata.type":"#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TickHistoryIntradaySummariesExtractionRequest","ContentFieldNames":["Open","High","Low","Last","Open Bid","High Bid","Low Bid"],"IdentifierList":{"@odata.type":"#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList","InstrumentIdentifiers":[{"Identifier":"%s","IdentifierType": "Ric"}],"ValidationOptions":null,"UseUserPreferencesForValidationOptions":false},"Condition":{"MessageTimeStampIn":"GmtUtc","ReportDateRangeType":"Range","QueryStartDate":"%s","QueryEndDate":"%s","SummaryInterval":"OneHour","TimebarPersistence":true,"DisplaySourceRIC":true}}}' % (ric,start,end)

#print (payload2)
headers2={}
headers2['prefer'] = "respond-async"
headers2['content-type'] = "application/json"
headers2['authorization'] = "Token " + str(uAuthValue)
headers2['cache-control'] = "no-cache"

#print (headers2)

conn.request("POST", "/RestApi/v1/Extractions/ExtractRaw", payload2, headers2)

res = conn.getresponse()
data = res.read() ### IMPORTANT FOR NEXT REQUEST INSTRUCTION
print ("OnDemand Request Status:" + str(res.status))
resheader=res.getheaders()
locationUrl=''

for i in range(0,len(resheader)):
    if str(resheader[i][0]) == 'Location':
        locationUrl=resheader[i][1]


locationUrl2 = locationUrl.split('hosted.datascopeapi.reuters.com')[1]
print (str(locationUrl2))

############
# Get JOB Status
############
conn.request("GET",str(locationUrl2), headers=headers2)
time.sleep(15)
res = conn.getresponse()
data = res.read()
print("Status Query:" + str(res.status))
while (res.status == 202):
    time.sleep(30)
    conn.request("GET",locationUrl, headers=headers2)
    res = conn.getresponse()
    data = res.read()

if res.status == 200:
    print ("Data Ready")
    #data=res.read()
    json_dict=json.loads(data.decode("utf-8"))
    jobid=''
    jobid=json_dict['JobId']
    print ("JOB ID ==>: " + str(jobid))

    ######
    # GET ACTUAL DATA
    ######
    headers2={}
    headers2['prefer'] = "respond-async"
    headers2['content-type'] = "text/plain"
    headers2['Accept-Encoding'] = "gzip"
    headers2['authorization'] = "Token " + str(uAuthValue)
    headers2['cache-control'] = "no-cache"

    localUrl2 = "/RestApi/v1/Extractions/RawExtractionResults('" + str(jobid) + "')/$value"
    print ("END POINT ==>:" + localUrl2)
    conn.request("GET", localUrl2, headers=headers2)
    res = conn.getresponse()
    data = res.read()
    #uncompressedData = gzip.decompress(data).decode('utf-8')
    #print (uncompressedData)
    ##########
    # DATA UNCOMPRESS
    ##########
    fileName='./dataRet.csv.gz'
    with open(fileName, 'wb') as fd:
        fd.write(data)
    fd.close()

    uncompressedData=''
    with gzip.open(fileName, 'rb') as fd:
        for line in fd:
            dataLine = line.decode('utf-8')
            uncompressedData = uncompressedData + dataLine
    fd.close()

    tmseries = pd.read_csv(StringIO(uncompressedData))
    print (tmseries)
    
    csvName='./dataRet.csv'
    tmseries.to_csv(csvName, index=False)






