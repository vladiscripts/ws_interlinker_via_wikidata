#!/usr/bin/env python
# coding: utf-8
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# from vladi_helpers import vladi_helpers
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
import vladi_helpers.lib_for_mwparserfromhell as mymwp
import pywikibot as pwb


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
    if title:
        page = pwb.Page(site, title)
    while page.isRedirectPage():
        page = page.getRedirectTarget()
    return page


def get_pages(args: list = None, test_pages: list = None):
    """ Get list of pages which using 'Template:infobox former country'
        без кавычек имена станиц/категорий в параметрах
    """
    from pywikibot import pagegenerators
    # from wd_utils import props
    from wd_utils import WD_utils

    if test_pages:
        gen = (pwb.Page(WD_utils.WP, title) for title in test_pages if title and title.strip() != '')
    else:
        # args = ['-family:wikipedia', '-lang:en', '-ns:0'] + [f'-transcludes:{tpl}' for tpl in tpl_names]
        gen_factory = pwb.pagegenerators.GeneratorFactory()
        local_args = pwb.handle_args(args)
        for arg in local_args:
            gen_factory.handleArg(arg)
        gen = gen_factory.getCombinedGenerator(
            preload=False
        )
    return gen
