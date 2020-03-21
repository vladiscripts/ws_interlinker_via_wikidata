#!/usr/bin/env python3
import requests
# from vladi_helpers import vladi_helpers
from vladi_helpers.vladi_helpers import url_params_str_to_dict, url_params_str_to_list
from vladi_helpers.file_helpers import json_save_to_file, json_load_from_file, file_savetext, file_readtext
from vladi_helpers.vladi_helpers import url_params_str_to_dict, url_params_str_to_list
import sqlite3
import json
from lxml.html import fromstring  # import html5lib
from urllib.parse import urlsplit, parse_qs, parse_qsl, unquote, quote, urlencode, urlunsplit
import pandas as pd
import os, io
from pathlib import Path
from datetime import datetime


def make_sql(lastedit_days: int):
    x = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    # categories = ','.join(['"%s"' % d['category_of_articles'] for prefix, d in prefixes.items()])
    categories = ','.join([f'"{}"' for c in ["Ручная ссылка:Википедия", "Ручная ссылка:Викиданные"]])
    #  'БЭЮ', 'БСЭ1' мелкие словарные статьи или масса перенаправлений
    sql = f"""
    SELECT page_namespace,  page_title
    FROM ruwikisource_p.page
        JOIN ruwikisource_p.categorylinks 
            ON cl_from = page_id
            AND page_namespace = 0 
            AND cl_to IN ({categories})
            AND page_is_redirect = 0
        LEFT JOIN ruwikisource_p.categorylinks cw 
            ON cw.cl_from = page_id
            AND cw.cl_to = "Викиданные:Страницы_с_элементами"
        LEFT JOIN ruwikisource_p.categorylinks cr 
            ON cr.cl_from = page_id
            AND cr.cl_to LIKE "%еренаправлени%"
        JOIN revision
            ON page_latest = rev_id
            AND rev_timestamp < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {lastedit_days} DAY)
    WHERE cw.cl_to IS NULL AND cr.cl_to IS NULL;
    """.replace('\n', ' ').strip()
    return sql


