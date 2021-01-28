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

    @property
    def is_active(self):
        return datetime.datetime.now > self.start_time and \
                datetime.datetime.now < self.end_time

    def __str__(self):
        return f'{self.start_time} - {self.end_time} - {self.style}'


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
    input_type = models.CharField(max_length=56)
    size = models.CharField(max_length=16)
    quantity = models.IntegerField()
    redacted = models.BooleanField(default=False)
    redaction_datetime = models.DateTimeField(null=True)
    defects = models.ManyToManyField(Defect)
    production_session = models.ForeignKey(ProductionSession, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.size} - {self.quantity} - {self.production_session.style}'
