#!/bin/sh
cdir=`pwd`
cd $HOME/marketPsychData/data1t

ls -1 *.zip > $cdir/_unzip.list

cat $cdir/_unzip.list | while read line
do
    outfile=`echo $line | awk -F'.' '{print $1"."$2"."$3"."$4"."$5"."$6".txt"}'`
    zcat $line > $outfile
    rm $line

done 
