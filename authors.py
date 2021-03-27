#!/usr/bin/env python
from __init__ import *
import wiki_util
from main_class import Process


class Author(Process):
    # works_pages_with_wditems: bool = True  # работать со страницами только имеющими элемент ВД
    # require_ruwiki_sitelink_in_item: bool = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    # make_wd_links: bool = False  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc: bool = False  # работать только по элементам типов 'Q17329259', 'Q1580166' (энц. и словар. статьи)
    # prj: str = 'ruwikisource'
    # allowed_header_names: bool = tuple(s.lower() for s in ('обавторе', 'об авторе', 'об_авторе'))
    allowed_header_names = ('обавторе', 'об авторе', 'об_авторе', 'Обавторе', 'Об авторе', 'Об_авторе')
    is_author_tpl: bool = True

    # enc_prefixes = []  # ['ЭСБЕ', 'РСКД', 'ВЭ']
    # wd = None

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    # wikiprojects = ['ВИКИПЕДИЯ', ]

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    # def __init__(self, test_run=False):
    #     super().__init__()
    #     self.test_run = test_run
    #     self.allowed_header_names = ['обавторе']
    #     # self.allowed_header_names.extend(self.enc_prefixes)

    def param_encyclopedia(self, p, param):
        """ done для авторов
        """
        # m_enc=param.pval_raw
        #
        # enc_pattern = self.wd.enc_meta[param.pname].get('titleVT')  # 'Британника' и т.п.
        # if not enc_pattern:
        #     return
        # param.pval_raw = enc_pattern.replace('$1', m_enc)

        # todo: ручная ссылка без статьи и ВД - Всеволод Михайлович Гаршин
        # todo: исключить страницы /ДО, перенаправления

        # wdlinks = self.wd.get_items(p.itemWD, self.is_author_tpl)
        # topic_item = wdlinks[0] if len(wdlinks) == 1 else None  # todo: проверить [0] или все links
        # topic_item = wdlinks[0] if len(wdlinks) == 1 else None  # todo: проверить [0] или все links
        # wd_item_ids = [itemWD]
        # for topic_item in wdlinks:
        topic_sitelink = p.itemWD.sitelinks['ruwikisource']

        m_enc_article_page = wiki_util.get_wikipage(self.wd.WS, page=param.pval_raw)
        if not m_enc_article_page.exists():
            return
        m_enc_article_item = m_enc_article_page.data_item()
        if not m_enc_article_item:
            return

        enc_article_sitelink = m_enc_article_item.sitelinks['ruwikisource']

        if self.skip_links_with_anchors and '#' in param.pval_raw:
            if param.pval_raw.partition('#')[0] == enc_article_sitelink:
                return
            # else:
            #     self.add_category('[[Категория:Ручная ссылка с якорем отличается от ссылки Викиданных]]')

        p.itemWD.get()
        if not self.wd.is_id_in_item_describes(param.pname, m_enc_article_item.id, p.itemWD):
            self.wd.add_article_in_subjectitem(param.pname, p.itemWD, m_enc_article_item)
        if self.wd.is_id_in_item_describes(pname, m_enc_article_item.id, p.itemWD):
            p.params_to_delete.append(param.pname)  # удалить параметр шаблона

            # # проверяем запись и очищаем параметр
            # linksWD = [i.id for i in self.wd_item.claims.get(Props.main_subject)]
            # if m_item_id in linksWD:
            #     r = True
            #     # mymwp.param_value_clear(tpl, param)

            # p.itemWD = self.page.data_item()
            # p.itemWD.get()
            #
            # # linksWD = self.get_wd_links()
            # # if not linksWD:
            # if not self.wd.link_():
            #     # self.wd.join_items_article_and_subject(pname, m_enc, p.itemWD)
            #     pass
            #
            # # if self.wdlink(m_item_id, linksWD):
            # if self.wd.link_():
            #     # очистить значение ВИКИДАННЫЕ
            #     return True
            # else:
            #     # различаются значения в ручном параметре и в ВД
            #     pass

    def param_Wikipedia(self, p, param):
        m_wp_pagename_raw = param.pval_raw

        # WP, m_wp_pagename = self.wd.get_WPsite(param.pval_raw)
        if not param.WP:
            return

        # m_enc_article_page = wiki_util.get_wikipage(self.wd.WS, page=m_pagename_enc)

        # param.item = self.wd.get_item(WP, title=m_wp_pagename)
        if not param.item:
            return

        if self.require_ruwiki_sitelink_in_item and param.item.sitelinks.get('ruwiki'):
            #     # if m_wp_pagename in m_wp_page_item.sitelinks.values():
            #     # if m_wp_pagename == ruwiki:
            #     if m_wp_pagename == m_wp_page_item.sitelinks.get(f'{WP.lang}wiki', ''):
            #         p.params_to_delete.append(pname)
            #         return

            sitelink = param.item.sitelinks.get(f'{param.WP.lang}wiki')
            if sitelink:
                if m_wp_pagename == sitelink.title:
                    p.params_to_delete.append(param.pname)
                    return

        # различаются значения в ручном параметре и в ВД
        # p.itemWD.sitelinks.get('ruwikisource')

        # # # очистить значение ВИКИПЕДИЯ
        # # # linksWD = self.get_wd_links()
        # # # if self.wdlink(m_itemId, linksWD):
        # if self.wdlink_():
        #     # p.params_to_delete.append(pname)
        #     pass
        #     # return True
        # # очистить значение ВИКИПЕДИЯ
        # if self.wd.param_value_equal_item(p.title, m_wp_pagename, self.itemWD, m_wp_page_item):
        #     return True

        # else:
        #     # подключаем указанный в ручную item
        #     # self.wd_item = pwb.ItemPage(WD, 'Q1057344')
        #     self.wd_item = pwb.ItemPage(self.WD, m_item_id)
        #     self.wd_item.get()
        #
        #     # if prj in self.wd_item.sitelinks and self.wd_item.getSitelink(prj) != self.page.title:
        #
        #     # в ВД другое значение
        #     if self.is_author_tpl:
        #         # if not prj in self.wd_item.sitelinks:
        #         # self.wd_item.setSitelink(sitelink={'site': prj, 'title': title}, summary='sitelink')
        #         pass
        #
        #         # проверяем запись и очищаем параметр
        #         if self.wd_item.getSitelink(self.prj) == self.page.title():
        #             mymwp.param_value_clear(tpl, param)
        #
        #     else:
        #         # self.wd_item.addClaim.claims.get(Props.main_subject)
        #
        #         claim = pwb.Claim(self.WD, Props.main_subject)
        #         target = pwb.ItemPage(self.WD, m_item_id)
        #         claim.setTarget(target)
        #         # self.wd_item.addClaim(claim, bot=self.as_bot, summary='add main subject')
        #
        #         # проверяем запись и очищаем параметр
        #         linksWD = [i.id for i in self.wd_item.claims.get(Props.main_subject)]
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

    def param_Wikidata(self, p, param):
        # tpl = self.tpl
        r = False
        m_item_id = param.pval_raw

        # item_id = pval
        # if p.itemWD:
        #     if p.itemWD.getSitelink('ruwikisource') == item_id:
        #         p.changed = mymwp.removeTplParameter(p.tpl, pname)  # очищаем параметр
        # else:
        #     # подключить элемент ВД
        #     p.itemWD = pwb.ItemPage(props.WD, item_id)
        #     p.itemWD.get()
        #     p.itemWD.setSitelink(sitelink={'site': 'ruwikisource', 'title': p.title},
        #                          summary='Set sitelink')

        if not p.itemWD:
            # todo исключить страницы /ДО
            # подключаем указанный в ручную item
            # wd_item = pwb.ItemPage(WD, 'Q1057344')
            m_item = pwb.ItemPage(self.wd.WD, m_item_id)
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

    def param_Image(self, p, param):
        # tpl = self.tpl
        # pname = 'ИЗОБРАЖЕНИЕ'

        # WP, m_wp_pagename = self.wd.get_WPsite(pvalue)
        # if not WP:
        #     return

        # m_wp_page_item = self.wd.get_item(self.wd.WP, title=m_wp_pagename)
        # if not m_wp_page_item:
        #     return
        # if self.require_ruwiki_sitelink_in_item and not m_wp_page_item.sitelinks.get('ruwiki'):
        #     return

        for c in p.itemWD.claims.get('P18', ()):  # 'preferred', 'normal'
            if c.target:
                if c.target.title(with_ns=False) == param.pval_raw:
                    p.params_to_delete.append(param.pname)  # очищаем параметр
                    return

        # if self.is_author_tpl:
        #     # различаются значения в ручном параметре и в ВД
        #     p.itemWD.sitelinks.get('ruwikisource')
        #     pass
        #     # # очистить значение ВИКИПЕДИЯ
        #     # # linksWD = self.get_wd_links()
        #     # # if self.wdlink(m_itemId, linksWD):
        #     if self.wdlink_():
        #         # mymwp.param_value_clear(tpl, param)
        #         pass
        #         return True
        #
        # else:
        #     # очистить значение ВИКИПЕДИЯ
        #     if self.wd.param_value_equal_item(p.rootpagename, m_wp_pagename, p.itemWD, m_wp_page_item):
        #         return True
        #
        #     if self.make_wd_links:
        #         # todo слишком общие страницы в ВИКИПЕДИЯ, не имеет смысла их связывать с элементом
        #         # добавить свойство "основная тема"
        #         if not self.wd.id_in_item_topics(m_wp_page_item.id, p.itemWD):
        #             self.wd.add_main_subject(p.itemWD, item=m_wp_page_item)
        #         # todo создаёт дубли, или это было из-за повторного использования вд-свойствв
        #         if not self.wd.id_in_item_describes(p.rootpagename, p.itemWD.id, m_wp_page_item):
        #             self.wd.add_article_in_subjectitem(p.rootpagename, m_wp_page_item, p.itemWD)
        #
        #         # очистить значение ВИКИПЕДИЯ
        #         if self.wd.param_value_equal_item(p.rootpagename, m_wp_pagename, p.itemWD, m_wp_page_item):
        #             return True


if __name__ == '__main__':
    # as_bot = True
    # test_run = False
    # wd = WD_utils(as_bot=as_bot, test_run=test_run)
    d = Author(test_run=False)
    # pwb.Site().login()
    d.works_pages_with_wditems = True

    # import author_tpl, articles

    # articles = articles.Articles(d)

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
        # '-cat:Авторы:Ручная ссылка:Изображение:Совпадает со ссылкой из Викиданных',
        # '-cat:Авторы:Ручная ссылка:ВЭ:Совпадает со ссылкой из Викиданных',
        # '-cat:Авторы:Ручная ссылка:РСКД',
        # '-cat:Авторы:Ручная ссылка:ПБЭ',
        '-cat:Авторы:Ручная ссылка:Википедия',
        # '-cat:Авторы:Ручная ссылка:МЭСБЕ',
        # '-cat:Авторы:Ручная ссылка:ЭСБЕ‎',
        # '-cat:Авторы:Ручная ссылка:Изображение',
        # '-cat:Авторы:Ручная ссылка:Изображение:Совпадает со ссылкой из Викиданных',
        # '-cat:Авторы:Ручная ссылка:ББСРП:Совпадает со ссылкой из Викиданных',
        # '-cat:Викитека:Ручная ссылка совпадает со ссылкой из Викиданных:БСЭ1',  # done
        '-cat:Авторы:Ссылка из Викиданных:Викитека',  # страница имеет itemWD
        # '-titleregex:(%s)' % '|'.join(d.enc_prefixes)
        # '-intersect',
        # '-file:/tmp/list.txt',
    ]
    # gen = wiki_util.get_pages(args)
    # # gen = wiki_util.get_pages(base_args, ['-catr:Авторы:Ручная_ссылка'], intersect=False)
    # for page in gen:
    #     d.process_page(page)

    d.pagegenerator_and_run()
