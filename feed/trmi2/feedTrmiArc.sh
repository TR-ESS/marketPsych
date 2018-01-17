#!/bin/sh
Platform=$1
assetType=$2
updateType=$3
endFolder=$4
storage=$5
table=$6

confPath="/home/thomsonreutersess/marketPsychConf/trmiFeed.conf"

if [ ! -e ./prev.arc.$assetType.$updateType.list ]; then
    touch ./prev.arc.$assetType.$updateType.list
fi


while true
do
    ##### VALIDATE NEWLY INCOMING DATA
    if [ $endFolder == "zzz" ]; then
	python ./listFTP.py /TRMI/$assetType/$updateType/ $confPath | sort -k9 > ./curr.arc.$assetType.$updateType.list
    else
	python ./listFTP.py /TRMI/$assetType/$updateType/$endFolder/ $confPath | sort -k9 > ./curr.arc.$assetType.$updateType.list
    fi
    diff ./prev.arc.$assetType.$updateType.list ./curr.arc.$assetType.$updateType.list > ./diff.arc.$assetType.$updateType.list
    grep ">" ./diff.arc.$assetType.$updateType.list | awk '{print $10}' > ./transfer.arc.$assetType.$updateType.list

    ##### DO FTP Whenever newly incoming is detected (Version 3.x)
    cat ./transfer.arc.$assetType.$updateType.list | grep "\.03"| while read line
    do
	date; echo "---> FTP GET $line"
	if [ $endFolder == "zzz" ]; then
	    python ./doFTP.py /TRMI/$assetType/$updateType/$line $HOME/marketPsychData/data/arc/$line $confPath
	else
	    python ./doFTP.py /TRMI/$assetType/$updateType/$endFolder/$line $HOME/marketPsychData/data/arc/$line $confPath
	fi
	### UNZIP
	zcat $HOME/marketPsychData/data/arc/$line > $HOME/marketPsychData/data/arc/$line.tsv
	### RE-FORMAT
	sed -e 's/\t$/\t0.0/g' $HOME/marketPsychData/data/arc/$line.tsv | sed -e 's/\t\t/\t0.0\t/g' |  sed -e 's/\t\t/\t0.0\t/g' > $HOME/marketPsychData/data/arc/$line.m
	rm $HOME/marketPsychData/data/arc/$line
	rm $HOME/marketPsychData/data/arc/$line.tsv
	### COPY FILE TO STORAGE
	if [ $Platform == "GCP" ]; then
	    gsutil cp $HOME/marketPsychData/data/arc/$line.m $storage/arc/$line
	    bq load --source_format=CSV --field_delimiter='\t' --autodetect $table $storage/arc/$line

	    rm $HOME/marketPsychData/data/arc/$line.m
	    gsutil rm $storage/arc/$line
	fi
    done

cp ./curr.arc.$assetType.$updateType.list ./prev.arc.$assetType.$updateType.list
sleep 360
done
