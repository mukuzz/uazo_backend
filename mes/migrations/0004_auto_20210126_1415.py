# Generated by Django 3.1.5 on 2021-01-26 14:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0003_auto_20210126_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productionorder',
            name='receive_date_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
