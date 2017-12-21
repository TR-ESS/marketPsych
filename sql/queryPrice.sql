#!/bin/sh

OutputBucket="tr-jp-analytics"

DataArea=$HOME/marketPsychData/data
LogArea=$HOME/marketPsychData/log
AppLogArea=$HOME/marketPsychData/applog

Platform=$1
retName=$2
tableName=$3
dateStart=$4
dataFrequency=$5

#dateStart=`date +"%Y-%m-%dT%H:00:00.000Z" --date "$dateBefore"`
if [ $dataFrequency == "1h" ]; then
    echo '"select * from '$tableName ' where assetCode='"'"$retName"'" ' and windowTimestamp > ' "'"$dateStart"'" ' order by windowTimestamp;" \' > ./sqlPriceString.$dataFrequency.aws
    echo '"select * from '$tableName ' where assetCode='"'"$retName"'" ' and windowTimestamp > ' "'"$dateStart"'" ' order by windowTimestamp"' > ./sqlPriceString.$dataFrequency.gcp
else
    echo '"select * from '$tableName ' where assetCode='"'"$retName"'" ' and date(windowTimestamp) > ' "'"$dateStart"'" ' order by windowTimestamp;" \' > ./sqlPriceString.$dataFrequency.aws
    echo '"select * from '$tableName ' where assetCode='"'"$retName"'" ' and date(windowTimestamp) > ' "'"$dateStart"'" ' order by windowTimestamp"' > ./sqlPriceString.$dataFrequency.gcp
fi

echo $queryString

# SWITCHIG PROCESS BASED ON THE PLATFORM (AWS or GCP)
if [ $Platform == "AWS" ]; then
    echo "Amazon Web Service Cleanup processing..."
    echo '#!/bin/sh' > .sql.$dataFrequency.cmd
    echo 'aws --region ap-northeast-1 athena start-query-execution \' >> .sql.$dataFrequency.cmd
    cat ./sqlPriceString.$dataFrequency.aws >> .sql.$dataFrequency.cmd
    echo ' --result-configuration OutputLocation=s3://'$OutputBucket >> .sql.$dataFrequency.cmd

elif [ $Platform == "GCP" ]; then
    ### CONSTRUCT SQL COMMAND WITH BIG QUERY
    echo '#!/bin/sh' > .sql.$dataFrequency.cmd
    echo 'bq query -n 1000000 \' >> .sql.$dataFrequency.cmd
    cat ./sqlPriceString.$dataFrequency.gcp >> .sql.$dataFrequency.cmd

    chmod 755 .sql.$dataFrequency.cmd

    ### EXECUTE QUERY
    ./.sql.$dataFrequency.cmd > $HOME/marketPsychData/sql/$dataFrequency/$retName.price.sql0
    grep -v "\-\-\-\-+"  $HOME/marketPsychData/sql/$dataFrequency/$retName.price.sql0 | sed -e "s/|\$//" | sed -e "s/^|//" | sed -e "s/|/,/g" | sed -e "s/ //g" | sed "/^$/d"  > $HOME/marketPsychData/sql/$dataFrequency/$retName.price.sql
    rm $HOME/marketPsychData/sql/$dataFrequency/$retName.price.sql0
fi



