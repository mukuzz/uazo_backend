from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete 
from django.dispatch import receiver
from .prod_session import ProductionSession
from .defect import Defect


class QcInputTemplate(models.Model):
    QC_INPUT_TYPES = (
        ('ftt', 'ftt'),
        ('rejected', 'rejected'),
        ('rectified','rectified'),
        ('defective', 'defective')
    )
    datetime = models.DateTimeField(default=timezone.now)
    ftt = models.BooleanField(default=True)
    input_type = models.CharField(max_length=56, choices=QC_INPUT_TYPES)
    size = models.CharField(max_length=16)
    quantity = models.IntegerField(default=1)
    defects = models.ManyToManyField(Defect)
    production_session = models.ForeignKey(ProductionSession, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.size} - {self.quantity} - {self.production_session.style}'


class QcInput(QcInputTemplate):
    pass

class DeletedQcInput(QcInputTemplate):
    deletion_datetime = models.DateTimeField(default=timezone.now)

def migrate_qc_input(sender, instance, **kwargs):
    # Migrate the to be deleted QcInput to DeletedQcInput
    delted_qc_input = DeletedQcInput.objects.create(
        datetime=instance.datetime,
        ftt=instance.ftt,
        input_type=instance.input_type,
        size=instance.size,
        quantity=instance.quantity,
        production_session=instance.production_session,
        deletion_datetime=timezone.now()
    )
    if instance.input_type == 'defective':
        for defect in instance.defects.all():
            delted_qc_input.defects.add(defect.pk)

pre_delete.connect(migrate_qc_input, QcInput)