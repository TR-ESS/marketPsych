# -*- coding: utf-8 -*-

import sys
import os
import datetime

dnow=datetime.datetime.now()
dnow+=datetime.timedelta(hours=-1)
dpast=dnow+datetime.timedelta(hours=-23)

print (dpast.strftime('%Y-%m-%dT%H:00:00.000Z'))
print (dnow.strftime('%Y-%m-%dT%H:59:59.000Z'))
