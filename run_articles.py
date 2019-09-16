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
from wd_utils import WD_utils
from get_other_sources_from_lua import get_other_sources
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
# # from vladi_helpers import vladi_helpers
from vladi_helpers.vladi_helpers import get_item_from_listdict
from main_class import PageMeta, Process

"""Перенос ссылок на энциклопедии/словари из статей в Викиданые и создание там записи."""
re_cat_redirect = re.compile(r'\[\[Категория:[^]]+?Перенаправления', flags=re.IGNORECASE)


# def parse(title):
#     page = pywikibot.Page(SITE, title)
#     text = page.get()
#     return mwparserfromhell.parse(text)


class Articles(Process):
    # works_pages_with_wditems = True  # работать со страницами только имеющими элемент ВД
    # require_ruwiki_sitelink_in_item = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    # skip_wd_links_to_disambigs = True  # не работать по словарным ссылкам на дизамбиги
    make_wd_links = True  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc = True  # работать только по элементам типов 'Q17329259', 'Q1580166' (энц. и словар. статьи)
    skip_existing_topics = True  # Item уже имеет темы, отличные от ручной ссылки. Возможно в ручной ссылке - дизамбиг

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    # wikiprojects = ['ВИКИПЕДИЯ', ]
    # encyclopedies = ['ЭСБЕ', 'РСКД', 'ВЭ']
    # encyclopedies = enc_prefixes

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    def __init__(self, test_run=False):
        super().__init__()
        self.test_run = test_run
        # self.allowed_header_names = tuple(s.lower() for s in ['отексте'] + list(self.enc_prefixes))
        self.allowed_header_names = tuple(['отексте', 'ЛЕНТАПЕДИЯ'] + list(self.enc_prefixes))

    # def param_encyclopedia(self, p, pname, m_enc):
    #     """ done для авторов
    #     """
    #     m_pagename_enc = self.wd.enc_meta[pname].get('titleVT')  # 'Британника' и т.п.
    #     if not m_pagename_enc:
    #         print('нет m_pagename_enc')
    #         return
    #     m_pagename_enc = m_pagename_enc.replace('$1', m_enc)
    #
    #     topic_items = self.wd.get_topic_items(p.itemWD)
    #     if not topic_items:
    #         # print('темы не указаны в свойсте. Надо создать, пока пропускаем')
    #         return
    #
    #     # todo: исключить страницы /ДО, перенаправления, страницы произведений не энциклопедий
    #     # todo: ручная ссылка без статьи и ВД - Всеволод Михайлович Гаршин
    #
    #     m_enc_article_page = pwb.Page(self.wd.WS, m_pagename_enc)
    #     # if not m_enc_article_page.exists():  return
    #     m_enc_article_item = self.wd.get_item(self.wd.WS, page=m_enc_article_page)
    #     if not m_enc_article_item:
    #         print('нет m_enc_article_item')
    #         return
    #
    #     # todo Создаются дубли описаний в темах. Проверить в unittest
    #     for topic_item in topic_items:
    #         while topic_item.isRedirectPage():
    #             topic_item = topic_item.getRedirectTarget()
    #         topic_item.get()
    #
    #         # не работать по ссылкам на дизамбиги
    #         if self.skip_wd_links_to_disambigs:
    #             for e in topic_item.claims.get(self.wd.item_type, []):
    #                 if e.target and e.target.id == self.wd.disambig:
    #                     print('ссылка на дизамбиг')
    #                     return
    #
    #     # todo создаёт дубли, или это было из-за повторного использования вд-свойств
    #     # if self.make_wd_links:
    #     #     if not self.wd.id_in_item_topics(p.itemWD, m_enc_article_item.id):
    #     #         # todo !!! указывает ссылки статей вместо ссылок темы
    #     #         self.wd.add_main_subject(p.itemWD, target=m_enc_article_item)
    #     #     if not self.wd.id_in_item_describes(p.rootpagename, p.itemWD.id, m_enc_article_item):
    #     #         self.wd.add_article_in_subjectitem(p.rootpagename, m_enc_article_item, p.itemWD)
    #
    #     if self.wd.id_in_item_topics(p.itemWD, m_enc_article_item.id) \
    #             and self.wd.id_in_item_describes(p.rootpagename, p.itemWD.id, m_enc_article_item):
    #         p.params_to_delete.append(pname)
    #         return
    #
    #     # # linksWD = self.get_wd_links()
    #     # # if not linksWD:
    #     # if not self.wd.link_():
    #     #     # self.wd.join_items_article_and_subject(pname, m_enc, p.itemWD)
    #     #     pass

    def param_Wikipedia(self, p, pname, m_wp_pagename_raw):
        WP, m_wp_pagename = self.wd.get_WPsite(m_wp_pagename_raw)
        if not WP:
            return

        m_wp_page_item = self.wd.get_item(WP, title=m_wp_pagename)
        if not m_wp_page_item:
            return

        topic_item = m_wp_page_item

        # if m_wp_page_item.sitelinks.get('ruwiki'):
        # if m_wp_pagename in m_wp_page_item.sitelinks.values():
        # if m_wp_pagename == ruwiki:

        # # очистить значение ВИКИПЕДИЯ
        # if self.wd.param_value_equal_item(p.rootpagename, m_wp_pagename, p.itemWD, m_wp_page_item):
        #     p.params_to_delete.append(pname)
        #     return
        #

        if topic_item.isRedirectPage():
            topic_item = topic_item.getRedirectTarget()
        topic_item.get()

        # не работать по ссылкам на дизамбиги
        if self.skip_wd_links_to_disambigs:
            for e in topic_item.claims.get(self.wd.item_type, []):
                if e.target and e.target.id == self.wd.disambig:
                    print('ссылка на дизамбиг')
                    return

        if self.require_ruwiki_sitelink_in_item:
            m_wp_sitelink = m_wp_page_item.sitelinks.get(f'ruwiki')
            if not m_wp_sitelink:
                return
            # if m_wp_pagename != m_wp_sitelink.title:  # страница может быть переименована
            #     return

        # todo слишком общие страницы в ВИКИПЕДИЯ, не имеет смысла их связывать с элементом

        # todo Создаются дубли описаний в темах. Проверить в unittest
        # добавить свойство "основная тема"
        if self.make_wd_links:
            if self.skip_existing_topics:
                if self.wd.another_id_in_item_topics(p.itemWD, m_wp_page_item.id):
                    print('Item уже имеет темы, отличные от ручной ссылки. Возможно в ручной ссылке - дизамбиг')
                    return

            if not self.wd.id_in_item_topics(p.itemWD, m_wp_page_item.id):
                self.wd.add_main_subject(p.itemWD, target=m_wp_page_item)
            if not self.wd.id_in_item_describes(p, p.itemWD.id, m_wp_page_item):
                self.wd.add_article_in_subjectitem(p.rootpagename, m_wp_page_item, p.itemWD)

        if self.wd.id_in_item_topics(p.itemWD, m_wp_page_item.id) \
                and self.wd.id_in_item_describes(p, p.itemWD.id, m_wp_page_item):
            p.params_to_delete.append(pname)
            return

        # # очистить значение ВИКИПЕДИЯ
        # if self.wd.param_value_equal_item(p.rootpagename, m_wp_pagename, p.itemWD, m_wp_page_item):
        #     return True

        # else:
        #     # подключаем указанный в ручную item
        #     # self.wd_item = pywikibot.ItemPage(WD, 'Q1057344')
        #     self.wd_item = pywikibot.ItemPage(self.WD, m_item_id)
        #     self.wd_item.get()
        #
        #     # if prj in self.wd_item.sitelinks and self.wd_item.getSitelink(prj) != self.page.title:
        #
        #     # в ВД другое значение
        #     if p.is_author_tpl:
        #         # if not prj in self.wd_item.sitelinks:
        #         # self.wd_item.setSitelink(sitelink={'site': prj, 'title': title}, summary='sitelink')
        #         pass
        #
        #         # проверяем запись и очищаем параметр
        #         if self.wd_item.getSitelink(self.prj) == self.page.title():
        #             mymwp.param_value_clear(tpl, param)
        #
        #     else:
        #         # self.wd_item.addClaim.claims.get(self.wd.main_subject)
        #
        #         claim = pywikibot.Claim(self.WD, self.wd.main_subject)
        #         target = pywikibot.ItemPage(self.WD, m_item_id)
        #         claim.setTarget(target)
        #         # self.wd_item.addClaim(claim, bot=self.as_bot, summary='add main subject')
        #
        #         # проверяем запись и очищаем параметр
        #         linksWD = [i.id for i in self.wd_item.claims.get(self.wd.main_subject)]
        #         if m_item_id in linksWD:
        #             mymwp.param_value_clear(tpl, param)
        #
        #         # if self.wd_item.getSitelink('ruwikisource') == m_item_id:
        #         #     self.wd_item.setSitelink(sitelink={'site': 'ruwikisource', 'title': title}, summary='sitelink')
        #         #     # todo: очистить значение ВИКИДАННЫЕ
        #         # else:
        #         #     # todo: поставить категорию что getSitelink('ruwikisource') занято др. значением
        #         #     pass
        #         # # # else:

    def param_Wikidata(self, p, pname, m_item_id):
        # tpl = self.tpl
        pname = 'ВИКИДАННЫЕ'
        r = False

        if not p.itemWD:
            # todo исключить страницы /ДО
            # подключаем указанный в ручную item
            # wd_item = pywikibot.ItemPage(WD, 'Q1057344')
            m_item = pwb.ItemPage(self.wd.WD, m_item_id)
            m_item.get()

            # if prj in wd_item.sitelinks and wd_item.getSitelink(prj) != self.page.title:

            # в ВД другое значение

            # todo: исключить страницы /ДО, перенаправления, страницы произведений не энциклопедий
            # self.wd_item.addClaim.claims.get(self.wd.main_subject)

            claim = pwb.Claim(self.wd.WD, self.wd.topic_subject)
            target = pwb.ItemPage(self.wd.WD, m_item_id)
            claim.setTarget(target)
            # m_item.addClaim(claim, bot=self.as_bot, summary='add main subject')

            # # проверяем запись и очищаем параметр
            # wd_item_ids = [i.id for i in self.wd_item.claims.get(self.wd.main_subject)]
            # if m_item_id in wd_item_ids:
            #     r = True
            #     # mymwp.param_value_clear(tpl, param)

            p.itemWD = p.page.data_item()
            p.itemWD.get()

        if p.itemWD:
            # if tplname.lower() == 'обавторе':
            # wd_itemIds = self.get_wd_links()

            # if self.wdlink(m_item_id, wd_itemIds):
            if self.wd.link_():
                # очистить значение ВИКИДАННЫЕ
                # mymwp.param_value_clear(tpl, param)
                pass
            else:
                # различаются значения в ручном параметре и в ВД
                pass

            # if self.wd_item.getSitelink('ruwikisource') == m_item_id:
            #     self.wd_item.setSitelink(sitelink={'site': 'ruwikisource', 'title': title}, summary='sitelink')
            #     # todo: очистить значение ВИКИДАННЫЕ
            # else:
            #     # todo: поставить категорию что getSitelink('ruwikisource') занято др. значением
            #     pass
            # # # else:


if __name__ == '__main__':
    # as_bot = True
    # test_run = False
    # wd = WD_utils(as_bot=as_bot, test_run=test_run)
    d = Articles(test_run=False)
    # pwb.Site().login()
    # d.works_pages_with_wditems = True

    # import author_tpl, articles

    # articles = articles.Articles(d)

    # ТЭ1/
    # pages = ['РСКД/Salarium', ]
    # pages = ['МЭСБЕ/Дионис', ]
    # pages = ['БСЭ1/А']
    # pages = ['РСКД/Libitina']
    # pages = ['БЭЮ/Абабды']  # нет элемента ВД
    # pages = ['ПБЭ/ВТ/Акоминат, Никита']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД
    # pages = ['РСКД/Thargelia']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД
    # pages = ['ЭСБЕ/Косва‎']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД

    # pages = ['МЭСБЕ/Аахен']
    # pages = ['Владимир Щербаненко']
    # pages = ['Юлий Таубин']

    # Pages generator
    # wiki_util.get_pages(tpl_names, test_pages = None, is_test_run = False)
    # args += ['-ns:0', '-cat:"Викитека:Ручная ссылка:Википедия"', '-catfilter:"Викитека:Ссылка из Викиданных:Викитека"', '-intersect']
    # без кавычек
    # from pywikibot import pagegenerators
    # query = """SELECT ?item ?sitelink WHERE {
    #     ?item wdt:P31 wd:Q17329259.
    #     ?sitelink schema:isPartOf <https://ru.wikisource.org/>;
    #      schema:about ?item.
    #     SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ru" }
    #     }
    #     LIMIT 300"""
    # generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    args = [
        '-family:wikisource', '-lang:ru',
        '-format:"{page.can_title}"',
        # '-format:3',
        # '-ns:0'  # [f'-transcludes:{tpl}' for tpl in tpl_names]
        # '-page:МЭСБЕ/Аахен',
        # '-page:БЭАН/Завет Ветхий и Новый',
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
        # '-cat:Ручная ссылка:ВЭ',
        # '-cat:Ручная ссылка:ЭСБЕ‎',
        # '-cat:Ручная ссылка:Википедия',
        # '-cat:Ссылка из Викиданных:Викитека',  # страница имеет itemWD
        # '-cat:Викиданные:Статьи с указанным элементом темы',
        # '-catfilter:Викиданные:Есть элемент темы‎',
        # '-cat:Авторы:Ручная ссылка:ББСРП:Совпадает со ссылкой из Викиданных',
        # '-cat:Ручная ссылка совпадает со ссылкой из Викиданных:БСЭ1',  # done
        # '-cat:Ручная ссылка совпадает со ссылкой из Викиданных:Википедия‎',
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
        # '-intersect',
    ]
    gen = wiki_util.get_pages(args)
    # gen = wiki_util.get_pages(base_args, ['-catr:Авторы:Ручная_ссылка'], intersect=False)
    for page in gen:
        d.process_page(page)
