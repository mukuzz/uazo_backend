from django.contrib import admin
import nested_admin
from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect, SizeQuantity, Line

admin.site.site_header = "Uazo"
admin.site.site_title = "Uazo"
admin.site.index_title = "Uazo Admin"
admin.site.site_url = "/dashboard"

class SizeQuantityInline(admin.StackedInline):
    model = SizeQuantity
    extra = 0
    verbose_name = "Size Quantity"
    verbose_name_plural = "Size Quantities"

class StyleInline(admin.StackedInline):
    model = Style
    extra = 0

class StyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'category', 'color', 'order']
    inlines = [SizeQuantityInline]
    filter_horizontal = ['defects']
    fields = ('order', 'name', 'number', 'category', 'color', 'sam', 'defects')
    list_filter = ['order', 'name', 'number', 'category']
    search_fields = ['name', 'number', 'category', 'color']
    autocomplete_fields = ['order', 'defects']
    save_as = True
    save_as_continue = False

admin.site.register(Style, StyleAdmin)

class SizeQuantityNestedInline(nested_admin.NestedTabularInline):
    model = SizeQuantity
    extra = 1
    verbose_name = "Size Quantity"
    verbose_name_plural = "Size Quantities"

class StyleNestedInline(nested_admin.NestedStackedInline):
    model = Style
    extra = 0
    inlines = [SizeQuantityNestedInline]
    autocomplete_fields = ['defects']


class ProductionOrderAdmin(nested_admin.NestedModelAdmin):
    inlines = [StyleNestedInline]
    date_hierarchy = 'due_date_time'
    list_display = ['buyer', 'quantity', 'receive_date_time', 'due_date_time', 'completed']
    list_filter = ['buyer', 'receive_date_time', 'due_date_time', 'completed']
    search_fields = ['buyer']
    save_as = True
    save_as_continue = False

admin.site.register(ProductionOrder, ProductionOrderAdmin)


class ProductionSessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ['start_time', 'end_time', 'style', 'line', 'target']
    list_filter = ['start_time', 'end_time', 'style', 'line']
    save_as = True
    save_as_continue = False

admin.site.register(ProductionSession, ProductionSessionAdmin)


class QcInputAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ['input_type', 'size', 'quantity', 'production_session']
    list_filter = ['input_type', 'production_session']

admin.site.register(QcInput, QcInputAdmin)


class DeletedQcInputAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ['input_type', 'size', 'quantity', 'production_session']
    list_filter = ['input_type', 'production_session']

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(DeletedQcInput, DeletedQcInputAdmin)


class DefectAdmin(admin.ModelAdmin):
    list_display = ['defect', 'operation']
    save_as = True
    save_as_continue = False
    search_fields = ['defect', 'operation']
    list_filter = ['defect', 'operation']

admin.site.register(Defect, DefectAdmin)


class LineAdmin(admin.ModelAdmin):
    list_display = ['number', 'location']
    save_as = True
    save_as_continue = False
    list_filter = ['location']

admin.site.register(Line, LineAdmin)