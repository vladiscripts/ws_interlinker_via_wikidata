#!/usr/bin/env python
# coding: utf-8
from __init__ import *
from wd_utils import WD_utils
import json


def parse_lua_to_dict(WS, page_name, var_name):
    lua_module = pwb.Page(WS, page_name)
    t = re.sub(r'--.+?\n', '', lua_module.text)
    other_sources_raw = re.search(var_name + r'\s*=\s*{'
                                             r'((?:\s*{[^}]+?},?\s*)+)'
                                             r'}', t, flags=re.S | re.VERBOSE)
    splitted = re.findall(r'\s*{([^}]+?)}(?:,\s|\s$)', other_sources_raw.group(1), flags=re.S | re.VERBOSE)
    data = []
    for params in splitted:
        d = {}
        pp = re.sub(r"(^|,)(\s*[^\s]+\s*=)", r'%#%\2', params, flags=re.S).split(
            '%#%')  # split с уст. врем. разделителя
        for p in pp:
            if p.strip() != '':
                k, _, v = p.partition('=')
                key = k.strip('\t\n\r \'')
                value = v.strip('\t\n\r \'')
                d[key] = value
        data.append(d)
        # assert len(other_sources[0]) == 6
    if not data:
        raise Exception('Ошибка загрузки данных о словарях из Модуль:Другие источники')
    return data


def get_other_sources():
    # other_sources = parse_lua_to_dict(WD_utils.WS, 'Модуль:Другие источники', 'otherSources')
    # wikiprojects = parse_lua_to_dict(self.wd.WD, 'Модуль:Навигация-мини', 'projects')
    j = pwb.Page(WD_utils.WS, 'MediaWiki:Encyclopedias_settings.json')
    other_sources = json.loads(j.text)
    enc_meta = {}
    for n in other_sources:
        n['wditem'] = pwb.ItemPage(WD_utils.WD, n['id'])
        pname = n['argument']
        enc_meta[pname] = n
    return enc_meta
