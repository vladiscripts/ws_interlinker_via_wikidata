from django import forms


# from sudkz import SeleniumSudKZ, FileOpps


class PagelinkForm(forms.Form):
    page_name = forms.CharField(label='Страница', max_length=150, required=False)
    page_item = forms.CharField(label='Элемент страницы', max_length=150, required=False)
    topic_name = forms.CharField(label='Тема', max_length=150, required=False)
    topic_item = forms.CharField(label='Элемент темы', max_length=150, required=False)


class InputForm(forms.Form):
    filename_list_courts = 'list_courts.json'
    blank_choice = [('', '--- Выберите значение ---')]
    # script = SeleniumSudKZ.json_data_from_file(self.settings.filename_list_courts)
    sel = forms.Select()

    # do = forms.CharField(widget=forms.Textarea(attrs=dict(cols="130", rows="15", placeholder='Введите текст')))
    SEARCH_STRING = forms.CharField(initial='', label='Поисковая строка', max_length=100)  # эмбамунайгаз
    INN_BIN = forms.CharField(label='ИИН / БИН', max_length=100, required=False)
    CASE_NUMBER = forms.CharField(label='Номер дела', max_length=100, required=False)
    #
    # # list_courts = script.get_list_all_courts_fromfile()
    # list_courts = FileOpps.json_data_from_file(filename_list_courts)
    # # region_only = forms.CharField(label='Область (столица, город республиканского значения)', max_length=100)
    # # region_only = forms.CharField(label='Область (столица, город республиканского значения)', max_length=100, required=False)
    # # region_all = forms.CharField(label='Область (столица, город республиканского значения)', max_length=100)
    #
    # # court_only = forms.CharField(label='Судебный орган', max_length=100)
    # # court_all = forms.CharField(label='Судебный орган', max_length=100)
    # # court = forms.CharField(label='Судебный орган', max_length=100)
    # # court = forms.ModelChoiceField(initial={'some_field': 'fs-2'})
    # # court = forms.ChoiceField(widget=sel, label='Суды', required=True, choices=list_courts)
    # # court = forms.ModelChoiceField(queryset = Classes.objects.all(),empty_label="Выберите класс",widget=forms.Select(attrs={'class':'dropdown'}),label="Класс")
    # # class Meta:
    # # model = Lessons
    # # fields = ('lessons_class',)
    #
    # cr = {}
    # for region, rid, courts in list_courts:
    #     cr[int(rid)] = blank_choice + [(int(i), n) for n, i in courts]
    # regions = [(int(rid), region) for region, rid, courts in list_courts]
    #
    # region_only = forms.ChoiceField(widget=sel, label='Поиск по региону', required=False,
    #                                 choices=[('', 'Регион')] + regions)
    # # region_all = forms.BooleanField(label='Поиск по всем регионам', required=False)
    #
    # courts2 = forms.ChoiceField(choices=cr[2], widget=sel, label='город Астана', required=False)
    # courts3 = forms.ChoiceField(choices=cr[3], widget=sel, label='город Алматы', required=False)
    # courts4 = forms.ChoiceField(choices=cr[4], widget=sel, label='Акмолинская область', required=False)
    # courts5 = forms.ChoiceField(choices=cr[5], widget=sel, label='Актюбинская область', required=False)
    # courts6 = forms.ChoiceField(choices=cr[6], widget=sel, label='Алматинская область', required=False)
    # courts7 = forms.ChoiceField(choices=cr[7], widget=sel, label='Атырауская область', required=False)
    # courts8 = forms.ChoiceField(choices=cr[8], widget=sel, label='Восточно-Казахстанская область', required=False)
    # courts9 = forms.ChoiceField(choices=cr[9], widget=sel, label='Жамбылская область', required=False)
    # courts10 = forms.ChoiceField(choices=cr[10], widget=sel, label='Западно-Казахстанская область', required=False)
    # courts11 = forms.ChoiceField(choices=cr[11], widget=sel, label='Карагандинская область', required=False)
    # courts12 = forms.ChoiceField(choices=cr[12], widget=sel, label='Костанайская область', required=False)
    # courts13 = forms.ChoiceField(choices=cr[13], widget=sel, label='Кызылординская область', required=False)
    # courts14 = forms.ChoiceField(choices=cr[14], widget=sel, label='Мангистауская область', required=False)
    # courts15 = forms.ChoiceField(choices=cr[15], widget=sel, label='Павлодарская область', required=False)
    # courts16 = forms.ChoiceField(choices=cr[16], widget=sel, label='Северо-Казахстанская область', required=False)
    # courts17 = forms.ChoiceField(choices=cr[17], widget=sel, label='Южно-Казахстанская область', required=False)
    # courts18 = forms.ChoiceField(choices=cr[18], widget=sel, label='Военный суд Республики Казахстан', required=False)
    #
    # # court_all = forms.BooleanField(label='Поиск по всем судам', required=False)
    #
    # search_year = 2009
    # search_year2_range = 2018
    # years_list = SeleniumSudKZ.get_list_years(search_year, search_year2_range)
    # # years_list = script.get_list_years(search_year, search_year2_range)
    # years = [(i, i) for i in years_list]
    # # year = forms.CharField(label='Год', max_length=4, widget=forms.NumberInput(attrs={'class': 'year'}))
    # year = forms.ChoiceField(widget=sel, label='Год', required=True, choices=[('', 'Год')] + years)
    # # year2_range = forms.CharField(label='Диапазон', max_length=4, widget=forms.NumberInput(attrs={'class': 'year'}), required=False)
    # year2_range = forms.ChoiceField(widget=sel, label='Год диапазона (опционально)', required=False,
    #                                 choices=[('', 'Год диапазона')] + years)
    # year_search_all = forms.BooleanField(label='Все годы', required=False)
    #
    # # Настройки
    # # results_filename_csv = forms.CharField(initial='results.csv', max_length=100)
    # results_filename_xlsx = forms.CharField(initial='results.xlsx', label='Export Excel file', required=False,
    #                                         max_length=100)
    # save_documents = forms.BooleanField(initial=False, required=False, label='Записывать файлы документов')
    #
    # directory_documents_save = forms.CharField(initial='documents', label='Папка для записи документов', max_length=100)
    #
    # webdriver_name = forms.ChoiceField(widget=sel, label='Webdriver', required=False,
    #                                    choices=[(i, i) for i in ('Firefox', 'Chrome')])
    #
    # # To hide the Chrome browser window on work
    # useHeadlessBrowser = forms.BooleanField(label='HeadlessBrowser (for Chrome)', required=False)
    #
    # # RUCAPTCHA_KEY = forms.CharField(initial=RUCAPTCHA_KEY, max_length=100, required=True)
    # captcha_image_path = forms.CharField(initial='captcha.png', max_length=100)
    # screenshot_path = forms.CharField(initial='screenshot.png', max_length=100)
    #
    # filename_list_courts = forms.CharField(initial=filename_list_courts, required=False, max_length=100)
    #
    # # Delay in seconds for wait end of lag after submit start form.
    # # After this time the site will drop connection and lie what no results.
    # delay_for_lag_of_start_form = forms.CharField(initial=40, max_length=3, widget=forms.NumberInput())
    #
    # # Delay in seconds for create list of all courts on start
    # cdelay = forms.CharField(initial=1, max_length=3, widget=forms.NumberInput(),
    #                          help_text='Delay in seconds for create list of all courts on start')
