#!/bin/sh
bq query -n 1000000 \
"select * from trmidb.cmpny_grp_1h  where dataType='News_Social'  and assetCode='MPTRXJP225'  and windowTimestamp >  '2012-01-01T00:00:00.000Z'  order by windowTimestamp"
