# Generated by Django 3.1.5 on 2021-04-06 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0073_auto_20210330_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defect',
            name='operation',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
