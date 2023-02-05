from django.contrib import admin

from . import models


@admin.register(models.ModelsInvoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'crew_id', 'car_id', 'customer_id', 'status', 'total_sum', 'start_at', 'finished_at')
