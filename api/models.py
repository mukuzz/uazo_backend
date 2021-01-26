from django.db import models
import datetime

class ProductionOrder(models.Model):
    buyer = models.CharField(max_length=256)
    quantity = models.IntegerField()
    receive_date_time = models.DateTimeField(default=datetime.datetime.now)
    due_date_time = models.DateTimeField()

    def __str__(self):
        return f'{self.buyer} - {self.quantity}'


class Style(models.Model):
    number = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    color = models.CharField(max_length=256)
    sizes = models.JSONField()
    name = models.CharField(max_length=256)
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.number}'


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    line_number = models.CharField(max_length=256)
    operators = models.IntegerField()
    helpers = models.IntegerField()
    date = models.DateField()
    start_time = models.DateTimeField(default=datetime.datetime.now)
    end_time = models.DateTimeField(default=datetime.datetime.now)
    target = models.IntegerField()

    def __str__(self):
        return f'{self.start_time} - {self.end_time} - {self.style}'


class QcInput(models.Model):
    datetime = models.DateTimeField()
    defect_type = models.CharField(max_length=256)
    size = models.CharField(max_length=16)
    quantity = models.IntegerField()
    production_sesion = models.ForeignKey(ProductionSession, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.size} - {self.quantity} - {self.production_sesion.style}'