from django.db import models
from .prod_order import ProductionOrder


class Style(models.Model):
    number = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    color = models.CharField(max_length=256)
    sizes = models.JSONField()
    name = models.CharField(max_length=256)
    sam = models.FloatField()
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.number}'