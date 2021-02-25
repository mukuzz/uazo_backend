from django.db import models
from django.utils import timezone


class Defect(models.Model):
    operation = models.CharField(max_length=256)
    defect = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.operation} - {self.defect}'
    
    class Meta:
        ordering = ["operation"]