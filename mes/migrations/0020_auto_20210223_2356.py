# Generated by Django 3.1.5 on 2021-02-23 18:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0019_auto_20210223_2353'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deletedqcinput',
            options={'permissions': [('get_add_notification', 'Can receive notifications for new QC inputs')]},
        ),
        migrations.AlterModelOptions(
            name='qcinput',
            options={'permissions': [('get_add_notification', 'Can receive notifications for new QC inputs')]},
        ),
    ]
