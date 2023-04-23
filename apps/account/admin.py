from django.contrib import admin
from . import models


@admin.register(models.ModelsAccount)
class ModelsAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'hst', 'status', 'last_invoice_month')


@admin.register(models.ModelsSatusAccount)
class ModelsStatusAccountAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'paid')

# admin.site.register(models.ModelsAccount)
# admin.site.register(models.ModelsSatusAccount)
