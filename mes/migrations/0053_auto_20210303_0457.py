# Generated by Django 3.1.5 on 2021-03-02 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0052_auto_20210302_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='style',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
