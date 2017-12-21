#!/bin/sh
platformName="GCP"
listAssetTypes="COU CUR COM_AGR COM_ENM CMPNY_GRP"
updateType="WDAI_UDAI"
endFolder="zzz"
storage='gs://tr-jp-analytics/trmi'
databases=(trmidb.cou_1d trmidb.cur_1d trmidb.com_agr_1d trmidb.com_enm_1d trmidb.cmpny_grp_1d)

cd $HOME/marketPsych/feed/trmi


count=0
for line in $listAssetTypes
do
    echo $line
    echo ${databases[$count]}

    ./feedTrmi.sh $platformName $line $updateType $endFolder $storage ${databases[$count]} &> $HOME/marketPsychData/applog/$line.$updateType.log &

    count=$count+1
done
