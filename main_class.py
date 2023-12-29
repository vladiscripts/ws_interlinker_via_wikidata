#!/usr/bin/env python
from __init__ import *
import wiki_util
from wd_utils import WD_utils
from get_other_sources_from_lua import get_other_sources
from parameter import ManualParam
from page import PageMeta
from datetime import datetime
from pywikibot.data import mysql
from pathlib import Path


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
                # if param.cause:
                #     pwb.stdout(param.cause)
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
        base_args = ['-family:wikisource', '-lang:ru', '-ns:0', '-format:"{page.can_title}"']
        args = base_args + sys.argv[1:]

        # if self.__class__.__name__ == 'Articles':
        #     import run_articles
        #     d = run_articles.Articles(test_run=False)

        # gen = wiki_util.pagegenerator(args)
        gen = make_list()

        # gen = wiki_util.get_pages(base_args, ['-catr:Авторы:Ручная_ссылка'], intersect=False)
        for page in gen:
            self.process_page(page)


def pagegenerator(args: list = None):
    """ Get list of pages which using 'Template:infobox former country'
        без кавычек имена станиц/категорий в параметрах
    """
    from pywikibot import pagegenerators

    # args = ['-family:wikipedia', '-lang:en', '-ns:0'] + [f'-transcludes:{tpl}' for tpl in tpl_names]
    gen_factory = pwb.pagegenerators.GeneratorFactory()
    local_args = pwb.handle_args(args)
    for arg in local_args:
        gen_factory.handleArg(arg)
    gen = gen_factory.getCombinedGenerator(preload=False)
    return gen


def make_sql(lastedit_days: int):
    import json
    WS = pwb.Site(fam='wikisource', code='ru')
    encs = pwb.Page(WS, 'MediaWiki:Encyclopedias settings.json')
    enc_settings = json.loads(encs.text)
    j = pwb.Page(WS, 'MediaWiki:Настройки бота для создания элементов ВД.json')
    settings = json.loads(j.text)
    # prefixes = {prefix: d for prefix, d in settings['prefixes'].items()}
    # categories = ','.join(['"%s"' % d['category_of_articles'].replace(' ', '_') for prefix, d in prefixes.items()])
    # categories += ['ЭСБЕ:ДО', 'ЭСБЕ', 'МЭСБЕ', 'ВЭ:ДО', 'ВЭ:ВТ', 'ЭЛ:ВТ', 'ЭЛ:ДО']

    prefixes = [d['title'] for d in enc_settings if d['project'] == 'ruwikisource']
    prefixes_sql = ' OR '.join([f'page_title LIKE "{prx}/%"' for prx in prefixes])

    x = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    # categories = ','.join(['"%s"' % d['category_of_articles'].replace(' ', '_') for prefix, d in prefixes.items()])
    categories = ','.join(
        [f'"%s"' % c.replace(' ', '_') for c in ["Ручная ссылка:Викиданные", "Ручная ссылка:Википедия"]])
    #  'БЭЮ', 'БСЭ1' мелкие словарные статьи или масса перенаправлений
    # sql = f"""
    # SELECT page_namespace,  page_title
    # FROM ruwikisource_p.page
    #     JOIN ruwikisource_p.categorylinks
    #         ON cl_from = page_id
    #         AND page_namespace = 0
    #         AND cl_to IN ({categories})
    #         AND page_is_redirect = 0
    #     LEFT JOIN ruwikisource_p.categorylinks cw
    #         ON cw.cl_from = page_id
    #         AND cw.cl_to = "Викиданные:Страницы_с_элементами"
    #     LEFT JOIN ruwikisource_p.categorylinks cr
    #         ON cr.cl_from = page_id
    #         AND cr.cl_to LIKE "%еренаправлени%"
    #     JOIN revision
    #         ON page_latest = rev_id
    #         AND rev_timestamp < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {lastedit_days} DAY)
    # WHERE cw.cl_to IS NULL AND cr.cl_to IS NULL;
    # """
    sql = f"""
    SELECT page_id,  page_title
    FROM ruwikisource_p.page
        JOIN ruwikisource_p.categorylinks 
            ON cl_from = page_id
            AND page_namespace = 0 
            AND cl_to IN ({categories})
            AND page_is_redirect = 0
        JOIN revision
            ON page_latest = rev_id
            AND rev_timestamp > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL {lastedit_days} DAY)
    WHERE {prefixes_sql}
;
    """
    return sql.replace('\n', ' ').strip()


def wdb_query(sql, limit=''):
    result = mysql.mysql_query(sql.format(limit), dbname='ruwikisource')
    return result


def make_list():
    base_args = ['-family:wikisource', '-lang:ru', '-ns:0', '-format:"{page.can_title}"']

    args = base_args + sys.argv[1:]  # + ['-mysqlquery:%s' % make_sql(lastedit_days=700)]

    # if self.__class__.__name__ == 'Articles':
    #     import run_articles
    #     d = run_articles.Articles(test_run=False)
    base_list = wdb_query(make_sql(lastedit_days=7000))
    s = '\n'.join((t.decode() for pid, t in base_list if not t.decode().startswith('ТСД')))
    Path('base_list.txt').write_text(s)
    # with io.StringIO(s) as fp: a=fp.read()
    import itertools

    def chain():
        for P31 in ['-onlyif:P31=Q13433827', '-onlyif:P31=Q1580166', '-onlyif:P31=Q10389811']:
            args = base_args + ['-file:base_list.txt'] + [P31, '-intersect']
            gen = pagegenerator(args)
            yield from gen

    # gen__=()
    # for P31 in ['-onlyif:P31=Q13433827','-onlyif:P31=Q1580166','-onlyif:P31=Q10389811']:
    #     args = base_args + ['-file:base_list.txt'] + [P31, '-intersect']
    #     gen = pagegenerator(args)
    #
    #     gen = (p for p in gen)
    #
    # args = base_args + ['-file:' + 'base_list.txt'] + ['-onlyif:P31=Q13433827', '-intersect']
    # gen = pagegenerator(args)
    #
    # args = base_args + ['-file:' + 'base_list.txt'] + ['-onlyif:P31=Q1580166', '-intersect']
    # gen = pagegenerator(args)
    #
    # args = base_args + ['-file:' + 'base_list.txt'] + ['-onlyif:P31=Q10389811', '-intersect']
    # gen = pagegenerator(args)
    # itertools.chain()

    gen = chain()

    # args = base_args + ['-page:БЭАН/Утренняя звезда']
    # gen = pagegenerator(args)

    # for p in gen:
    #     for p in gen:
    # ' -onlyif:P31=Q13433827'

    # if gen:
    #     z = tuple(gen)
    #     text = '\n'.join(tuple(gen))
    #     Path('pages.txt').write_text(text)

    return gen


if __name__ == '__main__':
    from pathlib import Path

    base_args = ['-family:wikisource', '-lang:ru', '-ns:0', '-format:"{page.can_title}"']

    args = base_args + sys.argv[1:]  # + ['-mysqlquery:%s' % make_sql(lastedit_days=700)]

    # if self.__class__.__name__ == 'Articles':
    #     import run_articles
    #     d = run_articles.Articles(test_run=False)
    base_list = wdb_query(make_sql(700))
    s = '\n'.join((t.decode() for i, t in base_list))
    Path('base_list.txt').write_text(s)
    # with io.StringIO(s) as fp: a=fp.read()
    args = base_args + ['-file:' + 'base_list.txt'] + ['-onlyif:P31=Q13433827', '-intersect']
    gen = pagegenerator(args)
    # for p in gen:
    #     for p in gen:
    # ' -onlyif:P31=Q13433827'
    if gen:
        z = tuple(gen)
        text = '\n'.join(tuple(gen))
        Path('pages.txt').write_text(text)
