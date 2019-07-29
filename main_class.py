#!/usr/bin/env python
# coding: utf-8
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# from operator import attrgetter
from typing import Iterable, Union
import pywikibot as pwb
import mwparserfromhell as mwp
import vladi_helpers.lib_for_mwparserfromhell as mymwp
import wiki_util
# from wikidata import wiki_util
from wd_utils import WD_utils, props
from get_other_sources_from_lua import get_other_sources
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_store_to_file, json_data_from_file
# # from vladi_helpers import vladi_helpers
from vladi_helpers.vladi_helpers import get_item_from_listdict

"""Перенос ссылок на энциклопедии/словари из статей в Викиданые и создание там записи."""
re_cat_redirect = re.compile(r'\[\[Категория:[^]]+?Перенаправления', flags=re.IGNORECASE)
re_remove_tag_commment = re.compile(r'<!--.*?(?:-->|$)', flags=re.DOTALL)


class PageMeta:
    itemWD: pwb.ItemPage
    title: str
    rootpagename: str
    subpagename: str
    tpl = None
    tplname: str
    is_author_tpl = False

    def __init__(self, page: pwb.page.Page):
        self.page = page
        self.title = page.title()
        self.rootpagename, self.subpagename = wiki_util.parse_pagename(self.title)
        self.params_to_delete = []

    def tpl_data(self, tpl):
        self.tpl = tpl
        self.tplname = tpl.name.strip()
        # self.is_author_tpl = self.tplname.lower() in allowed_header_names


class Process:
    works_pages_with_wditems = True  # работать со страницами только имеющими элемент ВД
    require_ruwiki_sitelink_in_item = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    make_wd_links = False  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc = False
    skip_links_with_anchors = True  # не трогать ссылки содержащие '#', вроде 'РСКД/Статья#якорь'
    prj = 'ruwikisource'
    allowed_header_names: tuple
    wd = None

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    wikiprojects = ['ВИКИПЕДИЯ', ]
    enc_prefixes: tuple

    # encyclopedies = ['ЭСБЕ', 'РСКД', 'ВЭ']

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    def __init__(self, test_run=False):
        self.as_bot = True
        self.test_run = test_run
        self.wd = WD_utils(as_bot=self.as_bot, test_run=test_run)
        self.wd.enc_meta = get_other_sources()
        # self.allowed_header_names.extend(self.enc_prefixes)
        self.enc_prefixes = tuple(self.wd.enc_meta.keys())

        self.pfuncmap = {
            # 'ВИКИДАННЫЕ': self.param_Wikidata,  # сначала ВИКИДАННЫЕ
            'ВИКИПЕДИЯ': self.param_Wikipedia,
            'ИЗОБРАЖЕНИЕ': self.param_Image,
        }

    def process_page(self, page):
        if page.isRedirectPage(): return
        p = PageMeta(page)

        # if p.title != 'Гай Валерий Катулл': return

        p.itemWD = self.wd.get_item(props.WS, page=page)
        if self.works_pages_with_wditems and not p.itemWD:
            return

        # self.page = pywikibot.Page(props.WS, title)
        # todo:  if not page.revisions[0].patroled.since >= 5days: return

        # пропускать страницы-перенаправления
        if re_cat_redirect.search(page.text):
            print('перенаправление')
            return

        # работать по энциклопедическая статья и словарная статья
        if self.work_only_enc:
            for e in p.itemWD.claims.get(props.item_type, []):
                if e.target.id not in props.types_to_search:
                    print('не словарная статья')
                    return

        print(p.title)

        text = p.page.get()
        wikicode = mwp.parse(text)
        # wikicode = mwp.parse('[[dffd|2222]][[Категория:апап|  33]]')
        for tpl in wikicode.filter_templates():
            p.tpl_name = tpl.name.strip()
            if p.tpl_name in self.allowed_header_names:
                p.tpl_data(tpl)

                if 'ТСД' in p.tpl_name:
                    return
                if [s for s in wikicode.filter_wikilinks(matches='^\[\[Категория:[^|]*?[Пп]еренаправления')]:
                    return
                # фильтр по размеру текста
                if p.tpl_name in ('МЭСБЕ', 'БЭАН'):
                    tmp = text.replace(str(tpl), '')
                    for s in wikicode.filter_wikilinks(matches='^\[\[Категория:'): tmp = tmp.replace(str(s), '')
                    if len(tmp) < 100:
                        return

                # if p.is_author_tpl is None: return
                p = self.process_params(p)

                if p.params_to_delete:
                    # очищаем параметры
                    mymwp.removeTplParameters(p.tpl, p.params_to_delete)
                    wiki_util.page_posting(p.page, str(wikicode), self.test_run)
                break

    def process_params(self, p):
        # if p.is_author_tpl:
        #     self.author()

        for param in p.tpl.params:
            pname = param.name.strip()
            if not pname in self.pfuncmap.keys() and not pname in self.enc_prefixes: continue
            pval = mymwp.get_param_value(p.tpl, pname) or ''
            pval = re_remove_tag_commment.sub('', pval).strip()
            if not pval or pval == '': continue

            # параметры проектов
            if pname in self.pfuncmap.keys():
                func = self.pfuncmap.get(pname)
                func(p, pname, pval)
                pass

            # параметры словарей
            elif pname in self.enc_prefixes:
                if 'ТСД' in pname: continue
                self.param_encyclopedia(p, pname, pval)
                pass

        return p

    def param_encyclopedia(self, p, pname, m_wp_pagename_raw):
        pass

    def param_Wikipedia(self, p, pname, m_wp_pagename_raw):
        pass

    def param_Image(self, p, pname, m_wp_pagename_raw):
        pass