# Generated by Django 3.1.5 on 2021-03-26 08:49

from django.db import migrations

def fill_operation_defects_table(apps, schema_editor):
    OperationDefect = apps.get_model('mes', 'OperationDefect')
    Defect = apps.get_model('mes', 'Defect')
    to_save = [OperationDefect(defect=defect) for defect in Defect.objects.all()]
    OperationDefect.objects.bulk_create(to_save)

def copy_qcinput_defects_to_defect_operations(apps, schema_editor):
    QcInput = apps.get_model('mes', 'QcInput')
    OperationDefect = apps.get_model('mes', 'OperationDefect')
    for qc_input in QcInput.objects.all():
        for defect in qc_input.defects.all():
            operation_defect = OperationDefect.objects.get(defect=defect)
            qc_input.operation_defects.add(operation_defect)

def copy_deleted_qcinput_defects_to_defect_operations(apps, schema_editor):
    DeletedQcInput = apps.get_model('mes', 'DeletedQcInput')
    OperationDefect = apps.get_model('mes', 'OperationDefect')
    for deleted_qc_input in DeletedQcInput.objects.all():
        for defect in deleted_qc_input.defects.all():
            operation_defect = OperationDefect.objects.get(defect=defect)
            deleted_qc_input.operation_defects.add(operation_defect)

class Migration(migrations.Migration):

    dependencies = [
        ('mes', '0068_auto_20210326_1411'),
    ]

    operations = [
        migrations.RunPython(fill_operation_defects_table),
        migrations.RunPython(copy_qcinput_defects_to_defect_operations),
        migrations.RunPython(copy_deleted_qcinput_defects_to_defect_operations),
    ]