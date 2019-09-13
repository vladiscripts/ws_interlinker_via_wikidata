#!/usr/bin/env python
# coding: utf-8
import requests
import sqlite3
import json
from lxml.html import fromstring
import re
from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote, quote
# from vladi_helpers import vladi_helpers
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_store_to_file, json_data_from_file
from typing import Iterable, Union
import pywikibot as pwb
from pywikibot.page import ItemPage
import copy
# import mwparserfromhell as mwp
import vladi_helpers.lib_for_mwparserfromhell as mymwp


class WD_utils:
    item_type = 'P31'
    types_to_search = 'Q17329259', 'Q1580166'  # энц. и словар. статья
    topic_subject = 'P921'  # основная тема
    described_by_source = 'P1343'  # описывается в источниках
    dedicated_article = 'P805'  # тема утверждения
    disambig = 'Q4167410'  # дизамбиг, страница значений в проекте Викимедиа

    sites = {
        'ruwikisource': pwb.Site('ru', 'wikisource', user='TextworkerBot'),
        'ruwikipedia': pwb.Site('ru', 'wikipedia', user='TextworkerBot'),
    }
    WS = sites['ruwikisource']
    WP = sites['ruwikipedia']
    WD = WS.data_repository()

    _claim_main_subject = pwb.Claim(WD, topic_subject)
    _claim_described_by_source = pwb.Claim(WD, described_by_source)
    _claim_dedicated_article = pwb.Claim(WD, dedicated_article)

    enc_meta = {}

    def __init__(self, as_bot=False, test_run=False):
        self.as_bot = as_bot
        self.test_run = test_run

    def get_topic_items(self, itemWD):
        return [i.target for i in itemWD.claims.get(self.topic_subject, []) if isinstance(i.target, ItemPage)]

    def claim_main_subject(self):
        # return pwb.Claim(self.WD, self.topic_subject)
        return copy.deepcopy(self._claim_main_subject)

    def claim_described_by_source(self):
        # return pwb.Claim(WD, self.described_by_source)
        return copy.deepcopy(self._claim_described_by_source)

    def claim_dedicated_article(self):
        # return pwb.Claim(WD, self.dedicated_article)
        return copy.deepcopy(self._claim_dedicated_article)

    @staticmethod
    def link(item_id: str, items: Union[list, tuple]):
        for i in items:
            if i.id == item_id:
                return True

    def link_(self, item_id: str = None, title: str = None):
        items = self.get_items(itemWD, is_author_tpl)
        if item_id:
            for i in items:
                if i.id == item_id:
                    return True

    def id_in_item_describes(self, rootpagename: str, search_id: str, item: ItemPage) -> bool:
        enc_item = self.enc_meta[rootpagename]['wditem']
        if enc_item:
            for c in item.claims.get(props.described_by_source, []):
                if enc_item.id == c.target.id:
                    for q in c.qualifiers.get(self.dedicated_article, []):
                        if q.target.id == search_id:
                            return True

    def id_in_item_topics(self, search_id: str, item: ItemPage) -> bool:
        for i in item.claims.get(props.topic_subject, []):
            if i.target.id == search_id:
                return True

    def param_value_equal_item(self, rootpagename: str, m_wp_pagename: str, itemWD: ItemPage,
                               m_wp_page_item: ItemPage) -> bool:
        if self.id_in_item_describes(rootpagename, itemWD.id, m_wp_page_item) \
                and self.id_in_item_topics(m_wp_page_item.id, itemWD):
            print(f'значение параметра ("{m_wp_pagename}") совпадает с item (label {m_wp_page_item.labels.get("ru")})')
            return True

    # def is_item_of_disambig(self, item: ItemPage) -> bool:
    #     for e in item.claims.get(self.item_type, []):
    #         if e.target and e.target.id == self.disambig:
    #             return True

    def _join_items_article_and_subject(self, pname: str, subject_item_id: str, target_item: ItemPage):
        # создать ссылку на элемент темы
        wditem_subject = self.add_main_subject(item_id=subject_item_id)

        # создать "описывается в источниках" в элементе темы
        if wditem_subject:
            self.add_article_in_subjectitem(wditem_subject, pname, target_item)

    def add_main_subject(self, itemWD: ItemPage, item_id: str = None, item: ItemPage = None):
        """ создать ссылку на элемент темы """
        claim_topic_subject = self.claim_main_subject()
        pwb.Claim(self.WD, self.topic_subject)
        if item_id:
            wditem_subject = pwb.ItemPage(self.WD, item_id)
        elif item:
            wditem_subject = item
        else:
            return
        # target = wd_item_ids[0]
        claim_topic_subject.setTarget(wditem_subject)
        if self.test_run:
            return
        itemWD.addClaim(claim_topic_subject, bot=self.as_bot, summary='+main subject; moved from ruwikisource')
        print(f'add main subject in item')

    def add_article_in_subjectitem(self, rootpagename: str,
                                   subject_item: ItemPage,
                                   target_item: ItemPage):
        """ создать "описывается в источниках" в элементе темы """
        # s = get_item_from_listdict(other_sources, 'argument', m_item_id)
        # [i.target for i in self.wd_item.claims.get(self.main_subject, [])]
        claim_described_by = self.claim_described_by_source()
        target = self.enc_meta[rootpagename]['wditem']
        claim_described_by.setTarget(target)
        qualifier = self.claim_dedicated_article()
        # qualifier_target = pwb.ItemPage(self.WD, m_item_id)
        qualifier.setTarget(target_item)
        claim_described_by.addQualifier(qualifier)
        if self.test_run:
            return
        subject_item.addClaim(claim_described_by, bot=self.as_bot,
                              summary='+described by source; moved from ruwikisource')
        print(f'add item of article in subject item')

    def get_item(self, site, item_id: str = None, title: str = None, page=None):
        item = None
        try:
            if item_id:
                item = pwb.ItemPage(site, item_id)
            elif title:
                page = pwb.Page(site, title)
                item = page.data_item()
            elif page:
                item = page.data_item()
            item.get()
        except pwb.exceptions.NoPage:
            item = None
        return item

    def get_WPsite(self, pagename_raw):
        # .target.title(with_ns=False)
        lnk_tmp = pwb.Link(pagename_raw, source=self.WP)
        lang_tmp = lnk_tmp.parse_site()[1]
        try:
            title_tmp = lnk_tmp.title
        except pwb.exceptions.SiteDefinitionError:
            '''Вероятно нестандартный языковый код страницы'''
            return None, None
        WP = self.sites.get(lang_tmp + 'wikipedia')
        if not WP:
            WP = self.sites[lang_tmp + 'wikipedia'] = pwb.Site(lang_tmp, 'wikipedia')
        return WP, title_tmp
