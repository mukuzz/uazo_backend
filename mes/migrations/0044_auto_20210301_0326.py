# Generated by Django 3.1.5 on 2021-02-28 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0043_auto_20210301_0324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='style',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='mes.stylecategory'),
            preserve_default=False,
        ),
    ]