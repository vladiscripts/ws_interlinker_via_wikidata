#!/usr/bin/env python
import wiki_util
from main_class import Process
# from page_data import PageMeta
from __init__ import *
from pywikibot import pagegenerators, WikidataBot


class NewItemRobot(WikidataBot):
    pass


class Articles(Process):
    # works_pages_with_wditems: bool = True  # работать со страницами только имеющими элемент ВД
    require_ruwiki_sitelink: bool = False  # пропускать страницы если у элемента темы нет страницы в ruwiki
    # skip_wd_links_to_disambigs: bool = True  # не работать по словарным ссылкам на дизамбиги
    make_wd_links: bool = True  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc: bool = True  # работать только по элементам типов 'Q17329259', 'Q1580166' (энц. и словар. статьи)
    skip_existing_topics: bool = True  # Item уже имеет темы, отличные от ручной ссылки. Возможно в ручной ссылке - дизамбиг
    if_no_ruwiki_sitelink_in_item_then_leave_manual_ruwikilink_and_link_items: bool = True

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    # wikiprojects = ['ВИКИПЕДИЯ', ]
    # encyclopedies = ['ЭСБЕ', 'РСКД', 'ВЭ']
    # encyclopedies = enc_prefixes

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    def __init__(self, test_run: bool = False):
        super().__init__()
        self.test_run = test_run
        # self.allowed_header_names = tuple(s.lower() for s in ['отексте'] + list(self.enc_prefixes))
        self.allowed_header_names = tuple(['отексте', 'ЛЕНТАПЕДИЯ', 'Словарная статья'] + list(self.enc_prefixes))

    # def param_encyclopedia(self, p, name, m_enc):
    #     """ done для авторов
    #     """
    #     m_pagename_enc = self.wd.enc_meta[name].get('titleVT')  # 'Британника' и т.п.
    #     if not m_pagename_enc:
    #         pwb.stdout('нет m_pagename_enc')
    #         return
    #     m_pagename_enc = m_pagename_enc.replace('$1', m_enc)
    #
    #     topic_items = self.wd.get_topic_items(p.itemWD)
    #     if not topic_items:
    #         # pwb.stdout('темы не указаны в свойсте. Надо создать, пока пропускаем')
    #         return
    #
    #     # todo: исключить страницы /ДО, перенаправления, страницы произведений не энциклопедий
    #     # todo: ручная ссылка без статьи и ВД - Всеволод Михайлович Гаршин
    #
    #     m_enc_article_page = pwb.Page(self.wd.WS, m_pagename_enc)
    #     # if not m_enc_article_page.exists():  return
    #     m_enc_article_item = self.wd.get_item(self.wd.WS, page=m_enc_article_page)
    #     if not m_enc_article_item:
    #         pwb.stdout('нет m_enc_article_item')
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
    #                     pwb.stdout('ссылка на дизамбиг')
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
    #         p.params_to_delete.append(name)
    #         return
    #
    #     # # linksWD = self.get_wd_links()
    #     # # if not linksWD:
    #     # if not self.wd.link_():
    #     #     # self.wd.join_items_article_and_subject(name, m_enc, p.itemWD)
    #     #     pass

    def param_Wikipedia(self, p, param):
        self.disambigs(p, param)  # не работать по ссылкам на дизамбиги

        # добавить свойство "основная тема"
        self.wd.add_link_to_main_subject(p, param.item, self.make_wd_links, self.skip_existing_topics)
        self.chk_wd_links_and_remove_param(p, param)

    def param_Wikidata(self, p, param):
        self.disambigs(p, param)  # не работать по ссылкам на дизамбиги

        # добавить свойство "основная тема"
        self.wd.add_link_to_main_subject(p, param.item, self.make_wd_links, self.skip_existing_topics)
        self.chk_wd_links_and_remove_param(p, param)

    def chk_wd_links_and_remove_param(self, p, param):
        if self.wd.is_id_in_item_topics(p.itemWD, param.item.id) \
                and self.wd.is_id_in_item_describes(p, p.itemWD.id, param.item):

            if param.name == 'ВИКИДАННЫЕ':
                wiki_util.remove_param(p, param.name)
                return

            if param.sitelink_ruwiki:
                wiki_util.remove_param(p, param.name)

            else:
                if len(param.item.sitelinks) == 1:
                    pwb.stdout(f'no ru sitelink in WD, has only interwiki sitelink equals manual param, remove manual')
                    wiki_util.remove_param(p, param.name, value_only=True)

                else:
                    if f'{param.lang}wiki' in param.item.sitelinks:
                        # todo
                        if param.lang == 'en' \
                                or (param.lang == 'de' and 'enwiki' not in param.item.sitelinks):
                            wiki_util.remove_param(p, param.name, value_only=True)

                        elif self.if_no_ruwiki_sitelink_in_item_then_leave_manual_ruwikilink_and_link_items:
                            pwb.stdout('m_wp_page param linked with item, no ruwiki, leaved m_wp_page')
                        else:
                            wiki_util.remove_param(p, param.name, value_only=True)


# def parse(title):
#     page = pywikibot.Page(SITE, title)
#     text = page.get()
#     return mwparserfromhell.parse(text)

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
        # '-family:wikisource', '-lang:ru',
        # '-format:"{page.can_title}"',  # '-format:3',
        # '-ns:0'  # [f'-transcludes:{tpl}' for tpl in tpl_names]
        # '-page:ЭСБЕ/Василишки, местечко Виленской губернии',
        '-page:ЭСБЕ/Вехте',
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
        '-titleregexnot:^ТСД',
        # '-cat:Ручная ссылка:ВЭ',
        # '-cat:Ручная ссылка:ЭСБЕ‎',
        # '-cat:Ручная ссылка:Википедия|Ге',
        # '-cat:Викиданные:Статьи с указанным элементом темы',
        # '-catfilter:Викиданные:Есть элемент темы‎',
        # '-cat:Авторы:Ручная ссылка:ББСРП:Совпадает со ссылкой из Викиданных',
        # '-cat:Ручная ссылка совпадает со ссылкой из Викиданных:БСЭ1',  # done
        # '-cat:Ручная ссылка совпадает со ссылкой из Викиданных:Википедия‎',
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
        # '',
        # '-onlyif:P31=Q13433827',
        # '-onlyif:P31=Q17329259',
        # '-onlyif:P31=Q1580166',  # энц. и словар. статья
    ]

    d.pagegenerator_and_run()
