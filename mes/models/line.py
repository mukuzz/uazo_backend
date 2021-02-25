from django.db import models

class Line(models.Model):
    number = models.CharField(max_length=256)
    location = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.number}'

