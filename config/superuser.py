USERNAME = 'admin'
EMAIL = 'admin@admin.admin'
PASSWORD = 'admin'


def ensure_superuser():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.filter(username=USERNAME).first()

    if user:
        user.email = EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.set_password(PASSWORD)
        user.save()
        return 'updated'

    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    return 'created'
