# Generated by Django 3.1.5 on 2021-01-26 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qcinput',
            old_name='prosdction_sesion',
            new_name='production_sesion',
        ),
    ]
