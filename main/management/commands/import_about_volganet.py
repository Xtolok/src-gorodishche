import re
import ssl
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from main.models import (
    AboutDocument,
    ContentSection,
    InstitutionProfile,
    ListItem,
    Page,
    RegionalSocialCenter,
    StaffMember,
)

BASE = 'https://442fz.volganet.ru'
ORG_BASE = f'{BASE}/025156/organizatsiya-otdykha-i-ozdorovleniya/organizatsiya-otdykha-i-ozdorovleniya-2026'
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def safe_url(url):
    parts = urlsplit(url)
    path = quote(parts.path, safe='/%:@')
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def fetch_bytes(url):
    req = Request(safe_url(url), headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, context=SSL_CTX, timeout=60) as resp:
        return resp.read()


def fetch_text(url):
    data = fetch_bytes(url)
    for enc in ('utf-8', 'cp1251', 'latin-1'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace')


def save_file_field(field, url, preferred_name=None):
    content = fetch_bytes(url)
    name = preferred_name or unquote(url.split('/')[-1].split('?')[0]) or 'file.bin'
    name = re.sub(r'[^\w.\- ()\[\]]', '_', name, flags=re.UNICODE)
    if not name.strip('._'):
        name = 'file.bin'
    field.save(name, ContentFile(content), save=False)


class Command(BaseCommand):
    help = 'Импортирует раздел «Об учреждении» с volganet.ru'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка страниц...')
        contacts_html = fetch_text(f'{BASE}/025156/about/contacts/')
        admin_html = fetch_text(f'{BASE}/025156/about/administration/')

        self._institution(contacts_html)
        self._regional_centers(contacts_html)
        self._staff(admin_html)
        self._polnomochiya()
        self._documents()
        self._pages()
        self.stdout.write(self.style.SUCCESS('Раздел «Об учреждении» импортирован.'))

    def _institution(self, html):
        profile = InstitutionProfile.get()
        profile.full_name = (
            'Государственное казенное специализированное учреждение социального обслуживания '
            '"Городищенский социально-реабилитационный центр для несовершеннолетних"'
        )
        profile.short_name = 'ГКСУ СО "Городищенский СРЦ"'
        profile.inn = '3403016961'
        profile.kpp = '340301001'
        profile.okpo = '53589642'
        profile.ogrn = '1023405361264'
        profile.registration_info = (
            'Дата регистрации: 22 октября 2001 года\n30 октября 2001 года — постановка на учёт'
        )
        profile.founder_info = (
            'Комитет социальной защиты населения Волгоградской области\n'
            'Председатель комитета: Васильева Ольга Вячеславовна\n'
            'Приёмная председателя комитета: 30-80-00, факс: (8442) 32-12-96\n'
            'Адрес: 400087, Россия, Волгоградская обл., г. Волгоград, ул. Новороссийская, 41\n'
            'E-mail: uszn@volganet.ru'
        )
        profile.director_name = 'Кудинова Светлана Евгеньевна'
        profile.property_type = 'Собственность субъектов Российской Федерации'
        profile.branch_address = (
            '403082, Волгоградская область, Иловлинский район, х. Медведев, ул. Нагорная, 1'
        )
        profile.branch_phone = '8-84467-5-47-90'

        main_img = re.search(r'src="(/025156/about/contacts/[^"]+\.jpg)"', html, re.I)
        branch_img = re.search(r'src="(/025156/about/contacts/иловля\.jpg)"', html, re.I)
        if main_img:
            self.stdout.write('  фото: здание Городище')
            save_file_field(
                profile.main_building_photo,
                urljoin(BASE, main_img.group(1)),
                'gorodische-building.jpg',
            )
        if branch_img:
            self.stdout.write('  фото: здание Иловля')
            save_file_field(
                profile.branch_building_photo,
                urljoin(BASE, branch_img.group(1)),
                'ilovlya-building.jpg',
            )
        profile.save()

    def _regional_centers(self, html):
        RegionalSocialCenter.objects.all().delete()
        rows = re.findall(
            r'<a href="(http://soc\.volganet\.ru[^"]+)"><span[^>]*>\s*(\d+)\s*</span></a>'
            r'.*?<a href="(http://soc\.volganet\.ru[^"]+)"><span[^>]*>(.*?)</span></a>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        for _url_num, num, url_name, name in rows:
            clean_name = re.sub(r'<[^>]+>', '', name).strip()
            RegionalSocialCenter.objects.create(
                number=int(num),
                name=clean_name,
                url=url_name,
            )
        self.stdout.write(f'  центров соцзащиты: {len(rows)}')

    def _staff(self, html):
        StaffMember.objects.all().delete()
        chunks = re.split(r'<div[^>]+class="people-item"', html)
        order = 0
        for chunk in chunks[1:]:
            post_m = re.search(r'<div class="post">\s*(.*?)\s*</div>', chunk, re.DOTALL)
            name_m = re.search(r'<h2>\s*(.*?)\s*</h2>', chunk, re.DOTALL)
            phone_m = re.search(r'people-phone.*?<span>(.*?)</span>', chunk, re.DOTALL)
            email_m = re.search(r'mailto:([^"]+)"', chunk)
            img_m = re.search(r'<img src="([^"]+)"', chunk)
            position = re.sub(r'\s+', ' ', post_m.group(1)).strip() if post_m else ''
            name = re.sub(r'\s+', ' ', name_m.group(1)).strip() if name_m else ''
            phone = re.sub(r'\s+', ' ', phone_m.group(1)).strip() if phone_m else ''
            email = email_m.group(1).strip() if email_m else ''
            if not position and not name:
                continue
            order += 1
            member = StaffMember(
                name=name,
                position=position,
                phone=phone,
                email=email,
                order=order,
            )
            if img_m and 'nophoto' not in img_m.group(1):
                img_url = urljoin(BASE, img_m.group(1))
                self.stdout.write(f'  фото: {name or position}')
                save_file_field(member.photo, img_url, f'staff-{order}.jpg')
            member.save()
        self.stdout.write(f'  сотрудников: {order}')

    def _polnomochiya(self):
        tasks = [
            'обеспечение временного проживания несовершеннолетних, оставшихся без попечения родителей, '
            'находящихся в трудной жизненной ситуации, социально опасном положении',
            'оказание помощи в восстановлении социального статуса несовершеннолетних, '
            'содействие возвращению несовершеннолетних в семьи',
            'разработка и реализация индивидуальных и групповых программ социальной реабилитации несовершеннолетних',
            'обеспечение защиты прав и законных интересов несовершеннолетних',
            'организация медицинского обслуживания и обеспечения несовершеннолетних',
            'содействие органам опеки и попечительства в решении вопросов жизнеустройства '
            'несовершеннолетних, оставшихся без попечения родителей',
            'реализация индивидуальной программы предоставления социальных услуг',
        ]
        functions = [
            'Учреждение оказывает государственные услуги (выполняет работы) в соответствии с государственным '
            'заданием, сформированным в установленном порядке Учредителем.',
            'Учреждение осуществляет расчёт среднедушевого дохода в отношении получателей социальных услуг.',
            'Учреждение осуществляет формирование, ведение и постоянное обновление регистра получателей '
            'социальных услуг с учётом требований к конфиденциальности и безопасности информации.',
        ]
        for order, title, items in (
            (1, 'Основные задачи Учреждения', tasks),
            (2, 'Функции Учреждения', functions),
        ):
            section, _ = ContentSection.objects.update_or_create(
                page_slug=Page.SLUG_ABOUT_POLNOMOCHIYA,
                order=order,
                defaults={'title': title, 'content': ''},
            )
            section.items.all().delete()
            for i, text in enumerate(items, start=1):
                ListItem.objects.create(section=section, text=text, order=i)

    def _documents(self):
        AboutDocument.objects.all().delete()
        docs = [
            (AboutDocument.SECTION_CONTACTS, 'Распоряжение о создании', f'{BASE}/025156/about/contacts/распоряжение.pdf'),
            (AboutDocument.SECTION_CONTACTS, 'Свидетельство о постановке на учёт', f'{BASE}/025156/about/contacts/Свидетельство%20о%20постановке%20на%20учет%20в%20налоговый%20орган%20(1).pdf'),
            (AboutDocument.SECTION_CONTACTS, 'Приказ о структурном подразделении', f'{BASE}/025156/about/contacts/ilovepdf_merged%20(1)-1-5.pdf'),
            (AboutDocument.SECTION_CONTACTS, 'Приказ о назначении директора', f'{BASE}/025156/protivodeystvie-korruptsii/приказ%20о%20назначении%20директора.pdf'),
            (AboutDocument.SECTION_CONTACTS, 'Свидетельство о внесении в реестр гос. собственности', f'{BASE}/025156/legal/charter/свидетельство%20о%20внесении%20в%20реестр%20объектов%20государственной%20собственности%20Волгоградской%20области.jpg'),
            (AboutDocument.SECTION_RULES, 'Положение об отделении диагностики и социальной реабилитации', f'{ORG_BASE}/положение%20ОДиСР.pdf'),
            (AboutDocument.SECTION_RULES, 'Положение об отделении дневного пребывания', f'{ORG_BASE}/положение%20ОДП.pdf'),
            (AboutDocument.SECTION_RULES, 'Положение о территориально разделённом отделении для несовершеннолетних', f'{ORG_BASE}/положение%20ТРО.pdf'),
            (AboutDocument.SECTION_RULES, 'Правила внутреннего трудового распорядка', f'{ORG_BASE}/ПВТР%202024%20года.pdf'),
            (AboutDocument.SECTION_RULES, 'Правила внутреннего распорядка для получателей социальных услуг', f'{BASE}/025156/about/rules/правила%20внутреннего%20распорядка%20воспитанников.pdf'),
            (AboutDocument.SECTION_RULES, 'Коллективный договор 2024–2027 гг.', f'{BASE}/025156/protivodeystvie-korruptsii/коллективный%20договор%202024-2027.pdf'),
            (AboutDocument.SECTION_RULES, 'Кодекс этики и служебного поведения работников', f'{ORG_BASE}/кодекс%20этики.pdf'),
            (AboutDocument.SECTION_PRAVILA, 'Правила внутреннего распорядка', f'{BASE}/025156/organizatsiya-otdykha-i-ozdorovleniya/organizatsiya-otdykha-i-ozdorovlenie/правила%20втр_0001.pdf'),
            (AboutDocument.SECTION_POPECH, 'Приказ № 52-пр от 08.02.2011 «О создании Попечительского Совета»', f'{BASE}/025156/current/popechitelskiy-sovet/Приказ%20о%20создании%20попечительского%20совета.pdf'),
            (AboutDocument.SECTION_POPECH, 'Положение о Попечительском совете', f'{BASE}/025156/current/popechitelskiy-sovet/Положение%20о%20Попечительском%20совете.docx'),
            (AboutDocument.SECTION_POPECH, 'План работы попечительского совета 2026', f'{ORG_BASE}/План%20работы%20попечительского%20совета%202026.pdf'),
            (AboutDocument.SECTION_POPECH, 'План работы попечительского совета 2025', f'{ORG_BASE}/План%20работы%20попечительского%20совета%202025.pdf'),
            (AboutDocument.SECTION_POPECH, 'Отчёт о работе Попечительского совета 2025', f'{ORG_BASE}/Отчет%20о%20работе%20Попечительского%20совета%202025.pdf'),
            (AboutDocument.SECTION_POPECH, 'Отчёт о работе Попечительского совета 2024', f'{ORG_BASE}/Отчет%20о%20работе%20Попечительского%20совета%202024.pdf'),
            (AboutDocument.SECTION_POPECH, 'План работы попечительского совета 2024', f'{ORG_BASE}/план%20работы%20попечительского%20совета%202024.pdf'),
            (AboutDocument.SECTION_POPECH, 'План работы попечительского совета 2023', f'{BASE}/025156/current/plan-finans/план%20Попечительского%20совета%202023%20год.pdf'),
            (AboutDocument.SECTION_POPECH, 'Отчёт о работе Попечительского совета 2023', f'{ORG_BASE}/Отчет%20о%20работе%20Попечительского%20совета%202023.pdf'),
            (AboutDocument.SECTION_POPECH, 'Состав Попечительского Совета', f'{BASE}/025156/current/plan-finans/состав.docx'),
        ]
        for order, (section, title, url) in enumerate(docs, start=1):
            self.stdout.write(f'  документ: {title[:50]}...')
            doc = AboutDocument(section=section, title=title, order=order)
            try:
                save_file_field(doc.file, url)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'    пропуск ({exc})'))
            doc.save()

    def _pages(self):
        pages = [
            (Page.SLUG_ABOUT, 'Об учреждении — Городищенский СРЦ', 'Об учреждении', 'Об учреждении социального обслуживания', 'Сведения о ГКСУ СО «Городищенский СРЦ»: контакты, полномочия, руководство, документы.'),
            (Page.SLUG_ABOUT_CONTACTS, 'Контакты — Городищенский СРЦ', 'Контакты', 'Контакты', ''),
            (Page.SLUG_ABOUT_POLNOMOCHIYA, 'Полномочия — Городищенский СРЦ', 'Полномочия', 'Полномочия (задачи и функции)', ''),
            (Page.SLUG_ABOUT_RUKOVODSTVO, 'Руководство — Городищенский СРЦ', 'Руководство', 'Руководство', ''),
            (Page.SLUG_ABOUT_LOKALNYE, 'Локальные акты — Городищенский СРЦ', 'Документы', 'Внутренние локальные акты', ''),
            (Page.SLUG_ABOUT_PRAVILA, 'Правила распорядка — Городищенский СРЦ', 'Документы', 'Правила внутреннего распорядка', ''),
            (Page.SLUG_ABOUT_POPECH, 'Попечительский совет — Городищенский СРЦ', 'Документы', 'Попечительский совет', ''),
        ]
        for slug, meta_title, badge, h1, intro in pages:
            Page.objects.update_or_create(
                slug=slug,
                defaults={
                    'meta_title': meta_title,
                    'badge': badge,
                    'h1': h1,
                    'intro': intro,
                },
            )
        Page.objects.filter(slug='kontakty').delete()
