# Generated by Django 3.1.5 on 2021-02-28 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0035_auto_20210228_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=256)),
            ],
        ),
        migrations.AlterField(
            model_name='line',
            name='location',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='mes.linenumber'),
        ),
    ]
