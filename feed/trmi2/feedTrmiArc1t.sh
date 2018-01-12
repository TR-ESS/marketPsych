#!/bin/sh
Platform=$1
assetType=$2
updateType=$3
endFolder=$4
storage=$5
table=$6


if [ ! -e ./prev.arc.1t.$assetType.$updateType.list ]; then
    touch ./prev.arc.1t.$assetType.$updateType.list
fi


    ##### VALIDATE NEWLY INCOMING DATA
    if [ $endFolder == "zzz" ]; then
	python ./listFTP.cgl.py /TRMI/$assetType/$updateType/ | sort -k9 > ./curr.arc.1t.$assetType.$updateType.list
    else
	python ./listFTP.cgl.py /TRMI/$assetType/$updateType/$endFolder/ | sort -k9 > ./curr.arc.1t.$assetType.$updateType.list
    fi
    diff ./prev.arc.1t.$assetType.$updateType.list ./curr.arc.1t.$assetType.$updateType.list > ./diff.arc.1t.$assetType.$updateType.list
    grep ">" ./diff.arc.1t.$assetType.$updateType.list | awk '{print $10}' > ./transfer.arc.1t.$assetType.$updateType.list

    ##### DO FTP Whenever newly incoming is detected (Version 3.x)
    cat ./transfer.arc.1t.$assetType.$updateType.list | grep "\.03"| while read line
    do
	date; echo "---> FTP GET $line"
	if [ $endFolder == "zzz" ]; then
	    python ./doFTP.cgl.py /TRMI/$assetType/$updateType/$line $HOME/marketPsychData/data/arc/$line
	else
	    python ./doFTP.cgl.py /TRMI/$assetType/$updateType/$endFolder/$line $HOME/marketPsychData/data/arc/$line
	fi
	### UNZIP
	zcat $HOME/marketPsychData/data/arc/$line > $HOME/marketPsychData/data/arc/$line.tsv
	### RE-FORMAT
	sed -e 's/\t\t/\t0.0\t/g' $HOME/marketPsychData/data/arc/$line.tsv | sed -e 's/\t\t/\t0.0\t/g' > $HOME/marketPsychData/data/arc/$line.m
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

cp ./curr.arc.1t.$assetType.$updateType.list ./prev.arc.1t.$assetType.$updateType.list

