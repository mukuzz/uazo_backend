from django.db import models
from django.utils import timezone
from .style import Style
from .line import Line
from django.conf import settings
from django.core.validators import MinValueValidator


def get_current_local_time():
    return timezone.localtime(timezone.now())

class ProductionSessionBreak(models.Model):
    start_time = models.TimeField(default=get_current_local_time) # TODO: make it timezone aware
    end_time = models.TimeField(default=get_current_local_time) # TODO: make it timezone aware

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['start_time', 'end_time'], name='unique_break_timing')
        ]
        
    def __str__(self):
        return f'{self.start_time.strftime("%I:%M %p")} - {self.end_time.strftime("%I:%M %p")}'


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.PROTECT)
    line = models.ForeignKey(Line, on_delete=models.PROTECT)
    operators = models.PositiveIntegerField()
    helpers = models.PositiveIntegerField()
    assigned_qc = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    breaks = models.ManyToManyField('mes.ProductionSessionBreak', blank=True)
    target = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.get_session_name()} - {self.style}'

    def get_session_name(self):
        local_start_time = timezone.localtime(self.start_time)
        local_end_time = timezone.localtime(self.end_time)
        if local_end_time - local_start_time > timezone.timedelta(days=1) \
            or local_end_time.hour < local_start_time.hour:
            return f'{local_start_time.strftime("%H:%M")} ({local_start_time.strftime("%d/%m/%Y")}) to {local_end_time.strftime("%H:%M")} ({local_end_time.strftime("%d/%m/%Y")})'
        else:
            return f'{local_start_time.strftime("%H:%M")} to {local_end_time.strftime("%H:%M")} ({local_start_time.strftime("%d/%m/%Y")})'
    
    @staticmethod
    def get_active():
        return ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )