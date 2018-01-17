# coding: utf-8
## Thomson Reuters Tick History Version 2 download with Rest API
# 2018 01 09
# Noriyuki Suzuki / Market Development Manager / Thomson Reuters
# Class : trthRestFeed

import os
import sys
import time
import codecs
import gzip

import http.client
import json
import pandas as pd
from io import StringIO



class trthRestFeed:
    ##### CONSTRUCTOR
    def __init__(self):
        self.uAuthKey = ''
        self.uName = ''
        self.uPassword = ''
        self.uJobID = ''
        self.uRootUrl = 'hosted.datascopeapi.reuters.com'
        self.localUrl=''
        self.outputName=''
        self.uFields=[]

    # *** METHOD DEFINITION
    ##### INITIALIZER
    ##### Creating Http.Client session and Obtain Authentification Key thru logon process
    def init(self, userName, userPassword, userRootUrl):
        if userRootUrl != '':
            self.uRootUrl = userRootUrl

        _headers={}
        _headers['prefer'] = 'respond-async'
        _headers['content-type'] = 'application/json'
        _headers['cache-control'] = 'no-cache'

        _payload=''
        _payload='{"Credentials":{"Username":"%s","Password":"%s"}}' % (userName, userPassword)

        ### TRYING TO CREATE HTTPS CLIENT SESSION
        try:
            self.conn = http.client.HTTPSConnection(self.uRootUrl)
        except:
            print ('***HTTPS Connection Error on ' + self.uRootUrl)
            return ''

        ### TRYING TO REQUEST USER AUTH KEY (TOKEN)
        try:
            self.conn.request('POST', '/RestApi/v1/Authentication/RequestToken', _payload,_headers)
            res = self.conn.getresponse()
            data=res.read()
        except:
            print ('***Request User Auth TOKEN Error : status = ' + str(res.status))
            return ''

        json_dict=json.loads(data.decode('utf-8'))
        try:
            self.uAuthKey=json_dict['value']
        except KeyError:
            print ('***Request User Auth TOKEN Error: ' + str(json_dict['error']['message']))
            return ''

        return self.uAuthKey

    # *** METHOD DEFINITION
    ##### REQUEST TICK HISTORY
    ##### Posting tick history request parameterse onto end point
    def reqIntradayBars(self,ricCode,fromDate,toDate,interval, fields):
        if self.uAuthKey == '':
            print ('***ReqIntradayBars, Token empty')
            return ''
        if fields == '':
            print ('***ReqIntradayBars, Fields empty')
            return ''

        ### CREATE FIELD ARRAY
        _fields = fields.replace('"','')
        self.uFields=_fields.split(',')
        print ('***** DEBUG FIELD NAME = ' + str(self.uFields))

        _headers={}
        _headers['prefer'] = 'respond-async'
        _headers['content-type'] = 'application/json'
        _headers['authorization'] = 'Token ' + str(self.uAuthKey)
        _headers['cache-control'] = 'no-cache'

        _payload='{"ExtractionRequest":{"@odata.type":"#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TickHistoryIntradaySummariesExtractionRequest","ContentFieldNames":[%s],"IdentifierList":{"@odata.type":"#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList","InstrumentIdentifiers":[{"Identifier":"%s","IdentifierType": "Ric"}],"ValidationOptions":null,"UseUserPreferencesForValidationOptions":false},"Condition":{"MessageTimeStampIn":"GmtUtc","ReportDateRangeType":"Range","QueryStartDate":"%s","QueryEndDate":"%s","SummaryInterval":"%s","TimebarPersistence":true,"DisplaySourceRIC":true}}}' % (fields,ricCode,fromDate,toDate,interval)

        self.conn.request('POST', '/RestApi/v1/Extractions/ExtractRaw', _payload, _headers)
        res=self.conn.getresponse()
        data=res.read()
        header=res.getheaders()
        
        for i in range(0,len(header)):
            if str(header[i][0]) == 'Location':
                self.localUrl=header[i][1]
        if self.localUrl != '':
            return self.localUrl.split(self.uRootUrl)[1]
        else:
            return ''

    # *** METHOD DEFINITION
    ##### getStateOfIntradayBars
    ##### looping until dataset is ready on TickHistory Server
    def getStateOfIntradayBars(self):
        _headers={}
        _headers['prefer'] = 'respond-async'
        _headers['content-type'] = 'application/json'
        _headers['authorization'] = 'Token ' + str(self.uAuthKey)
        _headers['cache-control'] = 'no-cache'

        self.conn.request('GET',str(self.localUrl),headers=_headers)
        res=self.conn.getresponse()
        data=res.read()
        while(res.status == 202):
            print ('..... Waiting for data ready on TickHist Service.')
            time.sleep(60)
            self.conn.request('GET',str(self.localUrl),headers=_headers)
            res=self.conn.getresponse()
            data=res.read()

        if res.status == 200:
            json_dict=json.loads(data.decode('utf-8'))
            self.uJobID=json_dict['JobId']
        return self.uJobID

    # *** METHOD DEFINITION
    ##### getIntradayBarsData
    #####
    def getIntradayBarsData(self,outputName):
        if self.uJobID == '':
            return ''
        _headers={}
        _headers['prefer'] = "respond-async"
        _headers['content-type'] = "text/plain"
        _headers['Accept-Encoding'] = "gzip"
        _headers['authorization'] = "Token " + str(self.uAuthKey)
        _headers['cache-control'] = "no-cache"

        _localUrl="/RestApi/v1/Extractions/RawExtractionResults('" + str(self.uJobID) + "')/$value"
        self.conn.request('GET',_localUrl,headers=_headers)
        res=self.conn.getresponse()
        data=res.read()
        _fileName='./' + outputName + '.gz'
        with open(_fileName, 'wb') as fd:
            fd.write(data)
        fd.close()

        _uncompressedData=''

        with gzip.open(_fileName, 'rb') as fd:
            for line in fd:
                dataLine = line.decode('utf-8')
                _uncompressedData = _uncompressedData + dataLine
        fd.close()
        tmseries = pd.read_csv(StringIO(_uncompressedData))
        #for i in range(0,len(self.uFields)):
        #    _shiftColName='s' + str(self.uFields[i])
        #    tmseries[_shiftColName] = tmseries[str(self.uFields[i])].shift(0)
        tmseries=tmseries.dropna()
        print (tmseries)
    
        _fileName='./' + outputName
        tmseries.to_csv(_fileName, index=False)

    # *** METHOD DEFINITION
    ##### getIntradayBarsData
    #####
    def getIntradayBarsData2(self,outputName):
        if self.uJobID == '':
            return ''
        _headers={}
        _headers['prefer'] = "respond-async"
        _headers['content-type'] = "text/plain"
        _headers['Accept-Encoding'] = "gzip"
        _headers['authorization'] = "Token " + str(self.uAuthKey)
        _headers['cache-control'] = "no-cache"

        _localUrl="/RestApi/v1/Extractions/RawExtractionResults('" + str(self.uJobID) + "')/$value"
        self.conn.request('GET',_localUrl,headers=_headers)
        res=self.conn.getresponse()
        data=res.read()
        _fileName='./' + outputName + '.gz'
        with open(_fileName, 'wb') as fd:
            fd.write(data)
        fd.close()

        _uncompressedData=''

        with gzip.open(_fileName, 'rb') as fd:
            for line in fd:
                dataLine = line.decode('utf-8')
                _uncompressedData = _uncompressedData + dataLine
        fd.close()
        tmseries = pd.read_csv(StringIO(_uncompressedData))
        tmseries = tmseries.rename(columns={'#RIC':'assetCode','Date-Time':'windowTimestamp','Open Bid':'Open','High Bid':'High','Low Bid':'Low','Close Bid':'Last'})
        if 'Alias Underlying RIC' in tmseries:
            tmseries = tmseries.drop(['Alias Underlying RIC','Domain','GMT Offset','Type'],axis=1)
        else:
            tmseries = tmseries.drop(['Domain','GMT Offset','Type'],axis=1)
        #for i in range(0,len(self.uFields)):
        #    _shiftColName='s' + str(self.uFields[i])
        #    tmseries[_shiftColName] = tmseries[str(self.uFields[i])].shift(0)
        tmseries=tmseries.dropna()
        print (tmseries)
    
        _fileName='./' + outputName
        tmseries.to_csv(_fileName, index=False)




        

