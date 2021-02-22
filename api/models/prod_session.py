from django.db import models
from django.utils import timezone
from .style import Style


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    line_number = models.CharField(max_length=256)
    operators = models.IntegerField()
    helpers = models.IntegerField()
    date = models.DateField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    target = models.IntegerField()

    def __str__(self):
        return f'{timezone.localtime(self.start_time).hour} to {timezone.localtime(self.end_time).hour} - {self.style}'