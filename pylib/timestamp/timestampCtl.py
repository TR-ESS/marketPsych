# coding: utf-8

import sys
import os
import datetime


class timestampCtl:
    def timeShift(self,inTimestamp,hours):
        try:
            dt=datetime.datetime.strptime(inTimestamp, '%Y-%m-%dT%H:%M:%S.000Z')
            dt+=datetime.timedelta(hours=hours)
            return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        except:
            return ''
