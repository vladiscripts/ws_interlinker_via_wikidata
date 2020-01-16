from __init__ import *
import wiki_util
from wd_utils import props  # , WD_utils


class PageMeta:
    tpl: Optional[mwp.wikicode.Template]
    tpl_name: Optional[str]
    params: List[Tuple[str, str]]
    enc_with_trancludes: bool

    def __init__(self, processor, page: pwb.page.Page, enc_metas: dict):
        self.is_author_tpl = False
        self.page = wiki_util.get_wikipage(page.site, page=page)
        self.itemWD = processor.wd.get_item(processor.wd.WS, page=page)
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

    def tpl_data(self, tpl: mwp.wikicode.Template):
        self.tpl = tpl
        self.tpl_name = tpl.name.strip()
        # self.is_author_tpl = self.tplname.lower() in allowed_header_names

    def set_skip(self, cause: str):
        self.do_skip = True
        self.cause = cause

    def __repr__(self):
        return self.page.title()
