from django.contrib import admin
from . import models


@admin.register(models.ModelsCars)
class ModelsCarsAdmin(admin.ModelAdmin):
    list_display = ('stock', 'po', 'vin', 'model', 'make')

# admin.site.register(models.ModelsCars)