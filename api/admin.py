from django.contrib import admin
from .models import ProductionOrder, Style, ProductionSession, QcInput, Defect

admin.site.register(ProductionOrder)
admin.site.register(Style)
admin.site.register(ProductionSession)
admin.site.register(QcInput)
admin.site.register(Defect)