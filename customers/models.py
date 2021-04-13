from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.conf import settings

# Create your models here.

class Factory(TenantMixin):
    name = models.CharField(max_length=256)
    paid_until = models.DateTimeField()
    on_trial = models.BooleanField()
    created_on = models.DateTimeField(auto_now_add=True)

    auto_create_schema = True

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Factory"
        verbose_name_plural = "Factories"


class Domain(DomainMixin):
    def __str__(self):
        return self.domain