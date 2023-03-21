from django.db import models

from apps.customer.models import ModelsCustomer
from apps.account.models import ModelsAccount
from apps.users.models import ModelsUser


class ModelsCars(models.Model):
    customer = models.ForeignKey(ModelsCustomer, on_delete=models.CASCADE)
    account = models.ForeignKey(ModelsAccount, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(ModelsUser, on_delete=models.CASCADE)
    description = models.TextField()
    stock = models.CharField(max_length=55)
    vin = models.CharField(max_length=55)
    model = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True, upload_to='car')
    create_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = "Car"


