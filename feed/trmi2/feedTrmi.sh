#!/bin/sh
Platform=$1
assetType=$2
updateType=$3
endFolder=$4
storage=$5
table=$6

confPath="$HOME/marketPsychConf/trmiFeed.conf"

if [ ! -e ./list/prev.$assetType.$updateType.list ]; then
    touch ./list/prev.$assetType.$updateType.list
fi


while true
do
    ##### VALIDATE NEWLY INCOMING DATA
    if [ $endFolder == "zzz" ]; then
	python ./listFTP.py /TRMI_LIVE/$assetType/$updateType/ $confPath | sort -k9 > ./list/curr.$assetType.$updateType.list
    else
	python ./listFTP.py /TRMI_LIVE/$assetType/$updateType/$endFolder/ $confPath | sort -k9 > ./list/curr.$assetType.$updateType.list
    fi
    diff ./list/prev.$assetType.$updateType.list ./list/curr.$assetType.$updateType.list > ./list/diff.$assetType.$updateType.list
    grep ">" ./list/diff.$assetType.$updateType.list | awk '{print $10}' > ./list/transfer.$assetType.$updateType.list

    ##### DO FTP Whenever newly incoming is detected
    cat ./list/transfer.$assetType.$updateType.list | while read line
    do
	date; echo "---> FTP GET $line"
	if [ $endFolder == "zzz" ]; then
	    python ./doFTP.py /TRMI_LIVE/$assetType/$updateType/$line $HOME/marketPsychData/data/$line $confPath
	else
	    python ./doFTP.py /TRMI_LIVE/$assetType/$updateType/$endFolder/$line $HOME/marketPsychData/data/$line $confPath
	fi
	### RE-FORMAT
	sed -e 's/\t$/\t0.0/g' $HOME/marketPsychData/data/$line | sed -e 's/\t\t/\t0.0\t/g' | sed -e 's/\t\t/\t0.0\t/g' > $HOME/marketPsychData/data/$line.m

	### COPY FILE TO STORAGE
	if [ $Platform == "GCP" ]; then
	    gsutil cp $HOME/marketPsychData/data/$line.m $storage/$line
	    bq load --source_format=CSV --field_delimiter='\t' --autodetect $table $storage/$line

	    rm $HOME/marketPsychData/data/$line.m
	    rm $HOME/marketPsychData/data/$line
	    gsutil rm $storage/$line
	fi
    done

cp ./list/curr.$assetType.$updateType.list ./list/prev.$assetType.$updateType.list
sleep 60
done
