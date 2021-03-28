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
import main_class


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


main_class.Process.pagegenerator_and_run = pagegenerator_and_run

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
    gen = main_class.pagegenerator(args)
    # for p in gen:
    #     for p in gen:
    # ' -onlyif:P31=Q13433827'
    if gen:
        z = tuple(gen)
        text = '\n'.join(tuple(gen))
        Path('pages.txt').write_text(text)
