# Generated by Django 3.1.5 on 2021-02-28 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0046_auto_20210301_0330'),
    ]

    operations = [
        migrations.RenameField(
            model_name='defect',
            old_name='style_catgory',
            new_name='style_category',
        ),
    ]
