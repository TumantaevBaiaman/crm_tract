from django.db import models

from apps.cars.models import ModelsCars
from apps.users.models import ModelsUser


class ModelsInvoice(models.Model):
    crew_id = models.ForeignKey(ModelsUser, on_delete=models.CASCADE)
    car_id = models.ForeignKey(ModelsCars, on_delete=models.CASCADE)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    finish = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crew_id}, {self.car_id}"

