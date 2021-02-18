from django.db import models
from django.utils import timezone

class ProductionOrder(models.Model):
    buyer = models.CharField(max_length=256)
    quantity = models.IntegerField()
    receive_date_time = models.DateTimeField(default=timezone.now)
    due_date_time = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.buyer} - {self.quantity}'
    
    @staticmethod
    def active():
        return ProductionOrder.objects.filter(completed=False)


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


class Defect(models.Model):
    operation = models.CharField(max_length=256)
    defect = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.operation} - {self.defect}'
    
    class Meta:
        ordering = ["operation"]

QC_INPUT_TYPES = ['ftt', 'rejected', 'rectified', 'defective']

class QcInput(models.Model):
    datetime = models.DateTimeField()
    ftt = models.BooleanField(default=True)
    input_type = models.CharField(max_length=56)
    size = models.CharField(max_length=16)
    quantity = models.IntegerField()
    redacted = models.BooleanField(default=False)
    redaction_datetime = models.DateTimeField(null=True)
    defects = models.ManyToManyField(Defect)
    production_session = models.ForeignKey(ProductionSession, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.size} - {self.quantity} - {self.production_session.style}'
