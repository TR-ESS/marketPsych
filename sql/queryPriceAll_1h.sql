#!/bin/sh

currencyList="JPY= EURJPY= GBPJPY= CHFJPY= AUDJPY= CADJPY= NZDJPY="
currencyTable=tickdb.tick_1h

platform=$1
dateBefore=`echo $2`
dateStart=`date +"%Y-%m-%dT%H:00:00.000Z" --date "$dateBefore"`
dataFrequency=1h

### CURRENCY QUERY
for line in $currencyList
do
    ./queryPrice.sql $platform $line $currencyTable $dateStart $dataFrequency
done



