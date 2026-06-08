import os


def bootstrap_render():
    if os.environ.get('RENDER') != 'true':
        return

    from django.core.management import call_command
    from main.models import Page

    call_command('migrate', '--noinput', verbosity=0)

    if not Page.objects.filter(slug=Page.SLUG_INDEX).exists():
        call_command('loaddata', 'initial_data', verbosity=0)

    _ensure_superuser()


def _ensure_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    if not username or not password:
        return

    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return

    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
    User.objects.create_superuser(username, email, password)
