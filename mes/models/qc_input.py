from django.db import models, connection
from django.utils import timezone
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import uuid


class QcInputTemplate(models.Model):
    FTT = 'ftt'
    REJECTED = 'rejected'
    RECTIFIED = 'rectified'
    DEFECTIVE = 'defective'
    QC_INPUT_TYPES = (
        (FTT, 'pass'),
        (REJECTED, 'rejected'),
        (RECTIFIED,'rectified'),
        (DEFECTIVE, 'defective')
    )
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField(default=timezone.now)
    is_ftt = models.BooleanField(default=True)
    input_type = models.CharField(max_length=56, choices=QC_INPUT_TYPES)
    size = models.ForeignKey('mes.SizeQuantity', on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    defects = models.ManyToManyField('mes.Defect', blank=True)
    operation_defects = models.ManyToManyField('mes.OperationDefect', blank=True)
    production_session = models.ForeignKey('mes.ProductionSession', on_delete=models.PROTECT)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        abstract = True
        permissions = [('can_receive_new_qc_input_notification','Can receive notifications for new QC inputs')]

    def __str__(self):
        if self.size == None:
            return f'{self.quantity} - {self.production_session.style}'
        else:
            return f'{self.size} - {self.quantity} - {self.production_session.style}'


class QcInput(QcInputTemplate):
    pass

class DeletedQcInput(QcInputTemplate):
    deletion_datetime = models.DateTimeField(default=timezone.now)

def migrate_qc_input(sender, instance, **kwargs):
    # Migrate the to be deleted QcInput to DeletedQcInput
    delted_qc_input = DeletedQcInput.objects.create(
        id = instance.id,
        datetime=instance.datetime,
        is_ftt=instance.is_ftt,
        input_type=instance.input_type,
        size=instance.size,
        quantity=instance.quantity,
        production_session=instance.production_session,
        creator=instance.creator,
        deletion_datetime=timezone.now()
    )
    if instance.input_type == 'defective':
        for defect in instance.defects.all():
            delted_qc_input.defects.add(defect.pk)
        for operation_defect in instance.operation_defects.all():
            delted_qc_input.operation_defects.add(operation_defect.pk)

pre_delete.connect(migrate_qc_input, QcInput)


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_channels_message(sender, instance, **kwargs):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "sse_group_" + connection.schema_name,
        {
            "type": "send_new_qcinput_update"
        }
    )

post_delete.connect(send_channels_message, QcInput)
post_save.connect(send_channels_message, QcInput)