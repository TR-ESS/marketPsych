# coding: utf-8

from trmiAnalytics import trmiAnalytics as ta
import sys
import os
import pandas as pd

### COMMAND ARGS VALIDATION
argvs=sys.argv
argc=len(argvs)
if argc != 6:
    print ('Usage: python %s config_file_path  sim_start_pos sim_span platform hidden_layer_size' % argvs[0])
    quit()
### INSTANCIATE ANALYTICS CLASS
asys = ta()
### LOAD CONFIG
confDF = asys.loadConfig(argvs[1],',')
emtModel = str(confDF['ml-model'][0])
emtMode = str(confDF['mode'][0])
emtAssetName = str(confDF['assetName'][0])
emtPositionFlag = int(confDF['positionFlag'][0])
emtNumDepth = int(confDF['numDepth'][0]) # for Decision Tree Only
emtActivationFunction = str(confDF['activationFunction'][0]) # MLP Only
emtSolver = str(confDF['solverName'][0]) # MLP Only
emtMaxInter = int(confDF['maxInter'][0]) # MLP Only

emtSupervisedSpan = int(argvs[3]) # SUPERVISING SPAN
emtStartPosition = int(argvs[2]) # STARTING FROM
emtPlatform = str(argvs[4])  # PLATFORM NAME GCP or AWS
emtHLS = int(argvs[5]) # Hidden Layer Size for MLP

if emtPlatform == "GCP":
    emtWindowTimestampFieldName = 'windowTimestamp'
    emtAssetCodeFieldName = 'assetCode_x'
else:
    emtWindowTimestampFieldName = 'windowtimestamp'
    emtAssetCodeFieldName = 'assetcode_x'

### LOAD TARGET ASSET PRICE (INITIAL)
emtAssetPricePath = '../../marketPsychData/sql/' + emtAssetName + '.price.sql'
emtPriceDF = asys.loadData2(emtAssetPricePath,',')
emtPriceLen = len(emtPriceDF)

### LOOK UP TRMI ASSET CODE
trmiGroup = ['JP', 'US', 'FR', 'GB', 'DE', 'CN', 'CA','CL', 'BR', 'AU', 'EG', 'IN', 'IR', 'IQ', 'IL', 'IT', 'LY', 'MX', 'KP', 'RU', 'ZA', 'CH', 'AR', 'UA']
#trmiGroup = ['JP']

### MAIN PROCESSING

corrArray = []
count = 0
accPL = 0
plArray = []

for i in range(emtPriceLen - emtStartPosition - emtSupervisedSpan + 1, emtPriceLen - emtSupervisedSpan + 1, emtSupervisedSpan):
    ### Copy Price Data in the range (current : current + dataSpan)
    priceDF = emtPriceDF[i:i + emtSupervisedSpan]
    priceFieldName = priceDF.columns.values

    ### IMPORTANT FOR LIVE MODE: CONTINUOUSLY FEED NEXT FEED and ADD NEWLY INCOMING PRICE INTO emtPriceDF
    if len(priceDF) != emtSupervisedSpan:
        print ("Continue for LIVE mode")

    ### LOAD TRMI DATA
    fwdCorrRanking = []

    for trmiAssetName in trmiGroup:
        trmiAssetNamePath = '../../marketPsychData/sql/' + trmiAssetName + '.trmi.sql'
        trmiDF = asys.loadData2(trmiAssetNamePath, ',')
        asys.setTrmiAsset(trmiAssetName)
        trmiFieldName = trmiDF.columns.values

        ### INNER JOIN B/W PRICE AND TRMI DATA USING "windowtimestamp" AS A MATCHING KEY
        mergedDF = pd.merge(priceDF, trmiDF, how='inner', on=[emtWindowTimestampFieldName])
        mergedPriceDF = mergedDF[[emtWindowTimestampFieldName, emtAssetCodeFieldName,'open','high','low','last']]
        mergedTrmiDF = mergedDF.drop([emtAssetCodeFieldName,'open','high','low','last'], axis=1)

        ### OBTAIN FORWARD LOOKING CORRELATION INDEX
        fwdCorrArr = []
        fwdCorrArr = asys.getForwardLookingCorr(mergedTrmiDF, mergedPriceDF, 5)
        fwdCorrRanking.extend(fwdCorrArr[0])

        #*** END OF LOOP : TRAVERSE trmiGroup

    ### SORTED BY POSITIVE CORRELATION
    CorrRanking = sorted(fwdCorrRanking, reverse=True)
    if len(CorrRanking) == 0:
        continue
    ### TOP 3 RANKED COUNTRY and ITS PSYCH INDICES
    country = []
    indexname = []
    for k in range(0,3):
        country.append(CorrRanking[k][1])
        indexname.append(CorrRanking[k][2].split('-')[1])

    ### LOAD TOP 3 RANKED TRMI ASSET DATA
    trmiIndices = []
    trmiNames = []
    for k in range(0,3):
        trmiTmpPath = '../../marketPsychData/sql/' + country[k] + '.trmi.sql'
        trmiTmp = asys.loadData2(trmiTmpPath,',')
        trmiIndices.append(trmiTmp)
        trmiNames.append(trmiTmp.columns.values)

    ### LOAD PRICE DATA : DURATION = LEARNING PERIOD + TESTING PERIOD
    sPriceDF = emtPriceDF[i:i + (2 * emtSupervisedSpan)]

    ### INNER JOIN B/W sPriceDF and trmiIndices by "windowtimestamp" as matching KEY
    sMergedDF0 = pd.merge(sPriceDF, trmiIndices[0], how='inner', on=[emtWindowTimestampFieldName])
    sMergedDF1 = pd.merge(sPriceDF, trmiIndices[1], how='inner', on=[emtWindowTimestampFieldName])
    sMergedDF2 = pd.merge(sPriceDF, trmiIndices[2], how='inner', on=[emtWindowTimestampFieldName])

    sMergedPriceDF0 = sMergedDF0[[emtWindowTimestampFieldName, emtAssetCodeFieldName,'open','high','low','last']]
    sMergedTrmiDF0 = sMergedDF0.drop([emtAssetCodeFieldName,'open','high','low','last'], axis=1)
    sMergedPriceDF1 = sMergedDF1[[emtWindowTimestampFieldName, emtAssetCodeFieldName,'open','high','low','last']]
    sMergedTrmiDF1 = sMergedDF1.drop([emtAssetCodeFieldName,'open','high','low','last'], axis=1)
    sMergedPriceDF2 = sMergedDF2[[emtWindowTimestampFieldName, emtAssetCodeFieldName,'open','high','low','last']]
    sMergedTrmiDF2 = sMergedDF2.drop([emtAssetCodeFieldName,'open','high','low','last'], axis=1)

    ### MACHINE LEARNING STUDYING PHASE
    studyPriceDF = sMergedPriceDF0[0:emtSupervisedSpan]
    studyTrmiDF0 = sMergedTrmiDF0[0:emtSupervisedSpan][indexname[0]]
    studyTrmiDF1 = sMergedTrmiDF1[0:emtSupervisedSpan][indexname[1]]
    studyTrmiDF2 = sMergedTrmiDF2[0:emtSupervisedSpan][indexname[2]]

    ### DEBUG
    print ('---> PRICE ARRAY FOR ML = ' + str(studyPriceDF[emtWindowTimestampFieldName][emtSupervisedSpan-1]) + '   ' + str(studyPriceDF['last'][emtSupervisedSpan-1]))

    ret = 0
    if emtModel == "DT":
        ret = asys.getSupervisingDTData(studyPriceDF,studyTrmiDF0,studyTrmiDF1,studyTrmiDF2,emtNumDepth,emtPositionFlag)
    elif emtModel == "MLP":
        ret = asys.getSupervisingMLPData(studyPriceDF,studyTrmiDF0,studyTrmiDF1,studyTrmiDF2,emtActivationFunction,emtSolver,emtMaxInter,emtPositionFlag, emtHLS)

    else:
        print ("no action taken........., skip machine learnig because of wrong model name in config")
        continue

    lastTradePrice = sMergedPriceDF0.iloc[emtSupervisedSpan - 1]['last']
    nextTradePrice = sMergedPriceDF0.iloc[emtSupervisedSpan]['last']

    lastWindowTime = sMergedPriceDF0.iloc[emtSupervisedSpan - 1][emtWindowTimestampFieldName]
    nextWindowTime = sMergedPriceDF0.iloc[emtSupervisedSpan][emtWindowTimestampFieldName]

    pl = (nextTradePrice - lastTradePrice) * ret
    accPL = accPL + pl
    print (nextWindowTime + ':' + str(accPL[0]) + ':' + str(nextTradePrice), flush=True)
    ### WRITE PL RESULT INTO CSV FILE
    plSubArray = []
    if emtPlatform == "GCP":
        plSubArray.append(str(nextWindowTime)[0:10] + ' ' + str(nextWindowTime)[10:18])
    else:
        plSubArray.append(str(nextWindowTime)[0:10] + ' ' + str(nextWindowTime)[11:19])
    plSubArray.append(ret[0])
    plSubArray.append(pl[0])
    plSubArray.append(accPL[0])
    plSubArray.append(nextTradePrice)
    plSubArray.append(country[0])
    plSubArray.append(indexname[0])
    plArray.append(plSubArray)

    ### TEST MODEL
    priceLen = len(sPriceDF)
    for x in range(emtSupervisedSpan,priceLen - 1):
        studyPriceDF = sMergedPriceDF0[0:x+1]
        studyTrmiDF0 = sMergedTrmiDF0[0:x+1][indexname[0]]
        studyTrmiDF1 = sMergedTrmiDF1[0:x+1][indexname[1]]
        studyTrmiDF2 = sMergedTrmiDF2[0:x+1][indexname[2]]

        ret = 0
        if emtModel == "DT":
            ret = asys.getSupervisingDTData(studyPriceDF,studyTrmiDF0,studyTrmiDF1,studyTrmiDF2,emtNumDepth,emtPositionFlag)
        elif emtModel == "MLP":
            ret = asys.getSupervisingMLPData(studyPriceDF,studyTrmiDF0,studyTrmiDF1,studyTrmiDF2,emtActivationFunction,emtSolver,emtMaxInter,emtPositionFlag, emtHLS)
        else:
            print ('no model')

        lastTradePrice = sMergedPriceDF0.iloc[x]['last']
        nextTradePrice = sMergedPriceDF0.iloc[x+1]['last']

        lastWindowTime = sMergedPriceDF0.iloc[x][emtWindowTimestampFieldName]
        nextWindowTime = sMergedPriceDF0.iloc[x+1][emtWindowTimestampFieldName]

        pl = (nextTradePrice - lastTradePrice) * ret
        accPL = accPL + pl
        print (nextWindowTime + ':' + str(accPL[0]) + ':' + str(nextTradePrice), flush=True)

        ### WRITE PL RESULT INTO CSV FILE
        plSubArray = []
        if emtPlatform == "GCP":
            plSubArray.append(str(nextWindowTime)[0:10] + ' ' + str(nextWindowTime)[10:18])
        else:
            plSubArray.append(str(nextWindowTime)[0:10] + ' ' + str(nextWindowTime)[11:19])
        plSubArray.append(ret[0])
        plSubArray.append(pl[0])
        plSubArray.append(accPL[0])
        plSubArray.append(nextTradePrice)
        plSubArray.append(country[0])
        plSubArray.append(indexname[0])
        plArray.append(plSubArray)


### PL ATTRIBUTE
profit = 0
loss = 0
for i in range(0,len(plArray)):
    if plArray[i][1] > 0:
        profit = profit + 1
    elif plArray[i][1] < 0:
        loss = loss + 1

winRate = (profit / (profit + loss)) * 100
print ('Winning Rate = ' + str(winRate))

outDF = pd.DataFrame(plArray,columns=['timeStamp','signal','pl','accPL','lastPrice','country','index'])
outFileName = '../../marketPsychData/ret/' + emtAssetName + '.' + emtModel + '.' + str(emtPositionFlag) + '.' + str(emtNumDepth) + '.' + emtActivationFunction + '.' + emtSolver + '.' + str(emtMaxInter) + '.' + str(emtStartPosition) + '.' + str(emtSupervisedSpan) + '.csv'

coverFileName = '../../marketPsychData/ret/' + emtAssetName + '.' + emtModel + '.csv'


outDF.to_csv(outFileName, index=False)
outDF.to_csv(coverFileName, index=False)

avrPL=outDF.mean()['pl']
stdevPL=outDF.std()['pl']
sharpRatio=(avrPL /  stdevPL) * 100
print ('Sharp Ratio = ' + str(sharpRatio))

performanceFileName = '../../marketPsychData/ret/' + emtAssetName + '.' + emtModel + '.pfm.csv'
pfmArray = []
pfmArray.append(winRate)
pfmArray.append(sharpRatio)

pArray = []
pArray.append(pfmArray)
pfmDF = pd.DataFrame(pArray, columns=['winRate', 'sharpRatio'])
pfmDF.to_csv(performanceFileName, index=False)


