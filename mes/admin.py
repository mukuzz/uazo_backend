from django.contrib import admin
from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect, SizeQuantity


class SizeQuantityInline(admin.StackedInline):
    model = SizeQuantity
    extra = 1


class StyleInline(admin.StackedInline):
    model = Style
    extra = 1

class StyleAdmin(admin.ModelAdmin):
    inlines = [SizeQuantityInline]

class ProductionOrderAdmin(admin.ModelAdmin):
    inlines = [StyleInline]


admin.site.site_header = "Uazo Admin"
admin.site.register(ProductionOrder, ProductionOrderAdmin)
admin.site.register(ProductionSession)
admin.site.register(QcInput)
admin.site.register(DeletedQcInput)
admin.site.register(Defect)