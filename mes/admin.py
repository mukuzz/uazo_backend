from django.contrib import admin
import nested_admin
from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect, SizeQuantity, Line, LineLocation, Buyer, StyleCategory, QcAppState

import os
FACTORY_NAME = os.getenv('FACTORY_NAME', 'Uazo')

admin.site.site_header = FACTORY_NAME
admin.site.site_title = FACTORY_NAME
admin.site.index_title = "Uazo Admin"
admin.site.site_url = None

class SizeQuantityInline(admin.StackedInline):
    model = SizeQuantity
    extra = 0
    verbose_name = "Size Quantity"
    verbose_name_plural = "Size Quantities"

class StyleInline(admin.StackedInline):
    model = Style
    extra = 0

class StyleAdmin(admin.ModelAdmin):
    list_display = ['number', 'category', 'color', 'order']
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
    list_display = ['order_number', 'buyer', 'quantity', 'receive_date_time', 'due_date_time', 'completed']
    list_filter = ['buyer__buyer', 'receive_date_time', 'due_date_time', 'completed']
    search_fields = ['buyer__buyer']
    save_as = True
    save_as_continue = False

admin.site.register(ProductionOrder, ProductionOrderAdmin)


class StyleCategoryAdmin(admin.ModelAdmin):
    list_display = ['category']
    autocomplete_fields = ['defects']

admin.site.register(StyleCategory, StyleCategoryAdmin)


class ProductionSessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ['start_time', 'end_time', 'style', 'line', 'target']
    list_filter = ['start_time', 'end_time', 'style', 'line']
    save_as = True
    save_as_continue = False

admin.site.register(ProductionSession, ProductionSessionAdmin)


class QcAppStateAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ['datetime', 'production_session', 'signed_in_user']
    list_filter = ['production_session', 'signed_in_user']

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(QcAppState, QcAppStateAdmin)


class QcInputAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ['input_type', 'size', 'quantity', 'datetime', 'production_session']
    list_filter = ['input_type', 'production_session']
    ordering = ['-datetime']

admin.site.register(QcInput, QcInputAdmin)


class DeletedQcInputAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime'
    list_display = ['input_type', 'size', 'quantity', 'deletion_datetime', 'production_session']
    list_filter = ['input_type', 'production_session']
    ordering = ['-deletion_datetime']

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
    list_filter = ['location__location']

admin.site.register(Line, LineAdmin)


class BuyerAdmin(admin.ModelAdmin):
    list_display = ['buyer']

admin.site.register(Buyer, BuyerAdmin)


class LineLocationAdmin(admin.ModelAdmin):
    list_display = ['location']

admin.site.register(LineLocation, LineLocationAdmin)