#!/bin/sh
listAssetConf="C.conf S.conf W.conf BADI.conf VIX.conf CRB.conf JPY.conf EURJPY.conf"
cd $HOME/marketPsych/feed/price


count=0
for line in $listAssetConf
do
    confPath="$HOME/marketPsychConf/trth/$line"
    echo $confPath

    ./trthFeed.sh $confPath &> $HOME/marketPsychData/applog/$line.log &
done
