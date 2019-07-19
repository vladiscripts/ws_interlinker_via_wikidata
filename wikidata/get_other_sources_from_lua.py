#!/usr/bin/env python
# coding: utf-8
import re
import pywikibot


def get_other_sources(cl):
    def parse_lua_to_dict(WS, var_name):
        k = {'otherSources': 'Модуль:Другие источники', 'projects': 'Модуль:Навигация-мини'}
        lua_text = pywikibot.Page(WS, k[var_name])
        other_sources_raw = re.search(var_name + r'\s*=\s*{'
                                                 r'((?:\s*{[^}]+?},?\s*)+)'
                                                 r'}', lua_text.text, flags=re.S | re.VERBOSE)
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

    other_sources = parse_lua_to_dict(cl.wd.WS, 'otherSources')
    # wikiprojects = parse_lua_to_dict(self.wd.WD, 'projects')
    for n in other_sources:
        n['wditem'] = pywikibot.ItemPage(cl.wd.WD, n['id'])
        pname = n['argument']
        cl.wd.enc_meta[pname] = n
        cl.enc_prefixes.append(pname)
