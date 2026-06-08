import re

from django.core.management.base import BaseCommand

from main.management.commands.import_about_volganet import BASE, fetch_text
from main.management.commands.import_current_volganet import extract_content, process_html
from main.management.commands.import_legal_volganet import strip_tags
from main.models import NokContent, Page

NOK_PATH = '/025156/nezavisimaya-otsenka-kachestva-nok/'


def clean_nok_html(html):
    html = re.sub(
        r'<p>\s*<b>Оцените нашу работу:</b>\s*</p>\s*'
        r'<p>\s*<a[^>]*>Обратная связь</a>.*?</p>',
        '',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(r'<p>\s*(?:<br\s*/?>\s*)*<img[^>]*>.*?</p>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</div>\s*$', '', html.strip())
    return html.strip()

class Command(BaseCommand):
    help = 'Импортирует раздел «Независимая оценка качества НОК» с volganet.ru'

    def handle(self, *args, **options):
        Page.objects.update_or_create(
            slug=Page.SLUG_NOK,
            defaults={
                'meta_title': 'Независимая оценка качества НОК — Городищенский СРЦ',
                'badge': 'Независимая оценка качества',
                'h1': 'Независимая оценка качества НОК',
                'intro': '',
            },
        )

        self.stdout.write('Загрузка страницы...')
        html = fetch_text(BASE + NOK_PATH)
        raw = extract_content(html)
        if not strip_tags(raw):
            self.stdout.write(self.style.WARNING('Пустой контент'))
        cache = {}
        body_html = clean_nok_html(process_html(raw, cache, self.stdout, subdir='nok'))
        content = NokContent.get()
        content.body_html = body_html
        content.save()

        links = body_html.count('href="')
        images = body_html.count('src="')
        self.stdout.write(f'Готово: ссылок {links}, изображений {images}')
        self.stdout.write(self.style.SUCCESS('Раздел «Независимая оценка качества НОК» импортирован.'))
