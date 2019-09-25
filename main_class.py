#!/usr/bin/env python
# coding: utf-8
from __init__ import *
# import requests
# import sqlite3
# import json
# from lxml.html import fromstring
# import re
# from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# from operator import attrgetter
# from typing import Iterable, Union
# import pywikibot as pwb
# import mwparserfromhell as mwp
# import vladi_helpers.lib_for_mwparserfromhell as mymwp
import wiki_util
from wd_utils import WD_utils
from get_other_sources_from_lua import get_other_sources
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
# from vladi_helpers.vladi_helpers import get_item_from_listdict
from abc import abstractmethod
import sys

"""Перенос ссылок на энциклопедии/словари из статей в Викиданые и создание там записи."""
re_cat_redirect = re.compile(r'\[\[Категория:[^]]+?Перенаправления', flags=re.IGNORECASE)
re_remove_tag_commment = re.compile(r'<!--.*?(?:-->|$)', flags=re.DOTALL)


class PageMeta:
    def __init__(self, page: pwb.page.Page):
        self.is_author_tpl = False
        self.page = wiki_util.get_wikipage(page.site, page=page)
        self.title = page.title()
        self.rootpagename, self.subpagename = wiki_util.parse_pagename(self.title)
        self.enc_with_trancludes = self.rootpagename in ('ПБЭ', 'ЭЛ')
        self.params_to_delete = []
        self.params_to_value_clear = []
        # do_cause = None
        self.tpl = None
        self.tpl_name = None
        self.summaries = []

    def tpl_data(self, tpl):
        self.tpl = tpl
        self.tpl_name = tpl.name.strip()
        # self.is_author_tpl = self.tplname.lower() in allowed_header_names


class Process:
    works_pages_with_wditems = True  # работать со страницами только имеющими элемент ВД
    require_ruwiki_sitelink_in_item = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    skip_wd_links_to_disambigs = True  # не работать по словарным ссылкам на дизамбиги
    make_wd_links = False  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc: bool  # работать только по элементам типов 'Q17329259', 'Q1580166' (энц. и словар. статьи)
    skip_links_with_anchors = True  # не трогать ссылки содержащие '#', вроде 'РСКД/Статья#якорь'
    skip_by_text_lengh = True
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
        self.test_run = test_run
        self.wd = WD_utils(as_bot=True, test_run=test_run)
        self.wd.enc_meta = get_other_sources()
        # self.allowed_header_names.extend(self.enc_prefixes)
        self.enc_prefixes = tuple(self.wd.enc_meta.keys())

        self.pfuncmap = {
            # 'ВИКИДАННЫЕ': self.param_Wikidata,  # сначала ВИКИДАННЫЕ
            'ВИКИПЕДИЯ': self.param_Wikipedia,
            'ИЗОБРАЖЕНИЕ': self.param_Image,
        }

    def process_page(self, page):
        p = PageMeta(page)
        pwb.stdout(p.title)

        if p.title.startswith('ТСД'):
            return

        p.itemWD = self.wd.get_item(self.wd.WS, page=page)
        if self.works_pages_with_wditems and not p.itemWD:
            pwb.stdout('no p.itemWD')
            return

        # self.page = pywikibot.Page(self.wd.WS, title)
        # todo:  if not page.revisions[0].patroled.since >= 5days: return

        # пропускать страницы-перенаправления
        if re_cat_redirect.search(page.text):
            pwb.stdout('перенаправление')
            return

        # работать по энциклопедическая статья и словарная статья
        if self.work_only_enc:
            # is_article = False
            for e in self.wd.get_claims_item_type(p.itemWD):
                #     for t in e.target.claims.claims.get('P279', []):
                #         if t.id == self.wd.enc_article_item:
                #             is_article = True
                # if not is_article:
                if e.target.id not in self.wd.types_to_search:
                    pwb.stdout('не словарная статья')
                    return

        text = p.page.get()
        p.wikicode = mwp.parse(text)
        # wikicode = mwp.parse('[[dffd|2222]][[Категория:апап|  33]]')
        for tpl in p.wikicode.filter_templates():
            p.tpl_data(tpl)
            if p.tpl_name in self.allowed_header_names:
                if [s for s in p.wikicode.filter_wikilinks(matches=r'^\[\[Категория:[^|]*?[Пп]еренаправления')]:
                    pwb.stdout('перенаправление')
                    return
                # фильтр по размеру текста
                # if p.tpl_name in ('МЭСБЕ', 'БЭАН'):
                if self.skip_by_text_lengh and not p.enc_with_trancludes:
                    tmp = text.replace(str(tpl), '')
                    for s in p.wikicode.filter_wikilinks(matches=r'^\[\[Категория:'): tmp = tmp.replace(str(s), '')
                    if len(tmp) < 100:
                        pwb.stdout('размер текста < 100')
                        return

                # if p.is_author_tpl is None: return
                p = self.process_params(p)

                # очищаем параметры, постим страницу
                # if p.params_to_delete or p.params_to_value_clear:
                summary = wiki_util.make_summary(p)
                wiki_util.page_posting(p.page, str(p.wikicode), summary, self.test_run)
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

    @abstractmethod
    def param_encyclopedia(self, p, pname, m_wp_pagename_raw):
        pass

    @abstractmethod
    def param_Wikipedia(self, p, pname, m_wp_pagename_raw):
        pass

    @abstractmethod
    def param_Image(self, p, pname, m_wp_pagename_raw):
        pass

    def pagegenerator_and_run(self):
        base_args = ['-family:wikisource', '-lang:ru', '-ns:0', '-format:"{page.can_title}"']
        args = base_args + sys.argv[1:]

        # if self.__class__.__name__ == 'Articles':
        #     import run_articles
        #     d = run_articles.Articles(test_run=False)

        gen = wiki_util.pagegenerator(args)
        # gen = wiki_util.get_pages(base_args, ['-catr:Авторы:Ручная_ссылка'], intersect=False)
        for page in gen:
            self.process_page(page)
