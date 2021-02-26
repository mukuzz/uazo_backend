from django.db import models
from django.utils import timezone
from .style import Style
from .line import Line
from django.conf import settings


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.DO_NOTHING, blank=True)
    operators = models.IntegerField()
    helpers = models.IntegerField()
    assigned_qc = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    target = models.IntegerField()

    def __str__(self):
        return f'{timezone.localtime(self.start_time).hour} to {timezone.localtime(self.end_time).hour} - {self.style}'