from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator


class ProductionOrder(models.Model):
    buyer = models.ForeignKey('mes.Buyer', on_delete=models.PROTECT)
    order_number = models.CharField(max_length=256, default=timezone.now)
    quantity = models.PositiveIntegerField()
    receive_date_time = models.DateTimeField(default=timezone.now)
    due_date_time = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.buyer} - {self.quantity()}'
    
    @staticmethod
    def get_active():
        return ProductionOrder.objects.filter(completed=False)
    
    def quantity(self):
        quantity = 0
        for style in self.style_set.all():
            for sizequantity in style.sizequantity_set.all():
                quantity += sizequantity.quantity
        return quantity
    
    def progress(self):
        """
        Returns the quantity of units produced for the production order
        """
        from .qc_input import QcInput
        
        qc_inputs = QcInput.objects\
            .filter(production_session__style__order=order)\
            .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
        produced = 0
        for qc_input in qc_inputs:
            produced += qc_input.quantity
        return produced