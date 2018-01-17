#!/bin/sh
platformName="GCP"
listAssetTypes="COM_AGR COM_ENM CMPNY_GRP"
updateType="WDAI_UHOU"
endFolder="Recent"
storage='gs://tr-jp-analytics/trmi'
databases=(trmidb.com_agr_1h_arc trmidb.com_enm_1h_arc trmidb.cmpny_grp_1h_arc)

cd $HOME/marketPsych/feed/trmi2


count=0
for line in $listAssetTypes
do
    echo $line
    echo ${databases[$count]}

    ./feedTrmiArc.sh $platformName $line $updateType $endFolder $storage ${databases[$count]} &> $HOME/marketPsychData/applog/$line.$updateType.arc.log &

    count=$count+1
done
