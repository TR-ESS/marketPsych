#!/bin/sh
Platform=$1
assetType=$2
updateType=$3
endFolder=$4
storage=$5
table=$6


if [ ! -e ./list/prev.arc.1t.$assetType.$updateType.list ]; then
    touch ./list/prev.arc.1t.$assetType.$updateType.list
fi


    ##### VALIDATE NEWLY INCOMING DATA
    if [ $endFolder == "zzz" ]; then
	python ./listFTP.cgl.py /TRMI/$assetType/$updateType/ | sort -k9 > ./list/curr.arc.1t.$assetType.$updateType.list
    else
	python ./listFTP.cgl.py /TRMI/$assetType/$updateType/$endFolder/ | sort -k9 > ./list/curr.arc.1t.$assetType.$updateType.list
    fi
    diff ./list/prev.arc.1t.$assetType.$updateType.list ./list/curr.arc.1t.$assetType.$updateType.list > ./list/diff.arc.1t.$assetType.$updateType.list
    grep ">" ./list/diff.arc.1t.$assetType.$updateType.list | awk '{print $10}' > ./list/transfer.arc.1t.$assetType.$updateType.list

    ##### DO FTP Whenever newly incoming is detected (Version 3.x)
    cat ./list/transfer.arc.1t.$assetType.$updateType.list | grep "\.03"| while read line
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
	sed -e 's/\t$/\t0.0/g' $HOME/marketPsychData/data/arc/$line.tsv | sed -e 's/\t\t/\t0.0\t/g' | sed -e 's/\t\t/\t0.0\t/g' > $HOME/marketPsychData/data/arc/$line.m
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

cp ./list/curr.arc.1t.$assetType.$updateType.list ./list/prev.arc.1t.$assetType.$updateType.list

