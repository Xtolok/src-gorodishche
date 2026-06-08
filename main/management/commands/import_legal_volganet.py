import re

from django.core.management.base import BaseCommand

from main.management.commands.import_about_volganet import BASE, fetch_text, save_file_field
from main.models import LegalItem, LegalSection, Page

SECTIONS = [
    ('ustav', Page.SLUG_LEGAL_USTAV, 'Устав учреждения', '/025156/legal/charter/'),
    ('litsenzii', Page.SLUG_LEGAL_LITSENZII, 'Лицензии на осуществление деятельности', '/025156/legal/licenses/'),
    ('federal', Page.SLUG_LEGAL_FEDERAL, 'Федеральное законодательство', '/025156/legal/acts/federalnoe-zakonodatelstvo/'),
    ('regional', Page.SLUG_LEGAL_REGIONAL, 'Законодательство Волгоградской области', '/025156/legal/acts/zakonodatelstvo-volgogradskoy-oblasti/'),
    ('normativy', Page.SLUG_LEGAL_NORMATIVY, 'Нормативы и порядки', '/025156/legal/acts/normativy-i-poryadki/'),
    ('sout', Page.SLUG_LEGAL_SOUT, 'Специальная оценка условий труда', '/025156/legal/sout/'),
]


def strip_tags(text):
    clean = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', clean).strip()


def parse_page_documents(html):
    match = re.search(r'<h1>.*?</h1>(.*?)<!--End content column-->', html, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    content = match.group(1)
    content = re.sub(r'<ul class="subsection-menu">.*?</ul>', '', content, flags=re.DOTALL | re.IGNORECASE)

    current_year = ''
    collected = []
    for link_match in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', content, re.IGNORECASE):
        pos = link_match.start()
        href = link_match.group(1).strip()
        if not href or href in ('#', '') or href.startswith('javascript:'):
            continue
        year_in_html = re.findall(r'>(20\d{2})<', content[max(0, pos - 3000):pos])
        year_in_href = re.findall(r'20\d{2}', href)
        current_year = year_in_html[-1] if year_in_html else (year_in_href[-1] if year_in_href else '')
        inner = strip_tags(link_match.group(2))
        line_start = max(0, content.rfind('<br', 0, pos), content.rfind('<p', 0, pos))
        line = content[line_start:content.find('<br', pos) if content.find('<br', pos) != -1 else pos + 400]
        before = strip_tags(line[:link_match.start() - line_start])

        title = inner if len(inner) >= len(before) else before
        title = re.sub(r'\s+', ' ', title.replace('\xa0', ' ').replace('&nbsp;', ' ')).strip()
        title = title.rstrip(' скачать').strip()
        if title.lower() in ('скачать', ''):
            continue
        if current_year and current_year not in title:
            if len(title) <= 6 or title.upper() == 'СОУТ':
                title = f'СОУТ ({current_year})'
            else:
                title = f'{title} ({current_year})'
        if len(title) < 3:
            continue
        collected.append((title[:500], href))

    seen = {}
    order = []
    for title, href in collected:
        if href not in seen:
            order.append(href)
        if href not in seen or len(title) > len(seen[href]):
            seen[href] = title
    return [(seen[href], href) for href in order]


def resolve_url(href):
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        return BASE + href
    return f'{BASE}/025156/{href.lstrip("/")}'


def is_local(href):
    return href.startswith('/') or '442fz.volganet.ru' in href


class Command(BaseCommand):
    help = 'Импортирует правовую основу с volganet.ru'

    def handle(self, *args, **options):
        LegalSection.objects.all().delete()
        pages_meta = [
            (Page.SLUG_LEGAL, 'Правовая основа деятельности — Городищенский СРЦ', 'Правовая основа', 'Правовая основа деятельности', 'Устав, лицензии, нормативные акты и СОУТ.'),
            (Page.SLUG_LEGAL_ACTS, 'Нормативные акты — Городищенский СРЦ', 'Правовая основа', 'Нормативные правовые акты', 'Федеральное и региональное законодательство, нормативы и порядки.'),
        ]
        for slug, meta_title, badge, h1, intro in pages_meta:
            Page.objects.update_or_create(
                slug=slug,
                defaults={'meta_title': meta_title, 'badge': badge, 'h1': h1, 'intro': intro},
            )

        for order, (section_slug, page_slug, title, path) in enumerate(SECTIONS, start=1):
            self.stdout.write(f'Раздел: {title}')
            html = fetch_text(BASE + path)
            Page.objects.update_or_create(
                slug=page_slug,
                defaults={
                    'meta_title': f'{title} — Городищенский СРЦ',
                    'badge': 'Правовая основа',
                    'h1': title,
                },
            )
            section = LegalSection.objects.create(slug=section_slug, title=title, order=order)
            docs = parse_page_documents(html)
            for i, (doc_title, href) in enumerate(docs, start=1):
                full_url = resolve_url(href)
                item = LegalItem(section=section, text=doc_title[:500], order=i)
                if is_local(href):
                    try:
                        self.stdout.write(f'  ↓ {doc_title[:60]}...')
                        save_file_field(item.file, full_url)
                    except Exception as exc:
                        self.stdout.write(self.style.WARNING(f'    пропуск файла: {exc}'))
                        item.external_url = full_url
                else:
                    item.external_url = full_url
                item.save()
            self.stdout.write(f'  документов: {len(docs)}')

        self.stdout.write(self.style.SUCCESS('Правовая основа импортирована.'))
