from django.db import models
from django.utils import timezone
from .style import Style
from .line import Line
from django.conf import settings


class ProductionSession(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.DO_NOTHING, blank=True)
    operators = models.IntegerField()
    helpers = models.IntegerField()
    assigned_qc = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    target = models.IntegerField()

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