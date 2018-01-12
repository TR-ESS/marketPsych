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
        try:
            self.ftp = FTP(self.hostname)
            self.ftp.login(self.username, self.password)
        except:
            return 'NG'
        return 'OK'

    def chDir(self, target):
        try:
            self.ftp.cwd(target)
        except:
            return 'NG'
        return 'OK'

    def listFiles(self):
        try:
            self.retobj = self.ftp.retrlines('LIST')
        except:
            return 'NG'
        return 'OK'

    def getListFiles(self):
        return self.retobj

    def getFile(self, infilepathname, outfilepathname):
        try:
            _file = open(outfilepathname, 'wb')
            _cmd = 'RETR ' + infilepathname
            self.ftp.retrbinary(_cmd, _file.write)
            _file.close()
        except:
            return 'NG'
        return 'OK'

    def closeSession(self):
        try:
            self.ftp.quit()
        except:
            return True
        return True

