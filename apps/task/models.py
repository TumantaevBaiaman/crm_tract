from django.db import models

from apps.invoice.models import ModelsInvoice


class ModelsTask(models.Model):
    invoice_id = models.ForeignKey(ModelsInvoice, on_delete=models.CASCADE)
    work = models.CharField(max_length=255, null=False)
    payment = models.CharField(max_length=255, null=False)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_id}, {self.work}"
