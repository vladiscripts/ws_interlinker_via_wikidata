#!/usr/bin/env python
# coding: utf-8
from __init__ import *
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# import pywikibot as pwb
# from vladi_helpers import vladi_helpers
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
import vladi_helpers.lib_for_mwparserfromhell as mymwp


def parse_pagename(title: str):
    rootpagename, subpagename = None, None
    if '/' in title:
        rootpagename, _, subpagename = title.partition('/')
    return rootpagename, subpagename


# def param_value_clear(tpl, pname, test_run=False, remove_param=False):
#     if not test_run:
#         if remove_param:
#             mymwp.removeTplParameters(tpl, pname)
#         else:
#             mymwp.param_value_clear(tpl, pname, new_val='\n')


def page_posting(page, page_text, summary=None, test_run=False):
    page_text = page_text.strip()
    if page.text != page_text:
        if test_run:
            return
        page.text = page_text
        page.save(summary)


def get_wikipage(site, title=None, page=None):
    page = page or pwb.Page(site, title)
    while page.isRedirectPage():
        page = page.getRedirectTarget()
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
        gen_factory.handleArg(arg)
    gen = gen_factory.getCombinedGenerator(preload=False)
    return gen


def remove_param(p, pname: str, value_only=False):
    mymwp.removeTplParameters(p.tpl, pname, remove_value_only=value_only)
    if value_only:
        p.params_to_value_clear.append(pname)
    else:
        p.params_to_delete.append(pname)


def make_summary(p):
    _summary = []
    if p.params_to_delete:
        _summary.append(f'ссылка перенесена в Викиданные (%s)' % ','.join(p.params_to_delete))
    if p.params_to_value_clear:
        _summary.append(f'ссылка на несущ. страницу (%s)' % ','.join(p.params_to_value_clear))
    summary = '; '.join(_summary + p.summaries)
    return summary


def make_re_wikilink_category(cat_name):
    return fr'\[\[Категория:{cat_name}(?:\|.*)?\]\]'


def make_wikilink_category(cat_name, text=None):
    if text:
        return f'[[Категория:{cat_name}|{text}]]'
    return f'[[Категория:{cat_name}]]'


def set_or_remove_category(p, cat_name: str, condition: bool, add_cat: bool = False, log_on_add: str = None):
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
