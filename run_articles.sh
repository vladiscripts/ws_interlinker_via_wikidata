#!/bin/bash
# jsub -once -e ~/cgi-bin/patrolpage/temp/ -o ~/cgi-bin/patrolpage/temp/ -N patrolpage ./run.sh
source $PYTHONENV/bin/activate
cd ~/cgi-bin/interlinker_by_wikidata
# PYTHONIOENCODING="utf-8"
LANG="ru_RU.UTF-8" ./articles.py -titleregexnot:"^ТСД" -cat:"Ручная ссылка:Википедия|И" -onlyif:P31=Q13433827
