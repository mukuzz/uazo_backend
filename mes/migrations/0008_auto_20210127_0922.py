# Generated by Django 3.1.5 on 2021-01-27 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0007_auto_20210127_0849'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qcinput',
            old_name='production_sesion',
            new_name='production_session',
        ),
    ]