from django.contrib import admin
from . import models


@admin.register(models.ModelsCustomer)
class ModelsCustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'postal_code', 'email', 'phone', 'phone2')

# admin.site.register(models.ModelsCustomer)