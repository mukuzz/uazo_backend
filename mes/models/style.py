from django.db import models
from django.core.validators import MinValueValidator


class StyleCategory(models.Model):
    category = models.CharField(max_length=256)
    defects = models.ManyToManyField('mes.Defect', blank=True)
    class Meta: 
        verbose_name = "Style Category"
        verbose_name_plural = "Style Categories"

    def __str__(self):
        return self.category


class Style(models.Model):
    number = models.CharField(max_length=256)
    category = models.ForeignKey(StyleCategory, on_delete=models.PROTECT)
    color = models.CharField(max_length=256)
    name = models.CharField(max_length=256, blank=True)
    sam = models.FloatField(validators=[MinValueValidator(0.001, message="sam should be greater than 0")])
    defects = models.ManyToManyField('mes.Defect')
    order = models.ForeignKey('mes.ProductionOrder', on_delete=models.PROTECT)

    def __str__(self):
        return self.number
    
    def quantity(self):
        quantity = 0
        for sizequantity in self.sizequantity_set.all():
            quantity += sizequantity.quantity
        return quantity


class SizeQuantity(models.Model):
    size = models.CharField(max_length=256)
    quantity = models.PositiveIntegerField()
    style = models.ForeignKey(Style, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.size} - {self.quantity}'