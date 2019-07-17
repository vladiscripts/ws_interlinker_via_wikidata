#!/usr/bin/env python
# coding: utf-8
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# from vladi_commons import vladi_helpers
# from vladi_commons.file_helpers import csv_save_dict_fromListWithHeaders, json_store_to_file, json_data_from_file
import vladi_commons.lib_for_mwparserfromhell as mymwp
import pywikibot as pwb


def parse_pagename(title: str):
    rootpagename, _, pagename = title.partition('/')
    return rootpagename, pagename


# def param_value_clear(tpl, pname, test_run=False, remove_param=False):
#     if not test_run:
#         if remove_param:
#             mymwp.removeTplParameters(tpl, pname)
#         else:
#             mymwp.param_value_clear(tpl, pname, new_val='\n')


def page_posting(page, page_text, test_run=False):
    if page.text != page_text:
        if test_run:
            return
        page.text = page_text
        page.save('очистка парметра, перенесено в Викиданные')


def get_pages(base_args, args: list = None, intersect=False, test_pages: list = None, test_run:bool=False):
    """ Get list of pages which using 'Template:infobox former country'
        без кавычек имена станиц/категорий в параметрах
    """
    from pywikibot import pagegenerators
    from wd_utils import Props

    if test_run:
        gen = (pwb.Page(Props.WP, title) for title in test_pages if title and title.strip() != '')
    else:
        # args = ['-family:wikipedia', '-lang:en', '-ns:0'] + [f'-transcludes:{tpl}' for tpl in tpl_names]
        local_args = pwb.handle_args(base_args)
        gen_factory = pwb.pagegenerators.GeneratorFactory()
        gen_factory.intersect = intersect
        for arg in args:
            gen_factory.handleArg(arg)
        gen = gen_factory.getCombinedGenerator(
            preload=False
                                               )
    return gen
