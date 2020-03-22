#!/bin/bash
# jsub -once -e ~/cgi-bin/patrolpage/temp/ -o ~/cgi-bin/patrolpage/temp/ -N patrolpage ./run.sh
# jsub -once -N articles ./run_articles.sh
source $PYTHONENV/bin/activate
cd ~/scripts/ws_interlinker_via_wikidata
# PYTHONIOENCODING="utf-8"
LANG="ru_RU.UTF-8" ./articles.py -titleregexnot:"^ТСД" -cat:"Ручная ссылка:Википедия" -onlyif:P31=Q13433827
# LANG="ru_RU.UTF-8" ./articles.py -titleregexnot:"^ТСД" -cat:"Ручная ссылка:Википедия" -onlyif:P31=Q17329259
# LANG="ru_RU.UTF-8" ./articles.py -titleregexnot:"^ТСД" -cat:"Ручная ссылка:Википедия" -onlyif:P31=Q1580166