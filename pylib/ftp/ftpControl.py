# -*- coding: utf-8 -*-

from ftplib import FTP

class ftpControl:
    def __init__(self):
        self.hostname = ''
        self.username = ''
        self.password = ''

    def init(self,host,user,pw):
        self.hostname = host
        self.username = user
        self.password = pw

    def getParams(self):
        _retStr = self.hostname + ':' + self.username + ':' + self.password
        return _retStr

    def login(self):
        self.ftp = FTP(self.hostname)
        self.ftp.login(self.username, self.password)

    def chDir(self, target):
        self.ftp.cwd(target)

    def listFiles(self):
        return self.ftp.retrlines('LIST')

    def getFile(self, infilepathname, outfilepathname):
        _file = open(outfilepathname, 'wb')
        _cmd = 'RETR ' + infilepathname
        self.ftp.retrbinary(_cmd, _file.write)
        _file.close()

    def closeSession(self):
        self.ftp.quit()
