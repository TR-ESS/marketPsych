#!/bin/sh
bq query -n 1000000 \
"select * from tickdb.tick_1d  where assetCode='NZDJPY='  and date(windowTimestamp) >  '2012-01-01'  order by windowTimestamp"
