#!/bin/sh
platformName="GCP"
listAssetTypes="COU CUR COM_AGR COM_ENM CMPNY_GRP"
updateType="WDAI_UHOU"
endFolder="LastTwoHours"
storage='gs://tr-jp-analytics/trmi'
databases=(trmidb.cou_1h trmidb.cur_1h trmidb.com_agr_1h trmidb.com_enm_1h trmidb.cmpny_grp_1h)

cd $HOME/marketPsych/feed/trmi2


count=0
for line in $listAssetTypes
do
    echo $line
    echo ${databases[$count]}

    ./feedTrmi.sh $platformName $line $updateType $endFolder $storage ${databases[$count]} &> $HOME/marketPsychData/applog/$line.$updateType.log &

    count=$count+1
done
