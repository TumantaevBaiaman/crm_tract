from django.db import models

from apps.users.models import ModelsUser


class ModelsCars(models.Model):
    customer = models.ForeignKey(ModelsUser, on_delete=models.CASCADE)
    description = models.TextField()
    vin = models.CharField(max_length=55)
    model = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vin

    class Meta:
        verbose_name = "Car"


