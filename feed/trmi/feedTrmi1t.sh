#!/bin/sh
Platform=$1
assetType=$2
updateType=$3
endFolder=$4
storage=$5
table=$6

cDir=`pwd`

cd $HOME/marketPsychData/data1t

ls -1  > $cDir/transfer1t.$assetType.list.0
grep $assetType $cDir/transfer1t.$assetType.list.0 > $cDir/transfer1t.$assetType.list

cd $cDir

##### DO FTP Whenever newly incoming is detected
cat ./transfer1t.$assetType.list | while read line
do
    date; echo "---> FTP GET $line"
    ### RE-FORMAT
    sed -e 's/\t\t/\t0.0\t/g' $HOME/marketPsychData/data1t/$line | sed -e 's/\t\t/\t0.0\t/g' > $HOME/marketPsychData/data1t/$line.m

    ### COPY FILE TO STORAGE
    if [ $Platform == "GCP" ]; then
	gsutil cp $HOME/marketPsychData/data1t/$line.m $storage/$line
	bq load --source_format=CSV --field_delimiter='\t' --autodetect $table $storage/$line

	rm $HOME/marketPsychData/data1t/$line.m
	rm $HOME/marketPsychData/data1t/$line
	gsutil rm $storage/$line
    fi
done


