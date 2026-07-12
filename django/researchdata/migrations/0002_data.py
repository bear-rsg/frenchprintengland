from django.db import migrations
from researchdata import models


def create_genders(apps, schema_editor):
    """
    Creates new Gender objects
    """

    names = ['Female', 'Male', 'Other']

    for name in names:
        models.Gender(name=name).save()


def create_agent_roles(apps, schema_editor):
    """
    Creates new AgentRole objects
    """

    names = [
        'Author',
        'Contributor',
        'Dedicatee',
        'Publisher',
        'Translator',
        'Owner'
    ]

    for name in names:
        models.AgentRole(name=name).save()


def create_languages(apps, schema_editor):
    """
    Creates new Language objects
    """

    names = ['English', 'French']

    for name in names:
        models.Language(name=name).save()


def create_formats_of_publication(apps, schema_editor):
    """
    Creates new AgentRole objects
    """

    names = ['4to', '8to']

    for name in names:
        models.FormatOfPublication(name=name).save()


class Migration(migrations.Migration):

    dependencies = [
        ('researchdata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_genders),
        migrations.RunPython(create_agent_roles),
        migrations.RunPython(create_languages),
        migrations.RunPython(create_formats_of_publication),
    ]
