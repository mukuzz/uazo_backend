from django.db import models
from .prod_order import ProductionOrder
from .defect import Defect


class Style(models.Model):
    number = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    color = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    sam = models.FloatField()
    defects = models.ManyToManyField(Defect)
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.number}'


class SizeQuantity(models.Model):
    size = models.CharField(max_length=256)
    quantity = models.IntegerField()
    style = models.ForeignKey(Style, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.size} - {self.quantity}'