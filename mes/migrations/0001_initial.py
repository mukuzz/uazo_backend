# Generated by Django 3.1.5 on 2021-01-26 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer', models.CharField(max_length=256)),
                ('quantity', models.IntegerField()),
                ('receive_date_time', models.DateTimeField()),
                ('due_date_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductionSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_number', models.CharField(max_length=256)),
                ('operators', models.IntegerField()),
                ('helpers', models.IntegerField()),
                ('date', models.DateField()),
                ('duration', models.DurationField()),
                ('start_time', models.DateTimeField()),
                ('target', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=256)),
                ('category', models.CharField(max_length=256)),
                ('color', models.CharField(max_length=256)),
                ('sizes', models.JSONField()),
                ('name', models.CharField(max_length=256)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mes.productionorder')),
            ],
        ),
        migrations.CreateModel(
            name='QcInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('defect_type', models.CharField(max_length=256)),
                ('size', models.CharField(max_length=16)),
                ('quantity', models.IntegerField()),
                ('prosdction_sesion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mes.productionsession')),
            ],
        ),
        migrations.AddField(
            model_name='productionsession',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mes.style'),
        ),
    ]
