from pywikibot.page import ItemPage, Claim
import copy
from typing import NamedTuple


class PropertiesID(NamedTuple):
    item_type = 'P31'
    topic_subject = 'P921'  # основная тема
    described_by_source = 'P1343'  # описывается в источниках
    dedicated_article = 'P805'  # тема утверждения
    types_to_search = 'Q13433827', 'Q1580166'  # энц. и словар. статья
    enc_article_item = 'Q10389811'  # энц. запись (её подклассы: энц. и словар. статья)
    disambig = 'Q4167410'  # дизамбиг, страница значений в проекте Викимедиа


props = PropertiesID()


class Get_claims:
    def topics(self, item: ItemPage) -> list:
        return item.claims.get(props.topic_subject, [])

    def described_by_source(self, item: ItemPage) -> list:
        return item.claims.get(props.described_by_source, [])

    def item_type(self, item: ItemPage) -> list:
        return item.claims.get(props.item_type, [])

    def get_qualifiers_dedicated_article(self, c: Claim) -> list:
        return c.qualifiers.get(props.dedicated_article, [])


class Claim_instance(Get_claims):
    def __init__(self, WD):
        self._claim_main_subject = Claim(WD, props.topic_subject)
        self._claim_described_by_source = Claim(WD, props.described_by_source)
        self._claim_dedicated_article = Claim(WD, props.dedicated_article)

    def claim_main_subject(self):
        # return Claim(self.WD, self.topic_subject)
        return copy.deepcopy(self._claim_main_subject)

    def claim_described_by_source(self):
        # return Claim(WD, self.described_by_source)
        return copy.deepcopy(self._claim_described_by_source)

    def claim_dedicated_article(self):
        # return Claim(WD, self.dedicated_article)
        return copy.deepcopy(self._claim_dedicated_article)
