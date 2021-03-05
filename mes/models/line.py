from django.db import models

class LineLocation(models.Model):
    location = models.CharField(max_length=256)

    def __str__(self):
        return self.location

class Line(models.Model):
    number = models.PositiveIntegerField()
    location = models.ForeignKey(LineLocation, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.number} - {self.location}'

