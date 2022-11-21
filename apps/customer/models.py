from django.db import models

from apps.users.models import ModelsUser


class ModelsCustomer(models.Model):
    user = models.ForeignKey(ModelsUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=122, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
