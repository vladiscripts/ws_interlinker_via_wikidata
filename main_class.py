#!/usr/bin/env python
from __init__ import *
import wiki_util
from wd_utils import WD_utils
from get_other_sources_from_lua import get_other_sources
from parameter import ManualParam
from page import PageMeta


class Process:
    works_pages_with_wditems: bool = True  # работать со страницами только имеющими элемент ВД
    require_ruwiki_sitelink: bool = True  # пропускать страницы если у элемента темы нет страницы в ruwiki
    skip_wd_links_to_disambigs: bool = True  # не работать по словарным ссылкам на дизамбиги
    make_wd_links: bool = False  # линковать ссылки ВД, иначе только удалять параметры дублирующие ВД
    work_only_enc: bool  # работать только по элементам типов 'Q17329259', 'Q1580166' (энц. и словар. статьи)
    skip_links_with_anchors: bool = True  # не трогать ссылки содержащие '#', вроде 'РСКД/Статья#якорь'
    skip_by_text_lengh: bool = True
    prj = 'ruwikisource'
    allowed_header_names: tuple
    wd: WD_utils = None

    # wikiprojects = parse_lua_to_dict(WS, 'projects')
    # wikiprojects = ['ВИКИПЕДИЯ', ]
    enc_prefixes: Tuple[str, ...]
    mapper_paramfunc: OrderedDict
    allowed_wikiprojects_params: Tuple[str, ...]

    # encyclopedies = ['ЭСБЕ', 'РСКД', 'ВЭ']

    # header_names = ['ОТЕКСТЕ', 'БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС',
    #                 'РСКД', 'РЭСБ', 'САР', 'ТСД1', 'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    def __init__(self, test_run: bool = False):
        self.test_run = test_run
        self.wd = WD_utils(as_bot=True, test_run=test_run)
        self.enc_metas = get_other_sources()
        for t in ('ТСД', 'ТСД1', 'ТСД2', 'ТСД3'): self.enc_metas.pop(t)  # исключить ТСД

        self.enc_prefixes = tuple(self.enc_metas.keys())

        # маппер параметр-функция, по порядку обработки
        self.mapper_paramfunc = OrderedDict((
            ('ВИКИДАННЫЕ', self.param_Wikidata),
            ('ВИКИПЕДИЯ', self.param_Wikipedia),
            ('ИЗОБРАЖЕНИЕ', self.param_Image),
        ))
        self.allowed_wikiprojects_params = tuple(self.mapper_paramfunc.keys())

    def process_page(self, page: pwb.page.Page):
        p = PageMeta(self, page, self.enc_metas, self.allowed_header_names)
        pwb.stdout(p.title)
        if p.do_skip:
            pwb.stdout(p.cause)
            return

        for tpl in p.wikicode.filter_templates():
            tpl_name = tpl.name.strip()
            if tpl_name in self.allowed_header_names:
                p.add_tpl_data(tpl)
                # logger.debug(f'{p.tpl_name=}')
                # if p.is_author_tpl is None: return
                self.process_params(p)

                # очищаем параметры, постим страницу
                if p.params_to_delete or p.params_to_value_clear:
                    summary = wiki_util.make_summary(p)
                    wiki_util.page_posting(p.page, str(p.wikicode), summary, self.test_run)
                    break
        # logger.debug(f'-')

    def process_params(self, p: PageMeta):
        """Итерация по параметрам шаблона"""
        # if p.is_author_tpl:
        #     self.author()

        for parameter in p.tpl.params:
            # logger.debug(f'{str(parameter).strip()}')
            param = ManualParam(self, parameter, p)
            if p.do_skip:
                return
            if param.do_skip:
                if param.cause:
                    pwb.stdout(param.cause)
                continue

            # запуск функции обработки параметра, устанавливается в self.mapper_paramfunc
            param.func(p, param)
            # logger.debug('param.func done')

    @abstractmethod
    def param_encyclopedia(self, p, parameter):
        pass

    @abstractmethod
    def param_Wikipedia(self, p, parameter):
        pass

    @abstractmethod
    def param_Image(self, p, parameter):
        pass

    @abstractmethod
    def param_Wikidata(self, p, parameter):
        pass

    def do_skip(self, p):
        """Пропуск страницы по условию"""
        pwb.stdout(p.cause)

    def pagegenerator_and_run(self):
        base_args = ['-site:wikisource:ru', '-ns:0', '-format:"{page.can_title}"']
        args = base_args + sys.argv[1:]
        gen = wiki_util.pagegenerator(args)
        for page in gen:
            self.process_page(page)

    def disambigs(self, p, param):
        """ссылки на дизамбиги"""
        # is_item_of_disambig = self.wd.is_item_of_disambig(param.item)
        wiki_util.set_or_remove_category(p, cat_name=f'Ручная ссылка на неоднозначность:{param.name.capitalize()}',
                                         condition=param.is_item_of_disambig, add_cat=self.skip_wd_links_to_disambigs,
                                         # log_on_add=f'{param.name}: ссылка на дизамбиг'
                                         )
        # if param.is_item_of_disambig and self.skip_wd_links_to_disambigs:
        #     pwb.stdout(f'{param.name}: ссылка на дизамбиг')
        #     p.do_skip = True
        #     return True
