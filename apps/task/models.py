from django.db import models

from apps.cars.models import ModelsCars


class ModelsTask(models.Model):
    car_id = models.ForeignKey(ModelsCars, on_delete=models.CASCADE)
    work = models.CharField(max_length=255, null=False)
    payment = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car_id}, {self.work}"
