# Generated by Django 3.1.5 on 2021-04-18 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0074_auto_20210406_1108'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='operationdefect',
            name='unique_operation_defect',
        ),
    ]
