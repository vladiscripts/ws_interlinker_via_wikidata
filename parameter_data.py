from __init__ import *
from mwparserfromhell.nodes.extras import Parameter
from enum import IntEnum
import wiki_util
from page_data import PageMeta


class ParamType(IntEnum):
    unknown = 0
    allowed_wikiprojects = 1
    enc = 2


class ManualParam:
    pname: Optional[str]
    pval_raw: Optional[str]
    pval: Optional[str]
    pagename: str  # реальное название страницы, через редиректы
    WP: pwb.Site

    flow: int
    is_item_of_disambig: bool
    sitelink_ruwiki: str

    page: Optional[pwb.Page]
    item: Optional[pwb.ItemPage]

    func: Callable

    do_skip: bool
    cause: str

    # allowed_header_names.extend(self.enc_prefixes)

    re_remove_tagcomment = re.compile(r'<!--.*?-->', flags=re.DOTALL)

    def __init__(self, processor, param):
        self.processor = processor
        self.wd = processor.wd
        self.p = p

        self.name = str(parameter.name).strip()
        self.do_skip = False
        self.cause = ''
        self.flow = 0
        if self.name in self.processor.enc_prefixes:
            self.flow = ParamType.enc
        elif self.name in self.processor.allowed_wikiprojects_params:
            self.flow = ParamType.allowed_wikiprojects
        if self.flow not in [ParamType.enc, ParamType.allowed_wikiprojects]:
            self.do_skip = True
            return

        self.pval_raw = parameter.value.strip()
        self.pval = self.re_remove_tagcomment.sub('', self.pval_raw).strip()
        if self.pval == '':
            self.do_skip = True
            return

        self.enc_meta = self.processor.enc_metas.get(self.name)
        # if self.is_enc_pagename:
        if self.flow == ParamType.enc:
            self.get_enc_pagename()
        self.get_mw_page()
        # logger.debug(f'+get_mw_page()')
        self.get_mw_item()  # get pwb.Page, pwb.ItemPage
        # logger.debug(f'+get_mw_item()')
        if self.item:
            self.mapper_paramfunc()

    def get_mw_page(self):
        """ Get
        self.WP, self.pagename
        self.page: pwb.Page
        """
        self.page = None
        site = None
        if self.name == 'ВИКИПЕДИЯ':
            self.WP, self.pagename = self.wd.get_WPsite(self.pval)
            if not self.WP:
                self.set_skip(f'{self.pval} - вероятно нестандартный языковый код страницы')
                return
            site = self.WP

        elif self.flow == ParamType.enc:
            site = self.wd.WS

        if site:
            self.page = wiki_util.get_wikipage(site, title=self.pagename)
            if not self.page:
                # бывают ссылки на отсутств. в ВТ, напр. [[К:Ручная ссылка на несуществующую словарную статью:НЭС]]
                # wiki_util.remove_param(self.p, self.name, value_only=True)
                self.set_skip('no m_wp_page')
                return

    def get_mw_item(self):
        """ Get
        self.page: pwb.Page
        self.item: pwb.ItemPage
        """
        self.item = None
        if self.page:
            self.item = self.wd.get_item_by_page(self.page)
        if self.name == 'ВИКИДАННЫЕ':
            self.item = self.wd.get_item_by_id(self.pval)
        if not self.item:
            self.set_skip('no m_wp_page_item')
            return

        # не работать по ссылкам на дизамбиги
        self.is_item_of_disambig = self.wd.is_item_of_disambig(self.item)
        # try:
        #     self.is_item_of_disambig = self.wd.is_item_of_disambig(self.item)
        # except:
        #     pass

        if self.is_item_of_disambig and self.processor.skip_wd_links_to_disambigs:
            self.set_skip(f'{self.name}: ссылка на дизамбиг')

        self.sitelink_ruwiki = self.item.sitelinks.get(f'ruwiki')
        if not self.sitelink_ruwiki and self.processor.require_ruwiki_sitelink:
            self.set_skip('no ruwiki for m_wp_page')

    def get_enc_pagename(self):
        RUWIKISOURCE = 'ruwikisource'
        if self.enc_meta.get('project') == RUWIKISOURCE:
            enc_pattern = self.enc_meta.get('titleVT')  # 'Британника' и т.п.
            if enc_pattern:
                self.pagename = enc_pattern.replace('$1', self.pval)
        else:
            projectCode = self.enc_meta.get('projectCode')
            prefix = self.enc_meta.get('prefix')
            suffix = self.enc_meta.get('suffix')
            # if all((projectCode, prefix, self.pval, suffix)):
            #     self.pagename = f':{projectCode}{prefix}{self.pval}{suffix}'
            self.pagename = f':{projectCode}{prefix}{self.pval}{suffix}'

    def mapper_paramfunc(self):
        # параметры проектов (ВИКИПЕДИЯ, ВИКИТЕКА, ВИКИСКЛАД и т.д.)
        if self.flow == ParamType.allowed_wikiprojects:
            self.func = self.processor.mapper_paramfunc.get(self.name)

        # параметры словарей (ЭСБЕ и т.д.)
        elif self.flow == ParamType.enc:
            self.func = self.processor.param_encyclopedia

    def set_skip(self, cause: str):
        self.do_skip = True
        self.cause = cause

    def __repr__(self):
        return self.name, self.pval
