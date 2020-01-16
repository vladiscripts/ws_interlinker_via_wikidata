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
import pywikibot
import mwparserfromhell as mwp
import vladi_helpers.lib_for_mwparserfromhell as mymwp
import wiki_util
# from wikidata import wiki_util
from wd_utils import WD_utils, props
from get_other_sources_from_lua import get_other_sources
# from vladi_helpers.file_helpers import csv_save_dict_fromListWithHeaders, json_save_to_file, json_load_from_file
# # from vladi_helpers import vladi_helpers
from vladi_helpers.vladi_helpers import get_item_from_listdict

"""Перенос ссылок на энциклопедии/словари из статей в Викиданые и создание там записи."""
re_cat_redirect = re.compile(r'\[\[Категория:[^]]+?Перенаправления', flags=re.IGNORECASE)


# def parse(title):
#     page = pywikibot.Page(SITE, title)
#     text = page.get()
#     return mwparserfromhell.parse(text)


class Process:
    works_pages_with_wditems = True  # работать со страницами только имеющими элемент ВД
    require_ruwiki_page_via_item = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    make_wd_links = False  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc = False
    prj = 'ruwikisource'
    allowed_header_names = ['отексте', 'обавторе']
    enc_prefixes = []
    wd = None

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    wikiprojects = ['ВИКИПЕДИЯ', ]
    # encyclopedies = ['ЭСБЕ', 'РСКД', 'ВЭ']
    encyclopedies = enc_prefixes

    is_author_tpl = bool

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    def __init__(self, test_run=False):
        self.as_bot = True
        self.test_run = test_run
        self.wd = WD_utils(as_bot=self.as_bot, test_run=test_run)
        get_other_sources(self)
        self.allowed_header_names.extend(self.enc_prefixes)

    def author(self):
        # tpl_source_meta = get_item_from_listdict(other_sources, 'argument', tplname)
        # if not tpl_source_meta: continue
        if not self.is_author_tpl: return

        pfuncmap = {
            # 'ВИКИДАННЫЕ': self.param_Wikidata,  # сначала ВИКИДАННЫЕ
            # 'ВИКИПЕДИЯ': self.param_Wikipedia,
            # 'ИЗОБРАЖЕНИЕ': self.param_Image,
        }
        for param in self.tpl.params:
            pname = param.name.strip()
            pval = mymwp.get_param_value(self.tpl, pname)
            if not pval: continue

            # сначала ВИКИДАННЫЕ
            if pname == 'ВИКИДАННЫЕ':
                item_id = pval
                if self.itemWD:
                    if self.itemWD.getSitelink('ruwikisource') == item_id:
                        self.changed = mymwp.removeTplParameters(self.tpl, pname)  # очищаем параметр
                else:
                    # подключить элемент ВД
                    self.itemWD = pywikibot.ItemPage(self.wd.WD, item_id)
                    self.itemWD.get()
                    self.itemWD.setSitelink(sitelink={'site': 'ruwikisource', 'title': self.title},
                                            summary='Set sitelink')

            if pname == 'ИЗОБРАЖЕНИЕ':
                for c in self.itemWD.claims.get('P18'):  # 'preferred', 'normal'
                    if c.target._link._text == pval:
                        self.changed = mymwp.removeTplParameters(self.tpl, pname)  # очищаем параметр

                print()

            # if pname == 'ВИКИПЕДИЯ':

        # # различаются значения в ручном параметре и в ВД
        # self.itemWD.sitelinks.get('ruwikisource')
        # pass
        # # # очистить значение ВИКИПЕДИЯ
        # # # linksWD = self.get_wd_links()
        # # # if self.wdlink(m_itemId, linksWD):
        # if self.wdlink_():
        #     # mymwp.param_value_clear(tpl, param)
        #     pass
        #     return True

        #     if pname in pfuncmap.keys() or pname in self.encyclopedies:
        #         pval = mymwp.get_param_value(self.tpl, pname)
        #         if not pval: continue
        #         cleanParam = False
        #
        #         # параметры проектов
        #         if pname in pfuncmap.keys():
        #             func = pfuncmap.get(pname)
        #             cleanParam = func(pname, pval)
        #
        #         # параметры словарей
        #         # elif pname in self.encyclopedies:
        #         #     r = self.param_encyclopedia(pname, pval)
        #         #     pass
        #
        #         # очищаем параметр
        #         if cleanParam and not self.test_run:
        #             # mymwp.param_value_clear(self.tpl, pname, new_val='\n')
        #             mymwp.removeTplParameters(self.tpl, pname)
        #             changed = True
        #
        # if changed:
        #     wiki_util.page_posting(self.page, str(self.wikicode), self.test_run)

        #
        #
        # # сначала ВИКИДАННЫЕ
        # item_id = params.get('ВИКИДАННЫЕ')
        # if item_id:
        #     if not self.itemWD:
        #         # pval
        #         # wd_item = pywikibot.ItemPage(WD, 'Q1057344')
        #         self.itemWD = pywikibot.ItemPage(self.wd.WD, item_id)
        #         self.itemWD.get()
        #         self.itemWD.setSitelink(sitelink={'site': 'ruwikisource', 'title': title}, summary='Set sitelink')
        #     else:
        #         if self.itemWD.getSitelink('ruwikisource') == item_id:
        #             pass
        #
        # # далее ВИКИПЕДИЯ
        # wp_value = params.get('ВИКИПЕДИЯ')
        #
        # for pname, pval in params.items():
        #     if pname == 'ВИКИПЕДИЯ' and pval != '':
        #         # link_lngcode = None
        #         # link_pname = pval
        #         # if ':' in pval:
        #         #     link_lngcode, link_pname = pval.split(':')
        #         # wpsite_tmp = pywikibot.Site(code=link_lngcode, fam='wikipedia')
        #         # wp_page_tmp = pywikibot.Page(wpsite_tmp, link_pname)
        #         # wp_page_item_tmp = wp_page_tmp.data_item()
        #         # k = pywikibot.Link(pval)
        #
        #         lnk_tmp = pywikibot.Link(pval, source=self.wd.WP)
        #         # lng_tmp = lnk_tmp.site
        #         lang_tmp = lnk_tmp.parse_site()[1]
        #         # lnk_tmp.canonical_title()
        #
        #         try:
        #             title_tmp = lnk_tmp.title
        #         except pywikibot.exceptions.SiteDefinitionError:
        #             '''Вероятно нестандартный языковый код страницы'''
        #             continue
        #
        #         WP_tmp = pywikibot.Site(lang_tmp, 'wikipedia')
        #         wp_page_tmp = pywikibot.Page(WP_tmp, link_pname)
        #         wp_page_item_tmp = wp_page_tmp.data_item()
        #
        #         # WPt = pywikibot.Site(lng, 'wikipedia')
        #         # pywikibot.Link(pval, source=WPt).title
        #
        #         # pywikibot.Link('Юлий Таубин', source=page)
        #         # pywikibot.Link('Юлий Таубин', source=WP)
        #         ws_topic_item = page.data_item()
        #         # wp_topic_item = pywikibot.Page(WP, pval).data_item()
        #         wp_topic_item = site_tmp.data_item()
        #         print()

        # for pname, pval in params.items():
        #     if pval == '': continue
        #
        #     if pname == 'ВИКИПЕДИЯ':
        #         # wp_topic_item = pywikibot.Page(WP, 'Дионис').data_item()
        #         # Todo: дисамбиги, 'w:А'
        #         wp_topic_item = pywikibot.Page(self.WP, pval).data_item()
        #
        #         o = wp_topic_item.claims['P1343'][5]
        #
        #         prop = 'P1343'  # described_by_source
        #         srcs = 'P805'  # тема утверждения
        #         if prop in wp_topic_item.claims:
        #             for c in wp_topic_item.claims['P1343']:
        #
        #                 # наличие что в ссылках на источники уже есть данный
        #                 if tpl_source_meta and c.target.id == tpl_source_meta['id']:
        #                     if srcs in c.qualifiers:
        #                         for q in c.qualifiers:
        #                             enc_item = q.get(srcs)[0].target
        #                             # if nameid in s:    name = s.get(nameid)[0].target['text']
        #                             # print(url, name)
        #                             # if urlid in s:     url = s.get(urlid)[0].target
        #
        #     source_meta = get_item_from_listdict(self.other_sources, 'argument', pname)
        #     if source_meta:
        #         if pname in wikiprojects:
        #             # v = p.value.strip()
        #
        #             pass
        #             # item=pywikibot.ItemPage.fromPage(page)
        #             item = page.data_item()
        #             sitelinks = item.sitelinks
        #
        #             prop = 'P921'
        #             for c in item.claims:
        #                 if prop in item.claims:
        #                     target_item = c.getTarget()
        #                     # print(claim.sources[0])

    def init_page(self, page):
        self.p = PageMeta(page)
        # self.page = pywikibot.Page(self.wd.WS, title)
        # todo:  if not page.revisions[0].patroled.since >= 5days: return

        # пропускать страницы-перенаправления
        if re_cat_redirect.search(page.text):
            return

        self.itemWD = self.wd.get_item(self.wd.WS, page=self.p.page)
        if self.works_pages_with_wditems and not self.itemWD:
            return

        # работать по энциклопедическая статья и словарная статья
        if self.work_only_enc:
            for e in self.itemWD.claims.get(props.item_type, []):
                if e.target.id not in props.types_to_search:
                    return

        self.p.title = page.title()
        self.p.rootpagename, self.p.pagename = wiki_util.parse_pagename(self.p.title)
        print(self.p.title)

        text = self.p.page.get()
        wikicode = mwp.parse(text)
        for tpl in wikicode.filter_templates():
            for allowed_header_name in self.allowed_header_names:
                if tpl.name.strip().lower() == allowed_header_name.lower():

                    import author_tpl
                    author_tpl.tpl_process(self)

                    self.p.set_tpl(tpl)
                    if self.p.is_author_tpl:
                        author.params_process(self.p)
                    elif not self.p.is_author_tpl:
                        d.tpl_process()
                    else:
                        return

        if self.changed:
            wiki_util.page_posting(self.page, str(wikicode), self.test_run)

    # def author_despatcher(self, params):
    # def despatcher_tpl(self, tplname, params):
    def despatcher_tpl(self):
        # v = tpl.get('КАЧЕСТВО').value.strip()
        # wp = tpl.get('ВИКИПЕДИЯ').value.strip()
        # for param in tpl.listhas('КАЧЕСТВО'):
        #     for p in tpl.params:
        #         pname = p.name.strip()
        #
        #         tpl.params[0].name.strip()
        #         if pname in header_names:
        #             wp = tpl.get('ВИКИПЕДИЯ').value.strip()
        #         wp_topic_item.id

        # сначала ВИКИДАННЫЕ
        self.param_Wikidata()

        # {{обавторе}}
        for tplname, params in self.page.raw_extracted_templates:
            if self.is_author_tpl:
                self.author(params)

        # for tplname, params in page.raw_extracted_templates:
        #     if tplname.upper() not in header_names: continue
        #
        #     tpl_source_meta = get_item_from_listdict(self.other_sources, 'argument', tplname)
        #     if not tpl_source_meta: continue

    # def clear_parameter(self, param):
    #     """Очистка параметра шаблона"""
    #     # if tpl.has(param):
    #     self.tpl.get(param).value = ''

    def tpl_process(self):
        changed = False
        pfuncmap = {
            # 'ВИКИДАННЫЕ': self.param_Wikidata,  # сначала ВИКИДАННЫЕ
            'ВИКИПЕДИЯ': self.param_Wikipedia,
            # 'ИЗОБРАЖЕНИЕ': self.param_Image,
        }

        # if self.is_author_tpl:
        #     self.author()

        for param in self.tpl.params:
            pname = param.name.strip()
            if not (pname in pfuncmap.keys() or pname in self.encyclopedies): continue
            pval = mymwp.get_param_value(self.tpl, pname)
            if not pval: continue
            cleanParam = False

            if not self.is_author_tpl and pname == self.rootpagename:
                # параметр дублирует rootpagename
                cleanParam = True

            # параметры проектов
            elif pname in pfuncmap.keys():
                # func = pfuncmap.get(pname)
                # cleanParam = func(pname, pval)
                pass

            # параметры словарей
            elif pname in self.encyclopedies:
                cleanParam = self.param_encyclopedia(pname, pval)
                pass

            # очищаем параметр
            if cleanParam and not self.test_run:
                # mymwp.param_value_clear(self.tpl, pname, new_val='\n')
                mymwp.removeTplParameters(self.tpl, pname)
                changed = True

        if changed:
            wiki_util.page_posting(self.page, str(self.wikicode), self.test_run)

    def param_encyclopedia(self, pname, m_enc):
        """ done для авторов
        """
        tpl = self.tpl
        # pagename_enc = self.wd.enc_meta[pname]['argument'].replace('$1', m_enc)
        pagename_enc = self.wd.enc_meta[pname]['titleVT'].replace('$1', m_enc)
        # param = 'ВИКИПЕДИЯ'
        # m_item_id = mymwp.param_value_or_none(tpl, param)
        # if m_item_id:

        # if not self.itemWD:
        # if prj in wd_item.sitelinks and wd_item.getSitelink(prj) != self.page.title:

        if not self.itemWD:
            return

        # todo исключить страницы /ДО
        # todo: ручная ссылка без статьи и ВД - Всеволод Михайлович Гаршин

        # в ВД другое значение
        # if self.is_author_tpl:

        # if not prj in self.wd_item.sitelinks:
        # enc_article_item.setSitelink(sitelink={'site': prj, 'title': title}, summary='sitelink')
        pass

        # # проверяем запись и очищаем параметр
        # if enc_article_item.getSitelink(self.prj) == self.page.title():
        #     r = True
        #     # mymwp.param_value_clear(tpl, param)

        # else:
        # подключаем указанный в ручную item
        # todo: исключить страницы /ДО, перенаправления, страницы произведений не энциклопедий

        wdlinks = self.wd.get_items(self.itemWD, self.is_author_tpl)
        # topic_item_id = wdlinks[0] if len(wdlinks) == 1 else None  # todo: проверить [0] или все links
        topic_item = wdlinks[0] if wdlinks else None  # todo: проверить [0] или все links

        # m_enc = 'Q1057344'
        # enc_article_item = self.wd.get_item(self.wd.WS, title=m_enc)
        enc_article_item = self.wd.get_item(self.wd.WS, title=pagename_enc)

        if topic_item and enc_article_item:
            topic_item.get()
            # todo создаёт дубли, или это было из-за повторного использования вд-свойствв
            if self.is_author_tpl:
                if not self.wd.is_id_in_item_describes(pname, enc_article_item.id, self.itemWD):
                    self.wd.add_article_in_subjectitem(pname, self.itemWD, enc_article_item)
                if self.wd.is_id_in_item_describes(pname, enc_article_item.id, self.itemWD):
                    # очистить значение ВИКИДАННЫЕ
                    return True
            else:

                if not self.wd.is_id_in_item_describes(pname, enc_article_item.id, topic_item):
                    self.wd.add_article_in_subjectitem(pname, topic_item, enc_article_item)
                if not self.wd.is_id_in_item_describes(pname, enc_article_item.id, topic_item):
                    # очистить значение ВИКИДАННЫЕ
                    return True

            # # проверяем запись и очищаем параметр
            # linksWD = [i.id for i in self.wd_item.claims.get(Props.main_subject)]
            # if m_item_id in linksWD:
            #     r = True
            #     # mymwp.param_value_clear(tpl, param)

            # self.itemWD = self.page.data_item()
            # self.itemWD.get()
            #
            # # linksWD = self.get_wd_links()
            # # if not linksWD:
            # if not self.wd.link_():
            #     # self.wd.join_items_article_and_subject(pname, m_enc, self.itemWD)
            #     pass
            #
            # # if self.wdlink(m_item_id, linksWD):
            # if self.wd.link_():
            #     # очистить значение ВИКИДАННЫЕ
            #     return True
            # else:
            #     # различаются значения в ручном параметре и в ВД
            #     pass

    def param_Wikipedia(self, pname, m_wp_pagename_raw):
        tpl = self.tpl
        # pname = 'ВИКИПЕДИЯ'
        if self.itemWD:
            WP, m_wp_pagename = self.wd.get_WPsite(m_wp_pagename_raw)
            if not WP:
                return

            m_wp_page_item = self.wd.get_item(WP, title=m_wp_pagename)
            if not m_wp_page_item:
                return
            if self.require_ruwiki_page_via_item and not m_wp_page_item.sitelinks.get('ruwiki'):
                return

            if self.is_author_tpl:
                # различаются значения в ручном параметре и в ВД
                self.itemWD.sitelinks.get('ruwikisource')
                pass
                # # очистить значение ВИКИПЕДИЯ
                # # linksWD = self.get_wd_links()
                # # if self.wdlink(m_itemId, linksWD):
                if self.wdlink_():
                    # mymwp.param_value_clear(tpl, param)
                    pass
                    return True

            else:
                # очистить значение ВИКИПЕДИЯ
                if self.wd.is_param_value_equal_item(self.rootpagename, m_wp_pagename, self.itemWD, m_wp_page_item):
                    return True

                if self.make_wd_links:
                    # todo слишком общие страницы в ВИКИПЕДИЯ, не имеет смысла их связывать с элементом
                    # добавить свойство "основная тема"
                    if not self.wd.is_id_in_item_topics(self.itemWD, m_wp_page_item.id):
                        self.wd.add_main_subject(self.itemWD, target=m_wp_page_item)
                    # todo создаёт дубли, или это было из-за повторного использования вд-свойствв
                    if not self.wd.is_id_in_item_describes(self.rootpagename, self.itemWD.id, m_wp_page_item):
                        self.wd.add_article_in_subjectitem(self.rootpagename, m_wp_page_item, self.itemWD)

                    # очистить значение ВИКИПЕДИЯ
                    if self.wd.is_param_value_equal_item(self.rootpagename, m_wp_pagename, self.itemWD, m_wp_page_item):
                        return True

    def param_Wikidata(self, pname, m_item_id):
        tpl = self.tpl
        pname = 'ВИКИДАННЫЕ'
        r = False

        if not self.itemWD:
            # todo исключить страницы /ДО
            # подключаем указанный в ручную item
            # wd_item = pywikibot.ItemPage(WD, 'Q1057344')
            m_item = pywikibot.ItemPage(self.wd.WD, m_item_id)
            m_item.get()

            # if prj in wd_item.sitelinks and wd_item.getSitelink(prj) != self.page.title:

            # в ВД другое значение
            if self.is_author_tpl:
                # m_item.setSitelink(sitelink={'site': prj, 'title': title}, summary='sitelink')
                pass

                # # проверяем запись и очищаем параметр
                # if m_item.getSitelink(self.prj) == self.page.title():
                #     r = True
                #     # mymwp.param_value_clear(tpl, param)

            else:
                # todo: исключить страницы /ДО, перенаправления, страницы произведений не энциклопедий
                # self.wd_item.addClaim.claims.get(Props.main_subject)

                claim = pywikibot.Claim(self.wd.WD, props.topic_subject)
                target = pywikibot.ItemPage(self.wd.WD, m_item_id)
                claim.setTarget(target)
                # m_item.addClaim(claim, bot=self.as_bot, summary='add main subject')

                # # проверяем запись и очищаем параметр
                # wd_item_ids = [i.id for i in self.wd_item.claims.get(Props.main_subject)]
                # if m_item_id in wd_item_ids:
                #     r = True
                #     # mymwp.param_value_clear(tpl, param)

            self.itemWD = self.page.data_item()
            self.itemWD.get()

        if self.itemWD:
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

    def param_author_Image(self, pname, pvalue):
        tpl = self.tpl
        # pname = 'ИЗОБРАЖЕНИЕ'
        if self.itemWD:
            # WP, m_wp_pagename = self.wd.get_WPsite(pvalue)
            # if not WP:
            #     return

            m_wp_page_item = self.wd.get_item(WP, title=m_wp_pagename)
            if not m_wp_page_item:
                return
            if self.require_ruwiki_page_via_item and not m_wp_page_item.sitelinks.get('ruwiki'):
                return

            if self.is_author_tpl:
                # различаются значения в ручном параметре и в ВД
                self.itemWD.sitelinks.get('ruwikisource')
                pass
                # # очистить значение ВИКИПЕДИЯ
                # # linksWD = self.get_wd_links()
                # # if self.wdlink(m_itemId, linksWD):
                if self.wdlink_():
                    # mymwp.param_value_clear(tpl, param)
                    pass
                    return True

            else:
                # очистить значение ВИКИПЕДИЯ
                if self.wd.is_param_value_equal_item(self.rootpagename, m_wp_pagename, self.itemWD, m_wp_page_item):
                    return True

                if self.make_wd_links:
                    # todo слишком общие страницы в ВИКИПЕДИЯ, не имеет смысла их связывать с элементом
                    # добавить свойство "основная тема"
                    if not self.wd.is_id_in_item_topics(self.itemWD, m_wp_page_item.id):
                        self.wd.add_main_subject(self.itemWD, target=m_wp_page_item)
                    # todo создаёт дубли, или это было из-за повторного использования вд-свойствв
                    if not self.wd.is_id_in_item_describes(self.rootpagename, self.itemWD.id, m_wp_page_item):
                        self.wd.add_article_in_subjectitem(self.rootpagename, m_wp_page_item, self.itemWD)

                    # очистить значение ВИКИПЕДИЯ
                    if self.wd.is_param_value_equal_item(self.rootpagename, m_wp_pagename, self.itemWD, m_wp_page_item):
                        return True


class PageMeta:
    changed = False
    page = None
    title = str
    rootpagename = str
    pagename = str
    tpl = None
    tplname = str
    is_author_tpl = bool

    def __init__(self, page):
        self.title = page.title()
        self.rootpagename, self.pagename = wiki_util.parse_pagename(self.title)

    def set_tpl(self, tpl):
        self.tpl = tpl
        self.tplname = tpl.name.strip()
        self.is_author_tpl = (self.tplname.lower() == 'обавторе')


def init_page(page):
    p = PageMeta(page)

    # self.page = pywikibot.Page(self.wd.WS, title)
    # todo:  if not page.revisions[0].patroled.since >= 5days: return

    # пропускать страницы-перенаправления
    if re_cat_redirect.search(page.text):
        return

    p.itemWD = d.wd.get_item(d.wd.WS, page=p.page)
    if d.works_pages_with_wditems and not d.itemWD:
        return

    # работать по энциклопедическая статья и словарная статья
    if d.work_only_enc:
        for e in p.itemWD.claims.get(props.item_type, []):
            if e.target.id not in props.types_to_search:
                return

    print(d.title)

    text = p.page.get()
    d.wikicode = mwp.parse(text)
    for tpl in d.wikicode.filter_templates():
        for allowed_header_name in d.allowed_header_names:
            if tpl.name.strip().lower() == allowed_header_name.lower():
                p.set_tpl(tpl)
                if p.is_author_tpl:
                    author.params_process(d)
                elif not p.is_author_tpl:
                    d.tpl_process()
                else:
                    return

    if p.changed:
        wiki_util.page_posting(p.page, str(d.wikicode), d.test_run)


if __name__ == '__main__':
    d = Process(test_run=False)
    # pywikibot.Site().login()
    d.works_pages_with_wditems = True

    import author_tpl

    author = author_tpl.Author(d)

    # ТЭ1/
    pages = ['РСКД/Salarium', ]
    pages = ['МЭСБЕ/Дионис', ]
    # pages = ['БСЭ1/А']
    # pages = ['РСКД/Libitina']
    # pages = ['БЭЮ/Абабды']  # нет элемента ВД
    pages = ['ПБЭ/ВТ/Акоминат, Никита']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД
    # pages = ['РСКД/Thargelia']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД
    # pages = ['ЭСБЕ/Косва‎']  # есть элемент, есть ручная ссылка ВП, нет связи через ВД

    # pages = ['МЭСБЕ/Аахен']
    # pages = ['Владимир Щербаненко']
    # pages = ['Юлий Таубин']

    # Pages generator
    # wiki_util.get_pages(tpl_names, test_pages = None, is_test_run = False)
    base_args = ['-family:wikisource', '-lang:ru',
                 # '-format:3',
                 # '-ns:0'
                 ]  # [f'-transcludes:{tpl}' for tpl in tpl_names]
    # args += ['-ns:0', '-cat:"Викитека:Ручная ссылка:Википедия"', '-catfilter:"Викитека:Ссылка из Викиданных:Викитека"', '-intersect']
    # без кавычек
    args = [
        '-cat:Викитека:Ручная ссылка:Википедия',
        '-cat:Викитека:Ссылка из Викиданных:Викитека',  # страница имеет itemWD
        #     '-catr:"Категория:РБС:Поэты"',
        #     '-cat:РБС:Поэты',
        # '-page:МЭСБЕ/Аахен',
        # '-page:ЭСБЕ/Венецуэла',
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
    ]
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
        # '-cat:Авторы:Ручная ссылка:Изображение:Совпадает со ссылкой из Викиданных',
        # '-cat:Авторы:Ручная ссылка:ВЭ:Совпадает со ссылкой из Викиданных',  # done
        '-cat:Викитека:Ручная ссылка совпадает со ссылкой из Викиданных:БСЭ1',  # done
        # '-cat:Викитека:Ссылка из Викиданных:Викитека',  # страница имеет itemWD
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
    ]
    gen = wiki_util.pagegenerator(base_args, args, intersect=True)
    # pages = tuple(p.title() for p in gen)
    for page in gen:
        # d.init_page(page)
        init_page(d, page)
