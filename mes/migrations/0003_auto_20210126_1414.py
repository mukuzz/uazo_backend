# Generated by Django 3.1.5 on 2021-01-26 14:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0002_auto_20210126_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productionsession',
            name='duration',
        ),
        migrations.AddField(
            model_name='productionsession',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
