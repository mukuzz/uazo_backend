# Generated by Django 3.1.5 on 2021-03-02 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0051_auto_20210301_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deletedqcinput',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='mes.sizequantity'),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='mes.sizequantity'),
        ),
    ]