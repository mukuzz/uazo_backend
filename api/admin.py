from django.contrib import admin
from api.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect

admin.site.register(ProductionOrder)
admin.site.register(Style)
admin.site.register(ProductionSession)
admin.site.register(QcInput)
admin.site.register(DeletedQcInput)
admin.site.register(Defect)