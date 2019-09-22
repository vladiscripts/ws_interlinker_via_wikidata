#!/usr/bin/env python3
# coding: utf-8
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlsplit, parse_qs, parse_qsl, unquote, quote
# from vladi_helpers import vladi_helpers
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_store_to_file, json_data_from_file
import re
from typing import Iterable, Union
import pywikibot as pwb
import mwparserfromhell as mwp
import vladi_helpers.lib_for_mwparserfromhell as mymwp
import logging

# logger = logging.getLogger('logger_')
# log_handler = logging.StreamHandler()
# log_handler.setLevel(logging.INFO)
# log_handler.setFormatter(logging.Formatter('%(message)s'))
# logger.addHandler(log_handler)
# logging.basicConfig(level=logging.INFO, format='%(message)s')
# logger = logging.getLogger('example_logger')
