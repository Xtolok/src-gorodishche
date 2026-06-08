from django.core.management.base import BaseCommand

from config.superuser import EMAIL, PASSWORD, USERNAME, ensure_superuser


class Command(BaseCommand):
    help = 'Создаёт или сбрасывает админа admin / admin'

    def handle(self, *args, **options):
        result = ensure_superuser()
        self.stdout.write(self.style.SUCCESS(
            f'Админ {result}: логин={USERNAME}, пароль={PASSWORD}, email={EMAIL}'
        ))
