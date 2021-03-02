from django.db import models
from django.utils import timezone


class Defect(models.Model):
    operation = models.CharField(max_length=256, blank=True, null=True)
    defect = models.CharField(max_length=256)

    def __str__(self):
        if self.operation == '':
            return self.defect
        return f'{self.operation} - {self.defect}'