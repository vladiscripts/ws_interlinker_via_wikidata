from __init__ import *
import wiki_util
from wd_utils import props  # , WD_utils


class PageMeta:
    tpl: Optional[mwp.wikicode.Template]
    tpl_name: Optional[str]
    params: List[Tuple[str, str]]
    enc_with_transcludes: bool
    is_author_tpl: bool
    short_page: bool
    params_to_delete: list
    params_to_value_clear: list
    summaries: list
    page: pwb.Page
    item: pwb.ItemPage

    # не обрабатывать страницу, устанавливается фильтрами
    do_skip: bool
    cause: str

    """Перенос ссылок на энциклопедии/словари из статей в Викиданые и создание там записи."""
    re_cat_redirect = re.compile(r'\[\[Категория:[^]]+?Перенаправления', flags=re.IGNORECASE)

    def __init__(self, processor, page: pwb.page.Page, enc_metas: dict, allowed_header_names):
        self.processor = processor
        self.do_skip = False
        # self.is_author_tpl = False
        self.page = wiki_util.get_wikipage(page.site, page=page)
        self.title = page.title()
        self.rootpagename, _, self.subpagename = self.title.partition('/')
        self.enc_with_transcludes = bool(self.rootpagename in ('ПБЭ', 'ЭЛ'))
        self.enc_meta = enc_metas.get(self.rootpagename)
        self.allowed_header_names = allowed_header_names
        self.short_page = False
        self.params_to_delete = []
        self.params_to_value_clear = []
        # do_cause = None
        self.summaries = []
        # self.get_filled_params()
        self.params = []

        self.itemWD = processor.wd.get_item_by_page(self.page)
        if not self.itemWD and processor.works_pages_with_wditems:
            self.set_skip('no p.itemWD')
            return

        # работать по энциклопедическая статья и словарная статья
        if processor.work_only_enc and not [True for e in processor.wd.get_claims.item_type(self.itemWD)
                                            if e.target.id in props.types_to_search]:
            self.set_skip('не словарная статья')
            return

        self.text = self.page.get()
        self.wikicode = mwp.parse(self.text)
        self.tpl = None
        self.tpl_name = None
        # if self.re_cat_redirect.search(page.text):  # пропускать страницы-перенаправления
        if [s for s in self.wikicode.filter_wikilinks(matches=r'^\[\[Категория:[^|]*?:Перенаправления')]:
            self.set_skip('перенаправление')
            return

        # фильтр по размеру текста
        if processor.skip_by_text_lengh:
            self.filter_by_text_lenght()
            if self.short_page:
                self.set_skip('размер текста < 100')
                return

    def filter_by_text_lenght(self, text_limit: int = 100):
        """фильтр по размеру текста"""
        if not self.processor.skip_by_text_lengh:
            return
        if self.enc_with_transcludes:
            return
        for _tpl in self.wikicode.filter_templates():
            if _tpl.name.strip() in self.allowed_header_names:
                self.tpl_data(_tpl)
                break

        if self.tpl:
            # убираем шаблон
            t = self.text.replace(str(self.tpl), '')
            # убираем категории и викиссылки
            for s in self.wikicode.filter_wikilinks(matches=r'^\[\[Категория:'):
                t = t.replace(str(s), '')
            for s in self.wikicode.filter_wikilinks():
                t = t.replace(str(s), str(s.text))
            t = t.strip()
            # часть ЭСБЕ - трансклюзии
            if self.tpl_name == 'ЭСБЕ' and len(t) == 0:
                return

            if len(t) < text_limit:
                self.short_page = True
                return

    def tpl_data(self, tpl: mwp.wikicode.Template):
        self.tpl = tpl
        self.tpl_name = tpl.name.strip()
        # self.is_author_tpl = self.tplname.lower() in allowed_header_names

    def set_skip(self, cause: str):
        self.do_skip = True
        self.cause = cause

    def __repr__(self):
        return self.page.title()
