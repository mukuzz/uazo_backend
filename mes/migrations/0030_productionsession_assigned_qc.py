# Generated by Django 3.1.5 on 2021-02-25 23:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mes', '0029_remove_productionorder_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionsession',
            name='assigned_qc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
