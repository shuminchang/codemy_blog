# Generated by Django 4.2.6 on 2024-01-18 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('predict', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PredResults',
            new_name='IrisPredResults',
        ),
    ]
