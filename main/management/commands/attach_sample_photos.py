from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from main.models import News


class Command(BaseCommand):
    help = 'Добавляет примеры новостей с фотографиями'

    def handle(self, *args, **options):
        items = [
            (
                'Режим работы учреждения в 2026 году',
                date(2026, 1, 15),
                'news-schedule.jpg',
                'ГКСУ СО «Городищенский социально-реабилитационный центр для несовершеннолетних» информирует о режиме работы в 2026 году.',
            ),
            (
                'Творческие занятия в дневном отделении',
                date(2026, 3, 12),
                'news-activity.jpg',
                'В дневном отделении центра прошли творческие занятия для воспитанников.',
            ),
            (
                'Весенние мероприятия для воспитанников',
                date(2026, 4, 8),
                'news-spring.jpg',
                'На территории центра состоялись весенние мероприятия для воспитанников.',
            ),
            (
                'Расписание личного приёма директора',
                date(2026, 2, 1),
                'news-meeting.jpg',
                'Утверждено расписание личного приёма граждан директором учреждения на 2026 год.',
            ),
        ]
        news_dir = Path(settings.MEDIA_ROOT) / 'news'
        News.objects.all().delete()
        for order, (title, published_at, filename, body) in enumerate(items):
            news = News.objects.create(
                title=title,
                body=body,
                published_at=published_at,
                order=order,
                is_published=True,
            )
            path = news_dir / filename
            if not path.exists():
                self.stderr.write(f'Файл не найден: {path}')
                continue
            with path.open('rb') as f:
                news.image.save(filename, File(f), save=True)
            self.stdout.write(f'OK: {title}')
