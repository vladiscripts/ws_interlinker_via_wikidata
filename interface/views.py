from django.shortcuts import render
from django.http import Http404
from interface.forms import InputForm, PagelinkForm
# import wikidata.wikidata as wd
# from wikidata.wikidata import

# from sudkz import SeleniumSudKZ
# from reqform.models import Region, Court


def get_court_id(formdata):
    """Перебирает результаты значений полей судов из формы, имеющих в ключах номера 2-18.
    Возврат: значение"""
    ckeys = [f'courts{rid}' for rid in range(2, 19)]  # генерация ключей
    for v in [formdata.pop(ck) for ck in ckeys]:
        if v != '':
            # formdata['court_only'] = v
            return v
    return 0

    # for ck in ckeys:
    #     v = formdata.get(ck, '')
    #     if v != '':
    #         return v
    # for fk in d.keys():
    #     for ck in ckeys:
    #         if fk == ck and d[fk] != '':
    #             return d[fk]


def to_int(d, keys):
    for k in keys:
        v = d[k]
        # if v is None:
        #     print(k, v)
        d[k] = int(v) if v != '' else 0


# Create your views here.
def show_page(request):
    # script = SeleniumSudKZ(syear)
    # list_courts = script.get_list_all_courts_fromfile()
    # list_courts = [(i[1], i[0]) for i in list_courts[1][2]]

    # for region, rid, courts in list_courts:
    #     record = Region(rid=rid, name=region)
    #     record.save()
    #     for court, cid in courts:
    #         record = Court(cid=cid, name=court, rid=rid)
    #         record.save()
    # Region.objects.all()[4]

    if request.method == 'POST':
        form = PagelinkForm(request.POST)
        if form.is_valid():

            d = form.cleaned_data
            d['court_only'] = get_court_id(d)
            to_int(d, ['region_only', 'court_only', 'year', 'year2_range', 'delay_for_lag_of_start_form', 'cdelay'])
            # d['region_only'] = 0 if d['region_all'] else d['region_only']

            # print(form.cleaned_data)

            # script = SeleniumSudKZ(d)
            # script.run()

            form.page_name.initial = page_name
            form.page_item.initial = page_item
            form.topic_name.initial = topic_name
            form.topic_item.initial = topic_item


        else:
            raise Http404
    else:
        form = PagelinkForm()

    return render(request, 'interface/ask.html', locals())


def wikisearch():
    import scripts.listpages

    prefixes = ['БСЭ1', 'БЭАН', 'БЭЮ', 'ВЭ', 'ГСС', 'ЕЭБЕ', 'МСР', 'МЭСБЕ', 'НЭС', 'ПБЭ', 'РБС', 'РСКД', 'РЭСБ', 'САР', 'ТСД1',
         'ТСД2', 'ТСД3', 'ТЭ1', 'ЭЛ', 'ЭСБЕ', 'ЭСГ']

    a = ['-family:wikisource', '-format:3', '-prefixindex:ЭСБЕ']
    scripts.listpages.main(*a)


def wikisearch_params(intitle, prefix):
    s = []
    if intitle:
        s.append(f'intitle:"{intitle}"')
    if prefix:
        s.append(f'prefix:"{prefix}"')
    string = ' '.join(s)
    return string


def requests_indexphp():
    import requests
    url_base = 'https://ru.wikisource.org/w/index.php'
    params = dict(search=wikisearch_params("Т", 'РСКд'),
                  # title='%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9F%D0%BE%D0%B8%D1%81%D0%BA',
                  # profile='default',fulltext=1,searchToken='5d6mu1ee4g174z531p3rnuitd'
                  )
    r = requests.get(url_base, params=params)
