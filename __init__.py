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
import pywikibot as pwb
import mwparserfromhell as mwp
import vladi_helpers.lib_for_mwparserfromhell as mymwp
import logging
from typing import Tuple, List, Optional, Any, Iterable, Union, Callable
# from typing import NamedTuple
from collections import OrderedDict
from abc import abstractmethod
import sys

logger = logging.getLogger('logger_')
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
# # logging.basicConfig(level=logging.INFO, format='%(message)s')
# logger..basicConfig(level=logging.INFO)
# logger = logging.getLogger('example_logger')

# logging.basicConfig(level=logging.INFO, format='%(message)s')
