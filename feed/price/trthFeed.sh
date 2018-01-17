#!/bin/sh

confPath=$1
if [ ! -e $confPath ]; then
    echo "Config file $confPath not found"
    exit
fi
outFile=`awk -F'|' 'NR==2 {print $8}' $confPath`


cd $HOME/marketPsych/feed/price

if [ ! -e ./$outFile.prev ]; then
    touch ./$outFile.prev
fi

while true
do
    python ./trthOnTheFly.py $confPath
    headerRec=`awk 'NR==1 {print}' $outFile`
    diff ./$outFile.prev ./$outFile > ./diff.$outFile
    grep ">" ./diff.$outFile | grep -v "#RIC" | cut -c 3- > ./transfer.$outFile.0
    numDiff=`wc -l ./transfer.$outFile.0 | awk '{print $1}'`
    if [ "$numDiff" != "0" ]; then
	cat ./transfer.$outFile.0 >> toFeed.$outFile
    fi
    cp ./$outFile ./$outFile.prev
    sleep 300
done
