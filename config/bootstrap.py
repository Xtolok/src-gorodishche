import os


def bootstrap_render():
    if os.environ.get('RENDER') != 'true':
        return

    from django.core.management import call_command
    from main.models import Page

    call_command('migrate', '--noinput', verbosity=0)

    if not Page.objects.filter(slug=Page.SLUG_INDEX).exists():
        call_command('loaddata', 'initial_data', verbosity=0)

    from config.superuser import ensure_superuser

    ensure_superuser()
