# Generated by Django 3.1.5 on 2021-03-20 12:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0061_qcappstate_inputs_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionSessionBreak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(default=django.utils.timezone.now)),
                ('end_time', models.TimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AlterField(
            model_name='deletedqcinput',
            name='input_type',
            field=models.CharField(choices=[('ftt', 'pass'), ('rejected', 'rejected'), ('rectified', 'rectified'), ('defective', 'defective')], max_length=56),
        ),
        migrations.AlterField(
            model_name='qcinput',
            name='input_type',
            field=models.CharField(choices=[('ftt', 'pass'), ('rejected', 'rejected'), ('rectified', 'rectified'), ('defective', 'defective')], max_length=56),
        ),
        migrations.AddField(
            model_name='productionsession',
            name='breaks',
            field=models.ManyToManyField(blank=True, to='mes.ProductionSessionBreak'),
        ),
    ]
