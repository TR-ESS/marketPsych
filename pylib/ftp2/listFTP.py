# -*- coding: utf-8 -*-
import sys
import os
import time
import pandas as pd

from ftpControl import ftpControl

argvals = sys.argv
arglen = len(argvals)

if (arglen != 3):
    print ('Usage: #python %s dirname configfile' % argvals[0])
    quit()

if os.path.exists(argvals[2]) == False:
    print ('Config %s not exist' % (argvals[2]))
    quit()

fdf=pd.read_csv(argvals[2],':')
uName=str(fdf['userID'][0])
pWord=str(fdf['Password'][0])
ftpServer=str(fdf['server'][0])

ftp =  ftpControl()
ftp.init(ftpServer, uName, pWord)



ret=ftp.login()
while ret == 'NG':
    time.sleep(60)
    ret=ftp.login()

ret = ftp.chDir(argvals[1])
while ret == 'NG':
    time.sleep(60)
    ftp.closeSession()
    ret=ftp.login()
    ret = ftp.chDir(argvals[1])

ret = ftp.listFiles()
while ret == 'NG':
    time.sleep(60)
    ftp.closeSession()
    ret=ftp.login()
    ret = ftp.chDir(argvals[1])
    ret = ftp.listFiles()

    
ftp.closeSession()

