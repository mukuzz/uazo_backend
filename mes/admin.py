from django.contrib import admin
import nested_admin
from django.forms import ModelForm, ValidationError
from mes.models import ProductionOrder, Style, ProductionSession, ProductionSessionBreak, QcInput, DeletedQcInput, Defect, SizeQuantity, Line, LineLocation, Buyer, StyleCategory, QcAppState, Operation, OperationDefect
from django.conf import settings
from django.utils import timezone

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
    fields = ('order', 'name', 'number', 'category', 'color', 'sam', 'defects', 'operations')
    list_filter = ['order', 'name', 'number', 'category']
    search_fields = ['name', 'number', 'category', 'color']
    autocomplete_fields = ['order', 'defects', 'operations']
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
    autocomplete_fields = ['defects', 'operations']


class ProductionOrderAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['receive_date_time'] >= cleaned_data['due_date_time']:
            validation_error = ValidationError('Due date time should be after receive date time')
            # add_error removes the field data from dict
            self.add_error('due_date_time', validation_error)
        return cleaned_data

class ProductionOrderAdmin(nested_admin.NestedModelAdmin):
    inlines = [StyleNestedInline]
    date_hierarchy = 'due_date_time'
    list_display = ['order_number', 'buyer', 'quantity', 'receive_date_time', 'due_date_time', 'completed']
    list_filter = ['buyer__buyer', 'receive_date_time', 'due_date_time', 'completed']
    search_fields = ['buyer__buyer']
    save_as = True
    save_as_continue = False
    form = ProductionOrderAdminForm

admin.site.register(ProductionOrder, ProductionOrderAdmin)


class StyleCategoryAdmin(admin.ModelAdmin):
    list_display = ['category']

admin.site.register(StyleCategory, StyleCategoryAdmin)

class ProductionSessionBreakAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['start_time'] >= cleaned_data['end_time']:
            validation_error = ValidationError('End time should be after start time')
            # add_error removes the field data from dict
            self.add_error('end_time', validation_error)
        return cleaned_data

class ProductionSessionBreakAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'end_time']
    search_fields = ['start_time', 'end_time']
    form = ProductionSessionBreakAdminForm

    def get_deleted_objects(self, objs, request):
        """
        Hook for customizing the delete process for the delete view and the
        "delete selected" action.
        """
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        for obj in to_delete:
            if type(obj) == list:
                protected += obj
        return to_delete, model_count, perms_needed, protected

admin.site.register(ProductionSessionBreak, ProductionSessionBreakAdmin)


class ProductionSessionAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data['start_time']
        end_time = cleaned_data['end_time']
        if start_time.date() != end_time.date():
            raise ValidationError('Production session cannot last more than one day')
        for prod_break in cleaned_data['breaks']:
            if prod_break.start_time < start_time.time() or prod_break.end_time > end_time.time():
                raise ValidationError('Break timings should be within production session timings.')
        if start_time >= end_time:
            validation_error = ValidationError('End time should be after start time')
            # add_error removes the field data from dict
            self.add_error('end_time', validation_error)
        return cleaned_data

class ProductionSessionAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ['start_time', 'end_time', 'style', 'line', 'target']
    list_filter = ['start_time', 'end_time', 'style', 'line']
    autocomplete_fields = ['breaks']
    save_as = True
    save_as_continue = False
    form = ProductionSessionAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_qc':
            from django.apps import apps
            User = apps.get_model(settings.AUTH_USER_MODEL)
            kwargs['queryset'] = User.objects.filter(groups__name='qc', is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        if obj:
            return timezone.localdate(timezone.now()) <= obj.end_time.date()
        else:
            return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        if obj:
            return timezone.localdate(timezone.now()) <= obj.end_time.date()
        else:
            return super().has_delete_permission(request, obj)

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
    # autocomplete_fields = ['operation_defects']

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
    list_display = ['defect']
    search_fields = ['defect']

    def get_deleted_objects(self, objs, request):
        """
        Hook for customizing the delete process for the delete view and the
        "delete selected" action.
        """
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        for obj in to_delete:
            if type(obj) == list:
                protected += obj
        return to_delete, model_count, perms_needed, protected

admin.site.register(Defect, DefectAdmin)

class OperationAdmin(admin.ModelAdmin):
    list_display = ['operation']
    search_fields = ['operation']

    def get_deleted_objects(self, objs, request):
        """
        Hook for customizing the delete process for the delete view and the
        "delete selected" action.
        """
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        for obj in to_delete:
            if type(obj) == list:
                protected += obj
        return to_delete, model_count, perms_needed, protected

admin.site.register(Operation, OperationAdmin)

class OperationDefectAdmin(admin.ModelAdmin):
    list_display = ['operation', 'defect']
    search_fields = ['operation', 'defect']
    list_filter = ['operation', 'defect']

admin.site.register(OperationDefect, OperationDefectAdmin)

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