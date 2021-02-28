from django.db import models

class Buyer(models.Model):
    buyer = models.CharField(max_length=256)

    def __str__(self):
        return self.buyer