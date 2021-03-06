# -*- coding: utf-8 -*-
import sys
import os
import time
import pandas as pd

from ftpControl import ftpControl

argvals = sys.argv
arglen = len(argvals)

if (arglen != 4):
    print ('Usage: #python %s ftpfilepath outfilename configfile' % argvals[0])
    quit()

if os.path.exists(argvals[3]) == False:
    print ('Config %s not exist' % (argvals[3]))
    quit()

fdf=pd.read_csv(argvals[3],':')
uName=str(fdf['userID'][0])
pWord=str(fdf['Password'][0])
ftpServer=str(fdf['server'][0])


ftp =  ftpControl()
ftp.init(ftpServer, uName, pWord)

ret=ftp.login()
while ret == 'NG':
    time.sleep(60)
    print ('..... doFTP, login,  waiting for login')
    ret=ftp.login()


ret=ftp.getFile(argvals[1], argvals[2])
while ret == 'NG':
    time.sleep(60)
    print ('..... doFTP, getfile, waitinng for login')
    ftp.closeSession()
    ret=ftp.login()
    ret=ftp.getFile(argvals[1], argvals[2])

ftp.closeSession()


