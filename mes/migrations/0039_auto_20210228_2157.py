# Generated by Django 3.1.5 on 2021-02-28 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0038_auto_20210228_2129'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buyer',
            old_name='name',
            new_name='buyer',
        ),
    ]
