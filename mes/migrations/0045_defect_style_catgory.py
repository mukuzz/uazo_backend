# Generated by Django 3.1.5 on 2021-02-28 22:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0044_auto_20210301_0326'),
    ]

    operations = [
        migrations.AddField(
            model_name='defect',
            name='style_catgory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='mes.stylecategory'),
        ),
    ]
