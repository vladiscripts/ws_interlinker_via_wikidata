#!/usr/bin/env python
from pywikibot.page import ItemPage
from __init__ import *
from wd_work import props, Get_claims, Claim_instance


class WD_utils:
    user = 'TextworkerBot'
    sites = {'ruwikisource': pwb.Site('ru', 'wikisource', user=user),
             'ruwikipedia': pwb.Site('ru', 'wikipedia', user=user)}
    WS = sites['ruwikisource']
    WP = sites['ruwikipedia']
    WD = WS.data_repository()

    re_is_item_id = re.compile(r'^Q\d+$')

    def __init__(self, as_bot: bool = True, test_run: bool = False):
        self.as_bot = as_bot
        self.test_run = test_run
        self.get_claims = Get_claims()
        self.claim_instance = Claim_instance(self.WD)

    # def get_topic_items(self, itemWD: ItemPage):
    #     return [i.target for i in self.get_claims.topics(itemWD) if isinstance(i.target, ItemPage)]

    @staticmethod
    def is_link(item_id: str, items: Union[list, tuple]):
        for i in items:
            if i.id == item_id:
                return True

    # def link_(self, item_id: str = None, title: str = None):
    #     items = self.get_items(itemWD, is_author_tpl)
    #     if item_id:
    #         for i in items:
    #             if i.id == item_id:
    #                 return True

    def is_id_in_item_describes(self, p, search_id: str, item: ItemPage) -> bool:
        rootpagename = p.rootpagename
        if rootpagename == 'Лентапедия' and p.title.endswith('/Полная версия'):
            rootpagename = 'Лентапедия2'
        enc_item = p.enc_meta['wditem']
        if enc_item:
            for c in self.get_claims.described_by_source(item):
                if enc_item.id == c.target.id:
                    for q in self.get_claims.get_qualifiers_dedicated_article(c):
                        if q.target.id == search_id:
                            return True

    def is_id_in_item_topics(self, item: ItemPage, search_id: str) -> bool:
        for i in self.get_claims.topics(item):
            if i.target and i.target.id == search_id:
                return True

    def is_another_id_in_item_topics(self, item: ItemPage, search_id: str) -> bool:
        if self.get_claims.topics(item) and not self.is_id_in_item_topics(item, search_id):
            return True

    def is_param_value_equal_item(self, p, m_wp_pagename: str, itemWD: ItemPage,
                                  m_wp_page_item: ItemPage) -> bool:
        if self.is_id_in_item_describes(p, itemWD.id, m_wp_page_item) \
                and self.is_id_in_item_topics(itemWD, m_wp_page_item.id):
            pwb.stdout(
                f'значение параметра ("{m_wp_pagename}") совпадает с item (label {m_wp_page_item.labels.get("ru")})')
            return True

    def is_item_of_disambig(self, item: ItemPage) -> bool:
        for e in self.get_claims.item_type(item):
            if e.target and e.target.id == props.disambig:
                return True

    # def _join_items_article_and_subject(self, pname: str, subject_item_id: str, target_item: ItemPage):
    #     # создать ссылку на элемент темы
    #     wditem_subject = self.add_main_subject(target_id=subject_item_id)
    #
    #     # создать "описывается в источниках" в элементе темы
    #     if wditem_subject:
    #         self.add_article_in_subjectitem(wditem_subject, pname, target_item)

    def add_link_to_main_subject(self, p, m_wp_page_item: ItemPage, make_wd_links: bool, skip_existing_topics: bool):
        """Добавить свойство "основная тема"""
        if make_wd_links:
            if skip_existing_topics:
                if self.is_another_id_in_item_topics(p.itemWD, m_wp_page_item.id):
                    pwb.stdout(
                        'Item уже имеет темы, отличные от ручной ссылки. Возможно в ручной ссылке - дизамбиг')
                    return

            if not self.is_id_in_item_topics(p.itemWD, m_wp_page_item.id):
                self.add_main_subject(p.itemWD, target=m_wp_page_item)
            if not self.is_id_in_item_describes(p, p.itemWD.id, m_wp_page_item):
                self.add_article_in_subjectitem(p, m_wp_page_item, p.itemWD)

    def add_main_subject(self, itemWD: ItemPage, target_id: str = None, target: ItemPage = None):
        """ создать ссылку на элемент темы """
        claim_topic_subject = self.claim_instance.claim_main_subject()
        # pwb.Claim(self.WD, props.topic_subject)
        if target_id:
            wditem_subject = pwb.ItemPage(self.WD, target_id)
        elif target:
            wditem_subject = target
        else:
            return
        # target = wd_item_ids[0]
        claim_topic_subject.setTarget(wditem_subject)
        if self.test_run:
            return
        itemWD.addClaim(claim_topic_subject, bot=self.as_bot, summary='moved from ruwikisource')
        pwb.stdout(f'added main subject in item')

    def add_article_in_subjectitem(self, p, subject_item: ItemPage, target_item: ItemPage):
        """ создать "описывается в источниках" в элементе темы """
        # s = get_item_from_listdict(other_sources, 'argument', m_item_id)
        # [i.target for i in self.wd_item.claims.get(self.main_subject, [])]
        claim_described_by = self.claim_instance.claim_described_by_source()
        rootpagename = p.rootpagename
        if p.rootpagename == 'Лентапедия' and p.title.endswith('/Полная версия'):
            rootpagename = 'Лентапедия2'
        target = p.enc_meta['wditem']
        claim_described_by.setTarget(target)
        qualifier = self.claim_instance.claim_dedicated_article()
        # qualifier_target = pwb.ItemPage(self.WD, m_item_id)
        qualifier.setTarget(target_item)
        claim_described_by.addQualifier(qualifier)
        if self.test_run:
            return
        subject_item.addClaim(claim_described_by, bot=self.as_bot, summary='moved from ruwikisource')
        pwb.stdout(f'added item of article in subject item')

    # def get_item(self, site, item_id: str = None, title: str = None, page=None):
    #     item = None
    #     try:
    #         if item_id:
    #             item = pwb.ItemPage(site, item_id)
    #         else:
    #             if title:
    #                 page = self.get_page(site, title=title)
    #             elif page:
    #                 page = self.get_page(site, page=page)
    #             if page and page.exists():
    #                 item = page.data_item()
    #         if item:
    #             item.get()
    #     except pwb.exceptions.NoPageError:
    #         item = None
    #     return item

    def get_item_by_title(self, site: pwb.Site, title: str) -> Optional[pwb.ItemPage]:
        page = pwb.Page(site, title)
        item = self.get_item_by_page(page)
        return item

    def get_item_by_id(self, item_id: str) -> Optional[pwb.ItemPage]:
        if pwb.ItemPage.is_valid_id(item_id):
            item = pwb.ItemPage(self.WD, item_id)
            return self.load_item(item)

    def get_item_by_page(self, page: pwb.Page) -> Optional[pwb.ItemPage]:
        if not isinstance(page, pwb.Page): return
        try:
            item = page.data_item()
        except pwb.exceptions.NoPageError:
            pass
        else:
            return self.load_item(item)

    def load_item(self, item: Optional[pwb.ItemPage]) -> Optional[pwb.ItemPage]:
        if isinstance(item, pwb.ItemPage) and item.exists():
            while item.isRedirectPage():
                item = item.getRedirectTarget()
            return item

    def _get_item(self, site: pwb.Site, pg: Union[str, pwb.Page]) -> Optional[pwb.ItemPage]:
        """
        :param site: pwb.Site
        :param pg: (str): название страницы, или id элемента ('Qxxx'), или pwb.Page
        :return: элемент или None
        """
        item = None
        if isinstance(pg, str):
            if pwb.ItemPage.is_valid_id(pg):
                item_id = pg
                item = pwb.ItemPage(site, item_id)
            else:
                title = pg
                pg = pwb.Page(site, title)
        if isinstance(pg, pwb.Page):
            try:
                # item = pwb.ItemPage.fromPage(pg, lazy_load=True)
                item = pg.data_item()
            except pwb.exceptions.NoPageError:
                pass
        if item and item.exists():
            item.get()
            return item

    def get_WPsite(self, pagename_raw: str) -> Tuple[Optional[pwb.Site], Optional[str]]:
        # .target.title(with_ns=False)
        pagename = None
        site = self.WP
        for _l in ('be-tarask', 'be-x-old'):
            if _l in pagename_raw:
                site = pwb.Site(_l, 'wikipedia')
                pagename = pagename_raw.rpartition(_l + ':')[-1]
                break
        lnk_tmp = pwb.Link(pagename or pagename_raw, source=site)
        lang_tmp = lnk_tmp.parse_site()[1]
        try:
            title_tmp = lnk_tmp.title
        # except (pwb.exceptions.SiteDefinitionError, pwb.exceptions.InvalidTitle):
        except:
            '''Вероятно нестандартный языковый код страницы'''
            return None, None
        WP = self.sites.get(lang_tmp + 'wikipedia')
        if not WP:
            WP = self.sites[lang_tmp + 'wikipedia'] = pwb.Site(lang_tmp, 'wikipedia')
        return WP, title_tmp

    # def create_item_article(self):
