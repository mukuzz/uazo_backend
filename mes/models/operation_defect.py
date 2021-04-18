from django.db import models
from django.db.models.signals import post_save

class OperationDefect(models.Model):
    operation = models.ForeignKey('mes.Operation', null=True, blank=True, on_delete=models.CASCADE)
    defect = models.ForeignKey('mes.Defect', on_delete=models.CASCADE)

    def __str__(self):
        if not self.operation:
            return self.defect.defect
        return f'{self.operation.operation} - {self.defect.defect}'

class Defect(models.Model):
    operation = models.CharField(max_length=256, blank=True)
    defect = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.defect

def create_operation_defects_for_new_defect(sender, instance, **kwargs):
    if kwargs['created']:
        operation_defects = [OperationDefect(operation=operation, defect=instance) for operation in Operation.objects.all()]
        OperationDefect.objects.bulk_create(operation_defects)
        OperationDefect(defect=instance).save()

post_save.connect(create_operation_defects_for_new_defect, Defect)


class Operation(models.Model):
    operation = models.CharField(verbose_name="operation", max_length=256, unique=True)

    class Meta:
        verbose_name = "Operation"
        verbose_name_plural = "Operations"

    def __str__(self):
        return self.operation

def create_operation_defects_for_new_operation(sender, instance, **kwargs):
    if kwargs['created']:
        operation_defects = [OperationDefect(operation=instance, defect=defect) for defect in Defect.objects.all()]
        OperationDefect.objects.bulk_create(operation_defects)

post_save.connect(create_operation_defects_for_new_operation, Operation)