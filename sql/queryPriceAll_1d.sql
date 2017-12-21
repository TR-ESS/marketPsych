#!/bin/sh

currencyList="JPY= EURJPY= GBPJPY= CHFJPY= AUDJPY= CADJPY= NZDJPY="
currencyTable=tickdb.tick_1d

platform=$1
dateBefore=`echo $2`
dateStart=`date +"%Y-%m-%d" --date "$dateBefore"`
dataFrequency=1d

### CURRENCY QUERY
for line in $currencyList
do
    ./queryPrice.sql $platform $line $currencyTable $dateStart $dataFrequency
done



