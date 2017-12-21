#!/bin/sh

countryList="JP US CN CA CL BR AU EG FR DE GR IN IR IQ IL IT LY MX KP RU ZA CH GB AR UA SA"
countryTable=trmidb.cou_1d

currencyList="JPY USD EUR GBP CNY AUD BRL CAD AUD NZD RUB ZAR CHF"
currencyTable=trmidb.cur_1d

agrList="COF COR COT HOGS ORJ POIL SOY1 SUG WHT CTTL"
agrTable=trmidb.com_agr_1d

enmList="CPPR CRU MOG HOIL NAP NGS GOL NKL PLAT PALL STEE SLVR BIOETH"
enmTable=trmidb.com_enm_1d

indxList="MPTRXUS30 MPTRXUS500 MPTRXUSNAS100 MPTRXUSMID2000 MPTRXAU500 MPTRXBR50 MPTRXDE30 MPTRXEU50 MPTRXFR40 MPTRXGB100 MPTRXIN50 MPTRXJP225"
indxTable=trmidb.cmpny_grp_1d

platform=$1
dateBefore=`echo $2`
dateStart=`date +"%Y-%m-%dT%H:00:00.000Z" --date "$dateBefore"`
dataFrequency=1d

### COUNTRY QUERY
for line in $countryList
do
    ./queryTrmi.sql $platform $line $countryTable $dateStart $dataFrequency
done

### CURRENCY QUERY
for line in $currencyList
do
    ./queryTrmi.sql $platform $line $currencyTable $dateStart $dataFrequency
done

### COM_AGR QUERY
for line in $agrList
do
    ./queryTrmi.sql $platform $line $agrTable $dateStart $dataFrequency
done

### COM_ENM QUERY
for line in $enmList
do
    ./queryTrmi.sql $platform $line $enmTable $dateStart $dataFrequency
done

### CMPNY_GRP QUERY
for line in $indxList
do
    ./queryTrmi.sql $platform $line $indxTable $dateStart $dataFrequency
done

