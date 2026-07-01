from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.db import transaction
from account import models


def insert_test_users(apps, schema_editor):
    """
    Inserts Test User objects
    """

    users = [
        {
            "password": make_password("mike"),
            "first_name": "Mike",
            "last_name": "Allaway",
            "email": "mike@mike.com",
            "is_superuser": True,
            "is_staff": True,
        },
    ]

    for user in users:
        with transaction.atomic():
            models.User(**user).save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial')
    ]

    operations = [
        migrations.RunPython(insert_test_users),
    ]
