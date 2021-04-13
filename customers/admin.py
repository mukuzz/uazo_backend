# from django.contrib import admin
# from django_tenants.admin import TenantAdminMixin

# from customers.models import Factory, Domain

# @admin.register(Factory)
# class FactoryAdmin(TenantAdminMixin, admin.ModelAdmin):
#     list_display = ('name', 'paid_until', 'created_on', 'on_trial')


# @admin.register(Domain)
# class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
#     list_display = ('domain', 'tenant')