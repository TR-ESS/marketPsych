# coding: utf-8

import sys
from scipy.stats.stats import pearsonr
import pandas as pd
import statsmodels.formula.api as sm
from sklearn import linear_model as lm
import numpy as np
import datetime as dt

argvals = sys.argv
arglen=len(argvals)
if (arglen != 2):
    print ('Usage: #python %s dirname' % argvals[0])
    quit()

filePath= argvals[1]
df = pd.read_csv(filePath, sep=',')
name=df.columns.values
print (name)

data1= df[name[0]] #RIC
data1len=len(data1)
data2 = df[name[1]] #Domain
data3 = df[name[2]] #DateTime
data4 = df[name[3]] #Type
data5 = df[name[4]] #Open
data6 = df[name[5]] #High
data7 = df[name[6]] #Low
data8 = df[name[7]] #Last


for ts in range(0,data1len):
    #    print (data1[ts])
    _dateTime1 = dt.datetime.strptime(data3[ts], '%Y-%m-%dT%H:%M:%S.000000000Z')
    _dateTime1 += dt.timedelta(hours=1)

    print (_dateTime1.strftime('%Y-%m-%dT%H:%M:%S.000Z') + ',' + data1[ts] + ',' + str(data5[ts]) + ',' + str(data6[ts]) + ',' + str(data7[ts]) + ',' + str(data8[ts]), flush=True)

