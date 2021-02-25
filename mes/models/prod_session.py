from django.db import models
from django.utils import timezone
from .style import Style
from .line import Line


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.DO_NOTHING, blank=True)
    operators = models.IntegerField()
    helpers = models.IntegerField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    target = models.IntegerField()

    def __str__(self):
        return f'{timezone.localtime(self.start_time).hour} to {timezone.localtime(self.end_time).hour} - {self.style}'