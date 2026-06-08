import os

RENDER_DEFAULTS = {
    'username': 'admin',
    'email': 'admin@admin.admin',
    'password': 'admin',
}


def ensure_superuser():
    if os.environ.get('RENDER') != 'true':
        return

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', RENDER_DEFAULTS['username'])
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', RENDER_DEFAULTS['password'])
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', RENDER_DEFAULTS['email'])

    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return

    User.objects.create_superuser(username, email, password)
