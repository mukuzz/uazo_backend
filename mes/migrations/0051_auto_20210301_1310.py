# Generated by Django 3.1.5 on 2021-03-01 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0050_auto_20210301_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sizequantity',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mes.style'),
        ),
    ]
