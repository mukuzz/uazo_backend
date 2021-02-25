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
    def get_active():
        return ProductionOrder.objects.filter(completed=False)