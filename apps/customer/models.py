from django.db import models

from apps.account.models import ModelsAccount
from apps.users.models import ModelsUser


class ModelsCustomer(models.Model):
    user = models.ForeignKey(ModelsUser, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(ModelsAccount, on_delete=models.CASCADE, null=True, blank=True)
    email = models.CharField(max_length=122)
    full_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=122, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
