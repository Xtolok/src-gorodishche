import re
from urllib.parse import unquote

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from main.management.commands.import_about_volganet import BASE, fetch_bytes, fetch_text
from main.management.commands.import_legal_volganet import resolve_url, strip_tags
from main.models import CurrentActivitySection, Page

SECTIONS = [
    ('uslugi', 'Социальные услуги', '/025156/current/services/'),
    ('formy', 'Формы социального обслуживания', '/025156/current/forms/'),
    ('vidy', 'Виды социальных услуг', '/025156/current/types/'),
    ('chislennost', 'Численность получателей социальных услуг', '/025156/current/number/'),
    ('obem', 'Объем предоставляемых социальных услуг', '/025156/current/volume/'),
    ('mesta', 'Количество свободных мест для приема получателей социальных услуг', '/025156/current/places/'),
    ('plan-finans', 'План финансово-хозяйственной деятельности учреждения', '/025156/current/plan-finans/'),
    ('otchety', 'Отчеты (об исполнении предписаний)', '/025156/current/reports/'),
    ('inaya-dokumentatsiya', 'Иная документация', '/025156/current/inaya-dokumentatsiya/'),
    ('otsenka-kachestva', 'Оценка качества предоставляемых услуг', '/025156/current/nezavisimaya-otsenka-kachestva-uslug/'),
    (
        'mat-teh',
        'Материально-техническое обеспечение предоставления социальных услуг',
        '/025156/current/materialno-tekhnicheskoe-obespechenie-predostavleniya-sotsialnykh-uslug.php',
    ),
    (
        'poryadok',
        'Порядок и условия предоставления социальных услуг',
        '/025156/current/poryadok-i-usloviya-predostavleniya-sotsialnykh-uslug.php',
    ),
    ('predpisaniya', 'Предписания органов', '/025156/current/predpisaniya-organov.php'),
]

FILE_EXT = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.rtf', '.odt')
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


def extract_content(html):
    match = re.search(r'<h1>.*?</h1>(.*?)<!--End content column-->', html, re.DOTALL | re.IGNORECASE)
    if not match:
        return ''
    content = match.group(1)
    content = re.sub(r'<ul class="subsection-menu">.*?</ul>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<div id="bxdynamic[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
    return content.strip()


def is_downloadable(href):
    if not href or href in ('#', '') or href.startswith('javascript:'):
        return False
    path = unquote(href.split('?')[0]).lower()
    return any(path.endswith(ext) or f'{ext}.' in path for ext in FILE_EXT + IMAGE_EXT)


def safe_filename(url):
    name = unquote(url.split('/')[-1].split('?')[0]) or 'file.bin'
    name = re.sub(r'[^\w.\- ()\[\]]', '_', name, flags=re.UNICODE)
    return name if name.strip('._') else 'file.bin'


def localize_asset(url, cache, stdout, subdir='current'):
    full_url = resolve_url(url)
    if full_url in cache:
        return cache[full_url]
    if not is_downloadable(url):
        cache[full_url] = url
        return url
    try:
        content = fetch_bytes(full_url)
        fname = safe_filename(full_url)
        base, dot, ext = fname.rpartition('.')
        path = f'{subdir}/{fname}'
        n = 1
        while default_storage.exists(path):
            n += 1
            path = f'{subdir}/{base}_{n}.{ext}' if dot else f'{subdir}/file_{n}.bin'
        saved = default_storage.save(path, ContentFile(content))
        cache[full_url] = default_storage.url(saved)
    except Exception as exc:
        stdout.write(f'    пропуск файла {full_url[:70]}: {exc}')
        cache[full_url] = full_url
    return cache[full_url]


def process_html(content, cache, stdout, subdir='current'):
    def replace_link(match):
        href = match.group(1)
        if href.startswith('http') and 'volganet.ru' not in href:
            return match.group(0)
        new_href = localize_asset(href, cache, stdout, subdir)
        return f'href="{new_href}"'

    def replace_src(match):
        src = match.group(1)
        if src.startswith('http') and 'volganet.ru' not in src:
            return match.group(0)
        new_src = localize_asset(src, cache, stdout, subdir)
        return f'src="{new_src}"'

    content = re.sub(r'href="([^"]+)"', replace_link, content)
    content = re.sub(r'src="([^"]+)"', replace_src, content)
    content = content.replace('\xa0', ' ').replace('&nbsp;', ' ')
    content = re.sub(r'<table(?![^>]*class=)', '<table class="data-table"', content, flags=re.IGNORECASE)
    return content


class Command(BaseCommand):
    help = 'Импортирует раздел «Текущая деятельность» с volganet.ru'

    def handle(self, *args, **options):
        Page.objects.update_or_create(
            slug=Page.SLUG_CURRENT,
            defaults={
                'meta_title': 'Текущая деятельность — Городищенский СРЦ',
                'badge': 'Текущая деятельность',
                'h1': 'Текущая деятельность',
                'intro': 'Сведения о социальных услугах, показателях деятельности, планах и отчётности учреждения.',
            },
        )

        CurrentActivitySection.objects.all().delete()
        cache = {}

        for order, (section_slug, title, path) in enumerate(SECTIONS, start=1):
            self.stdout.write(f'Раздел: {title}')
            html = fetch_text(BASE + path)
            raw = extract_content(html)
            if not strip_tags(raw):
                self.stdout.write(self.style.WARNING('  пустой контент'))
            body_html = process_html(raw, cache, self.stdout)
            CurrentActivitySection.objects.create(
                slug=section_slug,
                title=title,
                body_html=body_html,
                order=order,
            )
            links = len(re.findall(r'href="[^"]+"', body_html))
            self.stdout.write(f'  готово, ссылок: {links}')

        self.stdout.write(self.style.SUCCESS('Раздел «Текущая деятельность» импортирован.'))
