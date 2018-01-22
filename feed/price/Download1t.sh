#!/bin/sh

python trthDownload.py $HOME/marketPsychConf/trth/tmp/C.conf &> C.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/S.conf &> S.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/W.conf &> W.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/VIX.conf &> VIX.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/CRB.conf &> CRB.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/BADI.conf &> BADI.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/JPY.conf &> JPY.out &
python trthDownload.py $HOME/marketPsychConf/trth/tmp/EURJPY.conf &> EURJPY.out &

