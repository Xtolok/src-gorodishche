from django.db import models
from django.urls import reverse


class SiteSettings(models.Model):
    site_name = models.CharField('Название в шапке', max_length=200, default='Городищенский СРЦ')
    footer_text = models.CharField(
        'Текст в подвале',
        max_length=500,
        default='© 2026 ГКСУ СО «Городищенский социально-реабилитационный центр для несовершеннолетних»',
    )
    gosuslugi_url = models.URLField('Ссылка на Госуслуги', default='https://www.gosuslugi.ru/')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactInfo(models.Model):
    address = models.CharField('Адрес', max_length=300)
    phone_primary = models.CharField('Телефон 1 (отображение)', max_length=50)
    phone_primary_tel = models.CharField('Телефон 1 (для ссылки tel:)', max_length=30, blank=True)
    phone_secondary = models.CharField('Телефон 2 (отображение)', max_length=50, blank=True)
    phone_secondary_tel = models.CharField('Телефон 2 (для ссылки tel:)', max_length=30, blank=True)
    email = models.EmailField('Email')
    work_weekdays = models.CharField('Режим Пн–Пт', max_length=100, default='8:30 — 17:30')
    work_break = models.CharField('Перерыв', max_length=100, default='12:00 — 13:00')
    work_weekend = models.CharField('Сб — Вс', max_length=100, default='Выходной')
    map_placeholder = models.CharField(
        'Текст-заглушка (если карта выключена)',
        max_length=300,
        blank=True,
    )
    show_map = models.BooleanField('Показывать карту', default=True)
    map_latitude = models.DecimalField(
        'Широта',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Например: 48.706200',
    )
    map_longitude = models.DecimalField(
        'Долгота',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Например: 44.481500',
    )
    map_zoom = models.PositiveSmallIntegerField('Масштаб карты', default=16)
    map_iframe = models.TextField(
        'Код карты (iframe)',
        blank=True,
        help_text='Вставьте HTML с Яндекс.Карт (Поделиться → Вставить карту). Если заполнено — координаты не используются.',
    )
    reception_director = models.TextField('Личный приём директора', blank=True)
    reception_written = models.TextField('Письменные обращения', blank=True)
    reception_online = models.TextField('Онлайн-обращения', blank=True)

    class Meta:
        verbose_name = 'Контактная информация'
        verbose_name_plural = 'Контактная информация'

    def __str__(self):
        return self.address

    @property
    def has_map(self):
        if not self.show_map:
            return False
        if self.map_iframe:
            return True
        return self.map_latitude is not None and self.map_longitude is not None

    @property
    def yandex_map_widget_url(self):
        lon = self.map_longitude
        lat = self.map_latitude
        zoom = self.map_zoom
        return (
            f'https://yandex.ru/map-widget/v1/?ll={lon}%2C{lat}&z={zoom}'
            f'&pt={lon},{lat},pm2rdm'
        )

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'address': '403003, Волгоградская область, р.п. Городище, ул. Ворошилова, д. 35',
                'phone_primary': '8-84468-3-15-59',
                'phone_primary_tel': '+78446831559',
                'phone_secondary': '8-84468-5-21-54',
                'phone_secondary_tel': '+78446852154',
                'email': 'Gorodischenskiy_SRC@volganet.ru',
                'map_placeholder': 'Карта — р.п. Городище, ул. Ворошилова, д. 35',
                'show_map': True,
                'map_latitude': '48.706200',
                'map_longitude': '44.481500',
                'map_zoom': 16,
            },
        )
        return obj


class Page(models.Model):
    SLUG_INDEX = 'index'
    SLUG_SOCIAL = 'socialnye-uslugi'
    SLUG_PERECHEN = 'perechen-uslug'
    SLUG_DNEVNOE = 'dnevnoe-otdelenie'
    SLUG_APPEAL = 'rabota-s-obrascheniyami'
    SLUG_ABOUT = 'ob-uchrezhdenii'
    SLUG_ABOUT_CONTACTS = 'ob-uchrezhdenii-kontakty'
    SLUG_ABOUT_POLNOMOCHIYA = 'ob-uchrezhdenii-polnomochiya'
    SLUG_ABOUT_RUKOVODSTVO = 'ob-uchrezhdenii-rukovodstvo'
    SLUG_ABOUT_LOKALNYE = 'ob-uchrezhdenii-lokalnye-akty'
    SLUG_ABOUT_PRAVILA = 'ob-uchrezhdenii-pravila'
    SLUG_ABOUT_POPECH = 'ob-uchrezhdenii-popechitelskiy-sovet'
    SLUG_NEWS = 'novosti'
    SLUG_LEGAL = 'pravovye-akty'
    SLUG_LEGAL_ACTS = 'pravovye-akty-akty'
    SLUG_LEGAL_USTAV = 'pravovye-akty-ustav'
    SLUG_LEGAL_LITSENZII = 'pravovye-akty-litsenzii'
    SLUG_LEGAL_FEDERAL = 'pravovye-akty-federal'
    SLUG_LEGAL_REGIONAL = 'pravovye-akty-regional'
    SLUG_LEGAL_NORMATIVY = 'pravovye-akty-normativy'
    SLUG_LEGAL_SOUT = 'pravovye-akty-sout'
    SLUG_CURRENT = 'tekushchaya-deyatelnost'
    SLUG_NOK = 'nezavisimaya-otsenka-nok'

    SLUG_CHOICES = [
        (SLUG_INDEX, 'Главная'),
        (SLUG_SOCIAL, 'Социальные услуги'),
        (SLUG_PERECHEN, 'Перечень услуг'),
        (SLUG_DNEVNOE, 'Дневное отделение'),
        (SLUG_APPEAL, 'Работа с обращениями'),
        (SLUG_ABOUT, 'Об учреждении'),
        (SLUG_ABOUT_CONTACTS, 'Об учреждении — контакты'),
        (SLUG_ABOUT_POLNOMOCHIYA, 'Об учреждении — полномочия'),
        (SLUG_ABOUT_RUKOVODSTVO, 'Об учреждении — руководство'),
        (SLUG_ABOUT_LOKALNYE, 'Об учреждении — локальные акты'),
        (SLUG_ABOUT_PRAVILA, 'Об учреждении — правила распорядка'),
        (SLUG_ABOUT_POPECH, 'Об учреждении — попечительский совет'),
        (SLUG_NEWS, 'Новости'),
        (SLUG_LEGAL, 'Правовые акты'),
        (SLUG_LEGAL_ACTS, 'Правовые акты — НПА'),
        (SLUG_LEGAL_USTAV, 'Правовые акты — устав'),
        (SLUG_LEGAL_LITSENZII, 'Правовые акты — лицензии'),
        (SLUG_LEGAL_FEDERAL, 'Правовые акты — федеральное'),
        (SLUG_LEGAL_REGIONAL, 'Правовые акты — региональное'),
        (SLUG_LEGAL_NORMATIVY, 'Правовые акты — нормативы'),
        (SLUG_LEGAL_SOUT, 'Правовые акты — СОУТ'),
        (SLUG_CURRENT, 'Текущая деятельность'),
        (SLUG_NOK, 'Независимая оценка качества НОК'),
    ]

    slug = models.SlugField('Код страницы', max_length=50, choices=SLUG_CHOICES, unique=True)
    meta_title = models.CharField('Заголовок вкладки браузера', max_length=200)
    badge = models.CharField('Бейдж', max_length=200, blank=True)
    h1 = models.CharField('Заголовок H1', max_length=300)
    intro = models.TextField('Вводный текст / описание', blank=True)
    hero_button_text = models.CharField('Текст кнопки в шапке-блоке', max_length=100, blank=True)
    hero_button_url = models.CharField('Ссылка кнопки (имя url или http)', max_length=200, blank=True)
    free_banner_text = models.CharField('Баннер «бесплатно»', max_length=300, blank=True)
    block_title = models.CharField('Заголовок доп. блока', max_length=200, blank=True)
    block_content = models.TextField('Содержимое доп. блока', blank=True)
    dark_card_title = models.CharField('Тёмная карточка — заголовок', max_length=200, blank=True)
    dark_card_text = models.TextField('Тёмная карточка — текст', blank=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['slug']

    def __str__(self):
        return self.get_slug_display()

    def get_hero_button_href(self):
        if not self.hero_button_url:
            return ''
        if self.hero_button_url.startswith('http'):
            return self.hero_button_url
        return reverse(self.hero_button_url)


class HomeStat(models.Model):
    value = models.CharField('Значение', max_length=50)
    label = models.CharField('Подпись', max_length=200)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Показатель на главной'
        verbose_name_plural = 'Показатели на главной'
        ordering = ['order']

    def __str__(self):
        return f'{self.value} — {self.label}'


class InfoCard(models.Model):
    URL_CHOICES = [
        ('', '— без ссылки —'),
        ('index', 'Главная'),
        ('socialnye_uslugi', 'Социальные услуги'),
        ('perechen_uslug', 'Перечень услуг'),
        ('dnevnoe_otdelenie', 'Дневное отделение'),
        ('rabota_s_obrascheniyami', 'Работа с обращениями'),
        ('ob_uchrezhdenii', 'Об учреждении'),
        ('ob_uchrezhdenii_kontakty', 'Об учреждении — контакты'),
        ('ob_uchrezhdenii_polnomochiya', 'Об учреждении — полномочия'),
        ('ob_uchrezhdenii_rukovodstvo', 'Об учреждении — руководство'),
        ('ob_uchrezhdenii_lokalnye_akty', 'Об учреждении — локальные акты'),
        ('ob_uchrezhdenii_pravila', 'Об учреждении — правила распорядка'),
        ('ob_uchrezhdenii_popechitelskiy_sovet', 'Об учреждении — попечительский совет'),
        ('novosti', 'Новости'),
        ('pravovye_akty', 'Правовые акты'),
        ('tekushchaya_deyatelnost', 'Текущая деятельность'),
        ('nezavisimaya_otsenka_nok', 'Независимая оценка качества НОК'),
    ]

    PLACEMENT_CHOICES = [
        ('index_main', 'Главная — 3 карточки'),
        ('index_bottom', 'Главная — 2 карточки'),
        ('social_top', 'Соц. услуги — 3 карточки'),
        ('dnevnoe_top', 'Дневное — 3 карточки'),
        ('appeal_cards', 'Обращения — 2 карточки'),
    ]

    placement = models.CharField('Размещение', max_length=30, choices=PLACEMENT_CHOICES)
    icon = models.CharField('Иконка (эмодзи)', max_length=10, blank=True)
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    link_url_name = models.CharField('Ссылка', max_length=50, choices=URL_CHOICES, blank=True)
    link_text = models.CharField('Текст ссылки', max_length=100, blank=True)
    button_text = models.CharField('Текст кнопки', max_length=100, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Информационная карточка'
        verbose_name_plural = 'Информационные карточки'
        ordering = ['placement', 'order']

    def __str__(self):
        return self.title


class ContentSection(models.Model):
    page_slug = models.CharField('Страница', max_length=50, choices=Page.SLUG_CHOICES)
    title = models.CharField('Заголовок', max_length=300)
    content = models.TextField('Текст (абзацы через пустую строку)', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Текстовый блок'
        verbose_name_plural = 'Текстовые блоки'
        ordering = ['page_slug', 'order']

    def __str__(self):
        return f'{self.page_slug}: {self.title}'

    def paragraphs(self):
        if not self.content:
            return []
        return [p.strip() for p in self.content.split('\n\n') if p.strip()]


class ListItem(models.Model):
    section = models.ForeignKey(
        ContentSection,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Блок',
    )
    text = models.CharField('Пункт', max_length=500)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Пункт списка'
        verbose_name_plural = 'Пункты списка'
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class News(models.Model):
    title = models.CharField('Заголовок', max_length=300)
    slug = models.SlugField('Адрес страницы', max_length=300, unique=True, blank=True, allow_unicode=True)
    body = models.TextField('Полный текст', blank=True)
    published_at = models.DateField('Дата публикации')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at', 'order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base = slugify(self.title, allow_unicode=True) or 'news'
            slug = base
            n = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('novosti_detail', kwargs={'slug': self.slug})


class LegalSection(models.Model):
    slug = models.SlugField('Код раздела', max_length=80, unique=True, blank=True)
    title = models.CharField('Заголовок раздела', max_length=300)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Раздел правовых актов'
        verbose_name_plural = 'Разделы правовых актов'
        ordering = ['order']

    def __str__(self):
        return self.title


class LegalItem(models.Model):
    section = models.ForeignKey(
        LegalSection,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Раздел',
    )
    text = models.CharField('Акт', max_length=500)
    file = models.FileField('Файл', upload_to='legal/', blank=True, null=True)
    external_url = models.URLField('Внешняя ссылка', max_length=1000, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    @property
    def href(self):
        if self.file:
            return self.file.url
        return self.external_url

    class Meta:
        verbose_name = 'Правовой акт'
        verbose_name_plural = 'Правовые акты'
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class ServiceCategory(models.Model):
    title = models.CharField('Категория услуг', max_length=300)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Категории услуг'
        ordering = ['order']

    def __str__(self):
        return self.title


class ServiceItem(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Категория',
    )
    text = models.CharField('Услуга', max_length=500)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class InstitutionProfile(models.Model):
    full_name = models.CharField('Полное наименование', max_length=500)
    short_name = models.CharField('Сокращённое наименование', max_length=200)
    inn = models.CharField('ИНН', max_length=20)
    kpp = models.CharField('КПП', max_length=20)
    okpo = models.CharField('ОКПО', max_length=20)
    ogrn = models.CharField('ОГРН', max_length=20)
    registration_info = models.TextField('Дата регистрации', blank=True)
    founder_info = models.TextField('Учредитель', blank=True)
    director_name = models.CharField('Директор', max_length=200, blank=True)
    property_type = models.CharField('Вид собственности', max_length=300, blank=True)
    branch_address = models.CharField('Адрес структурного подразделения', max_length=300, blank=True)
    branch_phone = models.CharField('Телефон подразделения', max_length=50, blank=True)
    main_building_photo = models.ImageField('Фото здания (Городище)', upload_to='about/', blank=True, null=True)
    branch_building_photo = models.ImageField('Фото здания (Иловля)', upload_to='about/', blank=True, null=True)

    class Meta:
        verbose_name = 'Сведения об учреждении'
        verbose_name_plural = 'Сведения об учреждении'

    def __str__(self):
        return self.short_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'full_name': (
                    'Государственное казенное специализированное учреждение социального обслуживания '
                    '"Городищенский социально-реабилитационный центр для несовершеннолетних"'
                ),
                'short_name': 'ГКСУ СО "Городищенский СРЦ"',
                'inn': '3403016961',
                'kpp': '340301001',
                'okpo': '53589642',
                'ogrn': '1023405361264',
            },
        )
        return obj


class StaffMember(models.Model):
    name = models.CharField('ФИО', max_length=200, blank=True)
    position = models.CharField('Должность', max_length=300)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    photo = models.ImageField('Фото', upload_to='staff/', blank=True, null=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Сотрудник руководства'
        verbose_name_plural = 'Руководство'
        ordering = ['order']

    def __str__(self):
        return self.name or self.position


class AboutDocument(models.Model):
    SECTION_CONTACTS = 'contacts'
    SECTION_RULES = 'rules'
    SECTION_PRAVILA = 'pravila'
    SECTION_POPECH = 'popech'

    SECTION_CHOICES = [
        (SECTION_CONTACTS, 'Контакты — документы'),
        (SECTION_RULES, 'Внутренние локальные акты'),
        (SECTION_PRAVILA, 'Правила внутреннего распорядка'),
        (SECTION_POPECH, 'Попечительский совет'),
    ]

    section = models.CharField('Раздел', max_length=20, choices=SECTION_CHOICES)
    title = models.CharField('Название', max_length=500)
    file = models.FileField('Файл', upload_to='about/docs/', blank=True, null=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Документ об учреждении'
        verbose_name_plural = 'Документы об учреждении'
        ordering = ['section', 'order']

    def __str__(self):
        return self.title[:80]


class NokContent(models.Model):
    body_html = models.TextField('Содержимое (HTML)', blank=True)

    class Meta:
        verbose_name = 'Независимая оценка качества НОК'
        verbose_name_plural = 'Независимая оценка качества НОК'

    def __str__(self):
        return 'Независимая оценка качества НОК'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CurrentActivitySection(models.Model):
    slug = models.SlugField('Код раздела', max_length=80, unique=True)
    title = models.CharField('Заголовок', max_length=300)
    body_html = models.TextField('Содержимое (HTML)', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Раздел текущей деятельности'
        verbose_name_plural = 'Разделы текущей деятельности'
        ordering = ['order']

    def __str__(self):
        return self.title


class RegionalSocialCenter(models.Model):
    number = models.PositiveSmallIntegerField('№')
    name = models.CharField('Наименование', max_length=300)
    url = models.URLField('Ссылка', max_length=500)

    class Meta:
        verbose_name = 'Центр соцзащиты области'
        verbose_name_plural = 'Центры соцзащиты области'
        ordering = ['number']

    def __str__(self):
        return f'{self.number}. {self.name}'
