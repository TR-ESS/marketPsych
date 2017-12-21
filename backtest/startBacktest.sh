#!/bin/sh
asset=$1 #e.g N225 (same name in the config file)
model=$2 #dt (Decision Tree) or mlp (Multilayer Perceptron)
config="../config/ml.$model.$asset.conf"
startingFrom=$3
surveyPeriod=$4
platform="GCP"
hls=$5
asset2=`echo $asset | sed -e 's/=//g'`

python ./edge_market_tracer_1_1.py $config $startingFrom $surveyPeriod $platform

gsutil cp ../../marketPsychData/ret/$asset.$model.csv gs://tr-jp-analytics/temp/$asset2.$model.csv
gsutil cp ../../marketPsychData/ret/$asset.$model.pfm.csv gs://tr-jp-analytics/temp/$asset2.$model.pfm.csv

bq rm -f -t performance.$asset2'_'$model
bq rm -f -t performance.$asset2'_'$model'_pfm'



bq load --source_format=CSV --field_delimiter=',' --autodetect performance.$asset2'_'$model gs://tr-jp-analytics/temp/$asset2.$model.csv
bq load --source_format=CSV --field_delimiter=',' --autodetect performance.$asset2'_'$model'_pfm'  gs://tr-jp-analytics/temp/$asset2.$model.pfm.csv
