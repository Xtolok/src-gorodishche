from django.core.management import call_command
from django.core.management.base import BaseCommand

from main.models import Page


class Command(BaseCommand):
    help = 'Загружает initial_data.json, если база пустая'

    def handle(self, *args, **options):
        if Page.objects.filter(slug=Page.SLUG_INDEX).exists():
            self.stdout.write('Данные уже есть, пропуск.')
        else:
            self.stdout.write('База пустая, загружаю initial_data...')
            call_command('loaddata', 'initial_data')
            self.stdout.write(self.style.SUCCESS('Данные загружены.'))

