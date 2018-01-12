# -*- coding: utf-8 -*-
import sys
from ftpControl import ftpControl

argvals = sys.argv
arglen = len(argvals)

if (arglen != 3):
    print ('Usage: #python %s ftpfilepath outfilename' % argvals[0])
    quit()

ftp =  ftpControl()
ftp.init("mrn-ftp.thomsonreuters.com", "8814854", "JDj4ZL260zJS62Ndkl6Pu")
# print(ftp.getParams())

ftp.login()
#ftp.chDir('/TRMI_LIVE/COU/WDAI_UHOU')
#ftp.chDir(argvals[1])
ftp.getFile(argvals[1], argvals[2])
ftp.closeSession()

