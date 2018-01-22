#!/bin/sh

confPath=$1
if [ ! -e $confPath ]; then
    echo "Config file $confPath not found"
    exit
fi
outFile=`awk -F'|' 'NR==2 {print $8}' $confPath`
storage=`awk -F'|' 'NR==2 {print $11}' $confPath`
product=`echo $outFile | sed -e 's/.csv//g'`
table=`echo "tickdb.$product"`

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
	# cat ./transfer.$outFile.0 >> list/toFeed.$outFile
	echo "$headerRec" > list/toFeedBQ.$outFile
	cat ./transfer.$outFile.0 >> list/toFeedBQ.$outFile
	gsutil cp list/toFeedBQ.$outFile $storage/toFeedBQ.$outFile
	bq load --source_format=CSV --field_delimiter=',' --autodetect $table $storage/toFeedBQ.$outFile
	
    fi
    cp ./$outFile ./$outFile.prev
    sleep 300
done
