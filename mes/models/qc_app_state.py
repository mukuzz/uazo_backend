from django.db import models
from django.utils import timezone
from django.conf import settings

class QcAppState(models.Model):
    signed_in_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    inputs_count = models.PositiveIntegerField()
    persisted_inputs_count = models.PositiveIntegerField()
    synced_inputs_count = models.PositiveIntegerField()
    production_session = models.ForeignKey('mes.ProductionSession', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.datetime} - {self.production_session}'