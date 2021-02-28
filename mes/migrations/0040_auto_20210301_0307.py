# Generated by Django 3.1.5 on 2021-02-28 21:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mes', '0039_auto_20210228_2157'),
    ]

    operations = [
        migrations.CreateModel(
            name='StyleCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=256)),
            ],
        ),
        migrations.RemoveField(
            model_name='style',
            name='category',
        ),
        migrations.AlterField(
            model_name='deletedqcinput',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='deletedqcinput',
            name='production_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.productionsession'),
        ),
        migrations.AlterField(
            model_name='deletedqcinput',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='deletedqcinput',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.sizequantity'),
        ),
        migrations.AlterField(
            model_name='line',
            name='location',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='mes.linelocation'),
        ),
        migrations.AlterField(
            model_name='line',
            name='number',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='productionorder',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.buyer'),
        ),
        migrations.AlterField(
            model_name='productionorder',
            name='due_date_time',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(models.DateTimeField(default=django.utils.timezone.now), message='due date time should be greater than receive date time')]),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='assigned_qc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='end_time',
            field=models.DateTimeField(default=django.utils.timezone.now, validators=[django.core.validators.MinValueValidator(models.DateTimeField(default=django.utils.timezone.now), message='end time should be greater than start time')]),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='helpers',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='line',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='mes.line'),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='operators',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.style'),
        ),
        migrations.AlterField(
            model_name='productionsession',
            name='target',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='production_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.productionsession'),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.sizequantity'),
        ),
        migrations.AlterField(
            model_name='sizequantity',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='sizequantity',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.style'),
        ),
        migrations.AlterField(
            model_name='style',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mes.productionorder'),
        ),
        migrations.AlterField(
            model_name='style',
            name='sam',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0, message='sam should be greater than 0')]),
        ),
    ]
