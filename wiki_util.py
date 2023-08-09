#!/usr/bin/env python
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# import pywikibot as pwb
# from vladi_helpers import vladi_helpers
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
# import vladi_helpers.lib_for_mwparserfromhell as mymwp
from __init__ import *


# def parse_pagename(title: str) ->Optional[pwb.Page]:
#     rootpagename, subpagename = None, None
#     if '/' in title:
#         rootpagename, _, subpagename = title.partition('/')
#     return rootpagename, subpagename


# def param_value_clear(tpl, name, test_run=False, remove_param=False):
#     if not test_run:
#         if remove_param:
#             mymwp.removeTplParameters(tpl, name)
#         else:
#             mymwp.param_value_clear(tpl, name, new_val='\n')


def page_posting(page: pwb.Page, page_text: str, summary: str = None, test_run: bool = False) -> None:
    page_text = page_text.strip()
    if page.text != page_text:
        if test_run:
            return
        page.text = page_text
        page.save(summary)


def get_wikipage(site: str, title: str = None, page: pwb.Page = None) -> Optional[pwb.Page]:
    page = page or pwb.Page(site, title)
    while page.isRedirectPage():
        page = page.getRedirectTarget()
    if page.exists():
        return page


def pagegenerator(args: list = None):
    """ Get list of pages which using 'Template:infobox former country'
        без кавычек имена станиц/категорий в параметрах
    """
    from pywikibot import pagegenerators

    # args = ['-family:wikipedia', '-lang:en', '-ns:0'] + [f'-transcludes:{tpl}' for tpl in tpl_names]
    gen_factory = pwb.pagegenerators.GeneratorFactory()
    local_args = pwb.handle_args(args)
    for arg in local_args:
        gen_factory.handle_arg(arg)
    gen = gen_factory.getCombinedGenerator(preload=False)
    return gen

def removeTplParameters(tpl, keys, remove_value_only=False):
    if keys and isinstance(keys, str): keys = (keys,)
    for k in keys:
        if tpl.has(k):
            if remove_value_only:
                tpl.get(k).value = '\n' if '\n' in tpl.get(k).value else ''
            else:
                tpl.remove(k)
    return True

def remove_param(p, name: str, value_only: bool = False) -> None:
    removeTplParameters(p.tpl, name, remove_value_only=value_only)
    if value_only:
        p.params_to_value_clear.append(name)
    else:
        p.params_to_delete.append(name)


def make_summary(p) -> str:
    _summary = []
    if p.params_to_delete:
        lst = ','.join(p.params_to_delete)
        _summary.append(f'ссылка перенесена в Викиданные ({lst})')
    if p.params_to_value_clear:
        # _summary.append(f'ссылка на несущ. страницу (%s)' % ','.join(p.params_to_value_clear))
        lst = ','.join(p.params_to_value_clear)
        _summary.append(f'очистка параметра ({lst}), перенесено в Викиданные или ссылка на несущ. страницу')
    summary = '; '.join(_summary + p.summaries)
    return summary


def make_re_wikilink_category(cat_name: str) -> str:
    return fr'\[\[Категория:{cat_name}(?:\|.*)?\]\]'


def make_wikilink_category(cat_name: str, text: str = None) -> str:
    if text:
        return f'[[Категория:{cat_name}|{text}]]'
    return f'[[Категория:{cat_name}]]'


def set_or_remove_category(p, cat_name: str, condition: bool, add_cat: bool = False, log_on_add: str = None) -> None:
    cat_full = make_wikilink_category(cat_name)
    cat_full_re = make_re_wikilink_category(cat_name)
    if condition:
        if add_cat:
            if log_on_add: pwb.stdout(log_on_add)
            if not [i for i in p.wikicode.filter_wikilinks(matches=cat_full_re)]:
                p.wikicode.append(cat_full)
                p.summaries.append('категория')
            return
    else:
        for i in p.wikicode.filter_wikilinks(matches=cat_full_re):
            p.wikicode.remove(i)

# def parse(title):
#     page = pywikibot.Page(SITE, title)
#     text = page.get()
#     return mwparserfromhell.parse(text)

def iter_user_contributions(substr='', total=5, namespaces=0, minus_days=0, minus_hours=3,
                            start=None, end=None):
    from datetime import datetime, timedelta
    from wd_utils import WD_utils
    if minus_days or minus_hours:
        start = datetime.utcnow() - timedelta(days=minus_days, hours=minus_hours)
    u = pwb.User(WD_utils.WS, 'TextworkerBot')
    for page, revid, timestamp, summary in u.contributions(total=total, namespaces=namespaces, start=start, end=end):
        if substr in summary:
            return page
