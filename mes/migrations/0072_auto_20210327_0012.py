# Generated by Django 3.1.5 on 2021-03-26 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0071_auto_20210326_2304'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operation',
            options={'verbose_name': 'Operation', 'verbose_name_plural': 'Operations'},
        ),
        migrations.AddField(
            model_name='style',
            name='operations',
            field=models.ManyToManyField(to='mes.Operation', verbose_name='operations'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='operation',
            field=models.CharField(max_length=256, unique=True, verbose_name='operation'),
        ),
    ]
